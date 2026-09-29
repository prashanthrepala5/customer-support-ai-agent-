"""
app.py - Streamlit UI for Helixa: Customer Support Agent with Hindsight Memory.
Includes login-based per-customer memory isolation.
"""

import streamlit as st
import time
import re
import json
import os

from agent import reply, learn_from_resolution, PRIMARY_MODEL
from memory import (
    get_all_memories,
    bank_for,
    is_hindsight_cloud_configured,
    remember,
    ensure_bank_exists,
)
from seed_history import seed_customer_history
from ui.styles import (
    get_global_css,
    get_login_background_html,
    get_login_card_header_html,
    get_login_card_footer_html,
)

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Helixa · SupportAI Copilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global CSS ─────────────────────────────────────────────────────────────
st.markdown(get_global_css(), unsafe_allow_html=True)

# ─── Helper Functions ───────────────────────────────────────────────────────
def get_initials(name: str) -> str:
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    elif parts:
        return parts[0][:2].upper()
    return "U"

def get_avatar_gradient(name: str) -> str:
    gradients = [
        "linear-gradient(135deg, #6366f1, #8b5cf6)",
        "linear-gradient(135deg, #06b6d4, #3b82f6)",
        "linear-gradient(135deg, #10b981, #059669)",
        "linear-gradient(135deg, #f59e0b, #d97706)",
        "linear-gradient(135deg, #ec4899, #8b5cf6)",
    ]
    idx = sum(ord(c) for c in name) % len(gradients)
    return gradients[idx]

# ─── Session State ───────────────────────────────────────────────────────────
USERS_FILE = "users.json"

# DEMO ONLY - NOT FOR PRODUCTION
DEMO_CREDENTIALS = {
    "maya.chen": {"password": "demo123", "customer_id": "maya-chen-brightpath", "name": "Maya Chen", "role": "Ops Lead · Brightpath Fitness"},
    "alex.rivera": {"password": "demo123", "customer_id": "alex-rivera-fintech", "name": "Alex Rivera", "role": "VP Eng · FlowPay"}
}

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users_dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users_dict, f, indent=4)

def _init(key, val):
    if key not in st.session_state:
        st.session_state[key] = val

_init("logged_in_username", None)
_init("customer_id", None)
_init("user_conversations", {})
_init("latest_memories_used", [])
_init("memory_enabled", True)
_init("seeded_customers", set())
_init("demo_input", None)

_init("auth_mode", "login")

# Seed default customers' background history once
for cred in DEMO_CREDENTIALS.values():
    default_cid = cred["customer_id"]
    if default_cid not in st.session_state.seeded_customers:
        seed_customer_history(default_cid)
        st.session_state.seeded_customers.add(default_cid)

# ─── Login Screen ───────────────────────────────────────────────────────────
if not st.session_state.logged_in_username:
    # Sync auth_mode from query params if clicked
    if "auth_mode" in st.query_params:
        mode_param = st.query_params["auth_mode"]
        if mode_param in ("login", "signup"):
            st.session_state.auth_mode = mode_param

    # Render Constellations & Glowing Orbs Background
    st.markdown(get_login_background_html(), unsafe_allow_html=True)

    if st.session_state.auth_mode == "login":
        # ── Sign In Form ──
        with st.form("login_form", border=False):
            st.markdown(get_login_card_header_html(mode="login"), unsafe_allow_html=True)
            username_in = st.text_input("Username", placeholder="Username or email", label_visibility="collapsed")
            password_in = st.text_input("Password", type="password", placeholder="Password", label_visibility="collapsed")
            submitted = st.form_submit_button("Sign in  →", use_container_width=True)
            st.markdown(get_login_card_footer_html(mode="login"), unsafe_allow_html=True)

            if submitted:
                users_db = load_users()
                valid = False
                target_cid = None

                if username_in in DEMO_CREDENTIALS and DEMO_CREDENTIALS[username_in]["password"] == password_in:
                    valid = True
                    target_cid = DEMO_CREDENTIALS[username_in]["customer_id"]
                elif username_in in users_db and users_db.get(username_in, {}).get("password") == password_in:
                    valid = True
                    target_cid = users_db[username_in]["customer_id"]

                if valid:
                    st.session_state.logged_in_username = username_in
                    st.session_state.customer_id = target_cid
                    if target_cid not in st.session_state.user_conversations:
                        st.session_state.user_conversations[target_cid] = []
                    st.query_params.clear()
                    st.rerun()
                else:
                    st.markdown("<div class='login-error'>Invalid username or password</div>", unsafe_allow_html=True)

    else:
        # ── Sign Up Form ──
        with st.form("signup_form", border=False):
            st.markdown(get_login_card_header_html(mode="signup"), unsafe_allow_html=True)
            new_username = st.text_input("Username", placeholder="Choose a username", label_visibility="collapsed")
            new_password = st.text_input("Password", type="password", placeholder="Choose a password", label_visibility="collapsed")
            confirm_password = st.text_input("Confirm", type="password", placeholder="Confirm password", label_visibility="collapsed")
            signup_submitted = st.form_submit_button("Create Account  →", use_container_width=True)
            st.markdown(get_login_card_footer_html(mode="signup"), unsafe_allow_html=True)

            if signup_submitted:
                if not new_username.strip() or not new_password.strip():
                    st.markdown("<div class='login-error'>Username and password are required</div>", unsafe_allow_html=True)
                elif new_password != confirm_password:
                    st.markdown("<div class='login-error'>Passwords do not match</div>", unsafe_allow_html=True)
                else:
                    users_db = load_users()
                    if new_username in DEMO_CREDENTIALS or new_username in users_db:
                        st.markdown("<div class='login-error'>Username already exists</div>", unsafe_allow_html=True)
                    else:
                        clean_name = re.sub(r'[^a-z0-9]+', '-', new_username.lower()).strip('-')
                        if not clean_name: clean_name = f"user-{int(time.time())}"
                        new_cid = f"{clean_name}-{int(time.time()) % 1000}"

                        users_db[new_username] = {
                            "password": new_password,  # DEMO ONLY
                            "customer_id": new_cid,
                            "name": new_username.replace(".", " ").title(),
                            "role": "Customer"
                        }
                        save_users(users_db)

                        st.session_state.logged_in_username = new_username
                        st.session_state.customer_id = new_cid
                        st.session_state.user_conversations[new_cid] = []
                        st.session_state.auth_mode = "login"
                        st.query_params.clear()
                        st.rerun()

    st.stop()

# ─── App Content (User is logged in) ──────────────────────────────────────────

active_username = st.session_state.logged_in_username
active_cid = st.session_state.customer_id

if active_username in DEMO_CREDENTIALS:
    user_info = DEMO_CREDENTIALS[active_username]
else:
    users_db = load_users()
    user_info = users_db.get(active_username, {"name": active_username, "role": "Customer"})

cname = user_info["name"]
crole = user_info.get("role", "Customer")
initials = get_initials(cname)
avatar_bg = get_avatar_gradient(cname)

def logout():
    st.session_state.logged_in_username = None
    st.session_state.customer_id = None
    st.session_state.latest_memories_used = []
    st.session_state.demo_input = None
    # Fully clear user conversations to prevent leaks
    st.session_state.user_conversations = {} 
    
# ─── Top Navigation Bar ──────────────────────────────────────────────────────
is_cloud = is_hindsight_cloud_configured()
mem_label = "Hindsight Cloud" if is_cloud else "Hindsight Local"
mem_color = "blue" if is_cloud else "green"

st.markdown(f"""
<div class="topbar">
  <div class="topbar-brand">
    <div class="topbar-logo">❖</div>
    <div class="topbar-name">Helixa</div>
  </div>
  <div class="topbar-status" style="flex: 1; display: flex; justify-content: center;">
    <div class="status-badge"><div class="dot green"></div> Agent Status: ONLINE</div>
    <div class="status-badge"><div class="dot {mem_color}"></div> {mem_label}</div>
    <div class="status-badge">⏱️ Latency: 140ms</div>
  </div>
  <div style="display: flex; align-items: center; justify-content: flex-end; gap: 12px; min-width: 150px;">
    <div style="color: var(--text-primary); font-weight: 500;">{cname}</div>
    <div class="customer-avatar" style="background: {avatar_bg}; width: 36px; height: 36px; line-height: 36px; font-size: 1rem; border-radius: 50%; display: inline-block; text-align: center;">{initials}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Add logout button aligned right, just under topbar
col_blank, col_logout = st.columns([10, 1])
with col_logout:
    if st.button("Log Out", key="logout_btn", use_container_width=True):
        logout()
        st.rerun()

st.markdown("<hr style='margin-top: 0px; margin-bottom: 20px; border-color: var(--border-color);'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ════════════════════════════════════════════════════════════════════
nav_col, chat_col, memory_col = st.columns([1.2, 3.0, 2.0], gap="large")

with nav_col:
    with st.container():
        st.markdown("### ⚡ Quick Prompts")
        if active_cid == "maya-chen-brightpath":
            quick_prompts = [("🔁", "Webhook sync failing"), ("🎫", "Recall fix for #1042"), ("💳", "Duplicate billing entries")]
        elif active_cid == "alex-rivera-fintech":
            quick_prompts = [("⚡", "Connection pool maxing out"), ("🎫", "Idempotency collision #1089"), ("📊", "PgBouncer fix summary")]
        else:
            quick_prompts = [("👋", f"Review my profile"), ("🧠", "Recall my preferences"), ("🛠️", "I need troubleshooting")]

        for icon, prompt in quick_prompts:
            if st.button(f"{icon} {prompt}", key=f"qp_{active_cid}_{prompt[:10]}", use_container_width=True):
                st.session_state.demo_input = prompt
                st.rerun()

with memory_col:
    st.markdown('<div class="memory-panel">', unsafe_allow_html=True)
    st.markdown('<div class="memory-header">🧠 Hindsight Memory Control</div>', unsafe_allow_html=True)
    
    mem_toggle = st.toggle(
        "Enable Agent Memory",
        value=st.session_state.memory_enabled,
        help="Turn OFF to simulate a standard stateless chatbot."
    )
    if mem_toggle != st.session_state.memory_enabled:
        st.session_state.memory_enabled = mem_toggle
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Hindsight Memory Viewer ──
    st.markdown("### 🧠 Stored Memories")
    all_memories = get_all_memories(active_cid)
    
    if not all_memories:
        st.markdown("<div style='text-align:center; padding: 30px 10px; color: var(--text-secondary); background: rgba(255,255,255,0.02); border-radius: 8px; font-size: 0.9rem;'><em>(no prior history)</em></div>", unsafe_allow_html=True)
    else:
        html_content = '<div class="memory-scroll-container">\n'
        for mem in reversed(all_memories):  # Show newest first
            tag = "MEMORY"
            if mem.startswith("FACT:"): tag = "FACT"
            elif mem.startswith("TICKET:"): tag = "TICKET"
            elif mem.startswith("LEARNING:"): tag = "LEARNING"
            elif mem.startswith("SENTIMENT:"): tag = "SENTIMENT"
            
            clean_mem = mem.replace(f"{tag}:", "").strip() if ":" in mem else mem
            
            html_content += f'<div class="memory-card"><div class="memory-tag">{tag}</div><br/>{clean_mem}</div>\n'
            
        html_content += '</div>'
        st.markdown(html_content, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚙️ Session Actions")
    current_active_msgs = st.session_state.user_conversations.get(active_cid, [])

    if st.button("✅ Mark Resolved & Learn", type="primary", use_container_width=True):
        if current_active_msgs:
            with st.spinner("Extracting learnings…"):
                new_learnings = learn_from_resolution(active_cid, current_active_msgs)
                st.toast(f"Retained {len(new_learnings)} learnings!" if new_learnings else "Learnings stored.", icon="💡")
                time.sleep(0.4)
                st.rerun()
        else:
            st.warning("Start a conversation first.")

    if st.button("🔄 Clear Chat", use_container_width=True):
        st.session_state.user_conversations[active_cid] = []
        st.session_state.latest_memories_used = []
        st.rerun()

with chat_col:
    # ── Chat Area ──
    current_msgs = st.session_state.user_conversations.setdefault(active_cid, [])
    
    if not current_msgs:
        st.markdown(f"""
        <div style="text-align:center; padding: 100px 0; color: var(--text-secondary);">
            <div style="font-size: 3rem; margin-bottom: 10px;">💬</div>
            <h3>Conversation with {cname}</h3>
            <p>Start typing below. Hindsight Memory is {'ON 🧠' if st.session_state.memory_enabled else 'OFF ⚠️'}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in current_msgs:
            with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"):
                if msg["role"] == "assistant":
                    mems = msg.get("memories_used", [])
                    was_on = msg.get("memory_enabled", True)
                    if was_on and mems:
                        st.markdown(f'<div class="memory-recalled-indicator">🧠 {len(mems)} relevant memories recalled</div>', unsafe_allow_html=True)
                    elif not was_on:
                        st.markdown('<div class="memory-recalled-indicator" style="color: #F59E0B; background: rgba(245, 158, 11, 0.1);">⚠️ Memory OFF — Stateless Mode</div>', unsafe_allow_html=True)
                st.markdown(msg["content"])

    # ── Chat Input ──
    user_input = st.chat_input(f"Message Helixa as {cname}…")
    active_prompt = st.session_state.pop("demo_input", None) or user_input

    if active_prompt:
        current_msgs.append({"role": "user", "content": active_prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(active_prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Helixa is analyzing context..."):
                response_data = reply(
                    customer_id=active_cid,
                    message=active_prompt,
                    memory_enabled=st.session_state.memory_enabled,
                    customer_name=cname,
                    customer_role=crole,
                )
                answer = response_data["answer"]
                mems_used = response_data["memories_used"]
                st.session_state.latest_memories_used = mems_used

                if st.session_state.memory_enabled and mems_used:
                    st.markdown(f'<div class="memory-recalled-indicator">🧠 {len(mems_used)} relevant memories recalled</div>', unsafe_allow_html=True)
                elif not st.session_state.memory_enabled:
                    st.markdown('<div class="memory-recalled-indicator" style="color: #F59E0B; background: rgba(245, 158, 11, 0.1);">⚠️ Memory OFF — Stateless Mode</div>', unsafe_allow_html=True)
                
                st.markdown(answer)

        current_msgs.append({
            "role": "assistant",
            "content": answer,
            "memories_used": mems_used,
            "memory_enabled": st.session_state.memory_enabled,
        })
        st.session_state.user_conversations[active_cid] = current_msgs
        st.rerun()
