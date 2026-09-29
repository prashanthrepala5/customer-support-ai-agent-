"""
app.py - Streamlit UI for Helixa: Customer Support Agent with Hindsight Memory.
Includes multi-user persistent chat history (WhatsApp style) and dynamic customer creation.
"""

import streamlit as st
import time
import re

from agent import reply, learn_from_resolution, PRIMARY_MODEL
from memory import (
    get_all_memories,
    bank_for,
    is_hindsight_cloud_configured,
    remember,
    ensure_bank_exists,
)
from seed_history import seed_customer_history
from ui.styles import get_global_css

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Helixa · SupportAI Copilot Cluster",
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
DEFAULT_CUSTOMERS = {
    "maya-chen-brightpath": ("Maya Chen", "Ops Lead · Brightpath Fitness"),
    "alex-rivera-fintech":  ("Alex Rivera", "VP Eng · FlowPay"),
    "jordan-taylor-cloud":  ("Jordan Taylor", "Product Lead · NovaCloud"),
}

def _init(key, val):
    if key not in st.session_state:
        st.session_state[key] = val

_init("customers", dict(DEFAULT_CUSTOMERS))
_init("customer_id", "maya-chen-brightpath")
_init("user_conversations", {})
_init("latest_memories_used", [])
_init("memory_enabled", True)
_init("seeded_customers", set())
_init("demo_input", None)

# Initialize conversation arrays for default users if not present
for cid in st.session_state.customers:
    if cid not in st.session_state.user_conversations:
        st.session_state.user_conversations[cid] = []

# Seed default customers' background history once
for default_cid in DEFAULT_CUSTOMERS:
    if default_cid not in st.session_state.seeded_customers:
        seed_customer_history(default_cid)
        st.session_state.seeded_customers.add(default_cid)

# Backwards compatibility alias
st.session_state.messages = st.session_state.user_conversations.get(st.session_state.customer_id, [])

# ─── Top Navigation Bar ──────────────────────────────────────────────────────
is_cloud = is_hindsight_cloud_configured()
mem_label = "Hindsight Cloud" if is_cloud else "Hindsight Local"
mem_color = "blue" if is_cloud else "green"

st.markdown(f"""
<div class="topbar">
  <div class="topbar-brand">
    <div class="topbar-logo">⌬</div>
    <div class="topbar-name">SupportAI Helixa Copilot Cluster</div>
  </div>
  <div class="topbar-status">
    <div class="status-badge"><div class="dot green"></div> Agent Status: ONLINE</div>
    <div class="status-badge"><div class="dot {mem_color}"></div> {mem_label}</div>
    <div class="status-badge">⏱️ Latency: 140ms</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# MAIN CONTENT (Left Navigation, Chat, Memory Profile)
# ════════════════════════════════════════════════════════════════════
nav_col, chat_col, profile_col = st.columns([1.2, 2.5, 1.2], gap="large")

with nav_col:
    with st.container():
        st.markdown("### 🗂️ Active Customers")
        
        # ── Customer Profiles List ──
        for cid, (name, role) in list(st.session_state.customers.items()):
            is_active = st.session_state.customer_id == cid
            active_cls = "active" if is_active else ""
            initials = get_initials(name)
            avatar_bg = get_avatar_gradient(name)

            card_html = (
                f'<div class="customer-card {active_cls}">'
                f'<div style="display:flex; gap:10px; align-items:center;">'
                f'<div class="customer-avatar" style="background: {avatar_bg};">{initials}</div>'
                f'<div>'
                f'<div class="customer-name">{name}</div>'
                f'<div class="customer-role">{role}</div>'
                f'</div></div></div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

            if st.button(f"Select {name.split()[0]}", key=f"sw_{cid}", use_container_width=True, type="primary" if is_active else "secondary"):
                if cid != st.session_state.customer_id:
                    st.session_state.customer_id = cid
                    st.session_state.latest_memories_used = []
                    st.rerun()
        
        st.markdown("---")
        
        # ── Add New User Expander ──
        with st.expander("➕ Add New Customer", expanded=False):
            with st.form("new_user_form", clear_on_submit=True):
                new_name = st.text_input("Customer Name", placeholder="e.g. Liam Davis")
                new_role = st.text_input("Role & Company", placeholder="e.g. Lead DevOps")
                new_notes = st.text_area("Initial Context", placeholder="e.g. Prefers bullet points.")
                if st.form_submit_button("➕ Create", use_container_width=True):
                    if not new_name.strip():
                        st.error("Please enter a customer name.")
                    else:
                        clean_name = new_name.strip()
                        clean_role = new_role.strip() or "Customer"
                        slug = re.sub(r'[^a-z0-9]+', '-', clean_name.lower()).strip('-')
                        if not slug: slug = f"user-{int(time.time())}"
                        cid = slug
                        if cid in st.session_state.customers:
                            cid = f"{slug}-{int(time.time()) % 1000}"

                        st.session_state.customers[cid] = (clean_name, clean_role)
                        st.session_state.user_conversations[cid] = []
                        ensure_bank_exists(cid, clean_name)
                        remember(cid, f"FACT: Customer Profile: {clean_name} ({clean_role}).")
                        if new_notes.strip():
                            remember(cid, f"FACT: Background notes: {new_notes.strip()}")

                        st.session_state.customer_id = cid
                        st.session_state.latest_memories_used = []
                        st.toast(f"Added {clean_name}!", icon="🎉")
                        st.rerun()

        st.markdown("---")
        
        # ── Quick Prompts ──
        active_cid = st.session_state.customer_id
        active_user_tuple = st.session_state.customers.get(active_cid, (active_cid, "Customer"))
        cname = active_user_tuple[0]
        crole = active_user_tuple[1]

        st.markdown("### ⚡ Quick Prompts")
        if active_cid == "maya-chen-brightpath":
            quick_prompts = [("🔁", "Webhook sync failing"), ("🎫", "Recall fix for #1042"), ("💳", "Duplicate billing entries")]
        elif active_cid == "alex-rivera-fintech":
            quick_prompts = [("⚡", "Connection pool maxing out"), ("🎫", "Idempotency collision #1089"), ("📊", "PgBouncer fix summary")]
        elif active_cid == "jordan-taylor-cloud":
            quick_prompts = [("🔑", "Okta SAML SSO looping"), ("🎫", "Fix for ticket #994"), ("📋", "Executive summary")]
        else:
            quick_prompts = [("👋", f"Review my profile"), ("🧠", "Recall my preferences"), ("🛠️", "I need troubleshooting")]

        for icon, prompt in quick_prompts:
            if st.button(f"{icon} {prompt}", key=f"qp_{active_cid}_{prompt[:10]}", use_container_width=True):
                st.session_state.demo_input = prompt
                st.rerun()

with profile_col:
    # ── Customer Profile & Controls ──
    st.markdown(f"### 👤 {cname}")
    st.caption(active_user_tuple[1])
    
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
        st.info("No memories stored yet.")
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
