"""
app.py - Streamlit UI for Ava: Customer Support Agent with Hindsight Memory.
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

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ava · AI Support Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Global CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], .stApp {
    background: #080c14 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #e2e8f0 !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header,
[data-testid="collapsedControl"],
[data-testid="stSidebarNav"] { display: none !important; }

/* Remove default padding */
[data-testid="stAppViewContainer"] > .main > .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Top Navigation Bar ── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 32px;
    height: 64px;
    background: rgba(10, 14, 26, 0.95);
    border-bottom: 1px solid rgba(255,255,255,0.07);
    backdrop-filter: blur(20px);
    position: sticky;
    top: 0;
    z-index: 100;
}
.topbar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
}
.topbar-logo {
    width: 36px; height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    box-shadow: 0 0 20px rgba(99,102,241,0.4);
}
.topbar-name {
    font-size: 1.1rem;
    font-weight: 700;
    background: linear-gradient(90deg, #c7d2fe, #a5b4fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.01em;
}
.topbar-tagline {
    font-size: 0.72rem;
    color: #64748b;
    font-weight: 400;
    display: block;
    letter-spacing: 0.02em;
}
.status-dot {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.78rem;
    color: #94a3b8;
    padding: 4px 12px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
}
.dot-green  { width: 7px; height: 7px; border-radius: 50%; background: #22c55e; box-shadow: 0 0 6px #22c55e; }
.dot-blue   { width: 7px; height: 7px; border-radius: 50%; background: #38bdf8; box-shadow: 0 0 6px #38bdf8; }

/* ── Customer card in left panel ── */
.customer-card {
    padding: 10px 12px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.03);
    margin-bottom: 8px;
    transition: all 0.2s ease;
}
.customer-card.active {
    border-color: rgba(99,102,241,0.6);
    background: rgba(99,102,241,0.12);
    box-shadow: 0 4px 15px rgba(99,102,241,0.15);
}
.customer-card-inner {
    display: flex;
    align-items: center;
    gap: 10px;
}
.customer-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.8rem;
    color: #ffffff;
    flex-shrink: 0;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
}
.customer-info {
    flex: 1;
    min-width: 0;
}
.customer-header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.customer-name {
    font-size: 0.84rem;
    font-weight: 600;
    color: #e2e8f0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.customer-role {
    font-size: 0.7rem;
    color: #64748b;
    margin-top: 1px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.customer-preview {
    font-size: 0.72rem;
    color: #94a3b8;
    margin-top: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: flex;
    align-items: center;
    gap: 4px;
}
.msg-badge {
    font-size: 0.65rem;
    padding: 1px 6px;
    border-radius: 10px;
    background: rgba(99,102,241,0.3);
    color: #a5b4fc;
    border: 1px solid rgba(99,102,241,0.5);
    font-weight: 600;
}

.info-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 10px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    font-size: 0.78rem;
    color: #94a3b8;
    margin-bottom: 6px;
}

/* ── Chat topbar ── */
.chat-topbar {
    padding: 14px 28px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(8, 12, 20, 0.9);
    backdrop-filter: blur(10px);
}
.chat-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #e2e8f0;
}
.chat-subtitle { font-size: 0.72rem; color: #475569; margin-top: 2px; }

/* ── Memory tag ── */
.mem-tag {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.7rem;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 6px;
    font-weight: 500;
}
.mem-tag-on  { background: rgba(99,102,241,0.15); color: #818cf8; border: 1px solid rgba(99,102,241,0.3); }
.mem-tag-off { background: rgba(239,68,68,0.12);  color: #f87171; border: 1px solid rgba(239,68,68,0.3); }

/* ── Panel section title ── */
.panel-section-title {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #475569;
    margin-bottom: 8px;
}

/* Empty state */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    color: #334155;
    text-align: center;
}
.empty-icon { font-size: 3rem; opacity: 0.4; }
.empty-title { font-size: 1.1rem; font-weight: 600; color: #475569; }
.empty-sub { font-size: 0.82rem; color: #334155; max-width: 340px; line-height: 1.6; }

/* Buttons styling */
.stButton > button {
    border-radius: 8px !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    color: white !important;
}
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #94a3b8 !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: rgba(99,102,241,0.5) !important;
    color: #e2e8f0 !important;
    background: rgba(99,102,241,0.1) !important;
}

/* Override chat input */
[data-testid="stChatInput"] > div {
    background: rgba(20, 26, 44, 0.9) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
}
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border-radius: 10px !important;
}
.stMarkdown, [data-testid="stMarkdownContainer"] {
    font-family: 'Inter', sans-serif !important;
}

/* Form input dark styling */
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] {
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    background: rgba(255,255,255,0.02) !important;
}
</style>
""", unsafe_allow_html=True)

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
mem_label = "Hindsight Cloud (Connected)" if is_cloud else "Hindsight Local"
mem_color = "dot-blue" if is_cloud else "dot-green"

st.markdown(f"""
<div class="topbar">
  <div class="topbar-brand">
    <div class="topbar-logo">🤖</div>
    <div>
      <span class="topbar-name">Ava — AI Support Agent</span>
      <span class="topbar-tagline">Powered by Hindsight long-term memory</span>
    </div>
  </div>
  <div style="display:flex;gap:10px;align-items:center;">
    <div class="status-dot"><span class="dot-green"></span> Groq LLM Online</div>
    <div class="status-dot"><span class="{mem_color}"></span> {mem_label}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Two-column layout ───────────────────────────────────────────────────────
left_col, chat_col = st.columns([1.2, 3.0], gap="medium")

# ════════════════════════════════════════════════════════════════════
# LEFT PANEL (Customer Inbox & Navigation)
# ════════════════════════════════════════════════════════════════════
with left_col:
    st.markdown('<div style="padding:16px 8px 0;">', unsafe_allow_html=True)

    # ── Add New User Expander ──
    with st.expander("➕ Add New User / Customer", expanded=False):
        with st.form("new_user_form", clear_on_submit=True):
            new_name = st.text_input("Customer Name", placeholder="e.g. Liam Davis")
            new_role = st.text_input("Role & Company", placeholder="e.g. Lead DevOps · CloudNova")
            new_notes = st.text_area("Initial Context / Notes (Optional)", placeholder="e.g. Prefers bullet points. Uses AWS & Docker.")
            submitted = st.form_submit_button("➕ Create Customer", use_container_width=True)
            if submitted:
                if not new_name.strip():
                    st.error("Please enter a customer name.")
                else:
                    clean_name = new_name.strip()
                    clean_role = new_role.strip() or "Customer"
                    # Generate clean slug ID
                    slug = re.sub(r'[^a-z0-9]+', '-', clean_name.lower()).strip('-')
                    if not slug:
                        slug = f"user-{int(time.time())}"
                    cid = slug
                    if cid in st.session_state.customers:
                        cid = f"{slug}-{int(time.time()) % 1000}"

                    st.session_state.customers[cid] = (clean_name, clean_role)
                    st.session_state.user_conversations[cid] = []

                    # Ensure bank exists in Hindsight Cloud
                    ensure_bank_exists(cid, clean_name)

                    # Store initial profile info in Hindsight memory
                    base_profile_memory = f"FACT: Customer Profile: {clean_name} ({clean_role})."
                    remember(cid, base_profile_memory)

                    # Store optional initial background notes in Hindsight memory
                    if new_notes.strip():
                        remember(cid, f"FACT: Background notes: {new_notes.strip()}")

                    # Switch active customer to the new user
                    st.session_state.customer_id = cid
                    st.session_state.latest_memories_used = []
                    st.toast(f"User {clean_name} added successfully!", icon="🎉")
                    st.rerun()

    st.markdown('<p class="panel-section-title" style="margin-top:12px;">Customer Inboxes</p>', unsafe_allow_html=True)

    # ── Customer Profiles List (WhatsApp-style) ──
    for cid, (name, role) in list(st.session_state.customers.items()):
        is_active = st.session_state.customer_id == cid
        active_cls = "active" if is_active else ""
        conv = st.session_state.user_conversations.get(cid, [])
        msg_count = len(conv)
        initials = get_initials(name)
        avatar_bg = get_avatar_gradient(name)

        # Snippet of last message
        last_msg_snippet = "No messages yet"
        if conv:
            last_item = conv[-1]
            prefix = "You: " if last_item["role"] == "user" else "Ava: "
            text = last_item["content"].replace("\n", " ").strip()
            if len(text) > 30:
                text = text[:30] + "…"
            last_msg_snippet = f"{prefix}{text}"

        badge_html = f'<span class="msg-badge">{msg_count} msgs</span>' if msg_count > 0 else ""

        card_html = (
            f'<div class="customer-card {active_cls}">'
            f'<div class="customer-card-inner">'
            f'<div class="customer-avatar" style="background: {avatar_bg};">{initials}</div>'
            f'<div class="customer-info">'
            f'<div class="customer-header-row">'
            f'<div class="customer-name">{"🟢 " if is_active else ""}{name}</div>'
            f'{badge_html}'
            f'</div>'
            f'<div class="customer-role">{role}</div>'
            f'<div class="customer-preview">{last_msg_snippet}</div>'
            f'</div>'
            f'</div>'
            f'</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)

        btn_label = f"💬 Active Chat ({msg_count})" if is_active else f"Switch to {name.split()[0]}"
        if st.button(btn_label, key=f"sw_{cid}",
                     use_container_width=True,
                     type="primary" if is_active else "secondary"):
            if cid != st.session_state.customer_id:
                # Switch user WITHOUT erasing chat history (WhatsApp style)
                st.session_state.customer_id = cid
                st.session_state.latest_memories_used = []
                st.rerun()

    st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:16px 0;'>", unsafe_allow_html=True)

    # ── Memory Settings ──
    st.markdown('<p class="panel-section-title">Memory Settings</p>', unsafe_allow_html=True)
    mem_toggle = st.toggle(
        "🧠 Hindsight Memory",
        value=st.session_state.memory_enabled,
        help="Turn OFF to see how a stateless chatbot responds without customer history.",
    )
    if mem_toggle != st.session_state.memory_enabled:
        st.session_state.memory_enabled = mem_toggle
        st.rerun()

    active_cid = st.session_state.customer_id
    active_user_tuple = st.session_state.customers.get(active_cid, (active_cid, "Customer"))
    cname = active_user_tuple[0]

    info_html = (
        f'<div class="info-pill"><span>🏦</span> Bank: {bank_for(active_cid)}</div>'
        f'<div class="info-pill"><span>👤</span> Active User: {cname}</div>'
    )
    st.markdown(info_html, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:16px 0;'>", unsafe_allow_html=True)

    # ── Quick Prompts (Customer-Aware) ──
    st.markdown('<p class="panel-section-title">Quick Demo Prompts</p>', unsafe_allow_html=True)
    if active_cid == "maya-chen-brightpath":
        quick_prompts = [
            ("🔁", "The webhook sync is failing again."),
            ("🎫", "Can you remind me how we solved #1042?"),
            ("💳", "We saw duplicate billing entries again today."),
        ]
    elif active_cid == "alex-rivera-fintech":
        quick_prompts = [
            ("⚡", "Our payment gateway connection pool is maxing out again."),
            ("🎫", "How did we resolve the idempotency collision in #1089?"),
            ("📊", "Can you summarize the PgBouncer transaction pooling fix?"),
        ]
    elif active_cid == "jordan-taylor-cloud":
        quick_prompts = [
            ("🔑", "The Okta SAML SSO redirect is looping again."),
            ("🎫", "What was the fix for ticket #994?"),
            ("📋", "Can you provide an executive summary for our status report?"),
        ]
    else:
        quick_prompts = [
            ("👋", f"Hi Ava, I'm {cname.split()[0]}. Can you review my account profile?"),
            ("🧠", "What do you recall about my setup and preferences?"),
            ("🛠️", "I need assistance troubleshooting an issue on our systems."),
        ]

    for icon, prompt in quick_prompts:
        if st.button(f"{icon}  {prompt}", key=f"qp_{active_cid}_{prompt[:16]}", use_container_width=True):
            st.session_state.demo_input = prompt
            st.rerun()

    st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:16px 0;'>", unsafe_allow_html=True)

    # ── Actions ──
    st.markdown('<p class="panel-section-title">Actions</p>', unsafe_allow_html=True)
    current_active_msgs = st.session_state.user_conversations.get(active_cid, [])

    if st.button("✅  Mark Resolved & Learn", type="primary", use_container_width=True):
        if current_active_msgs:
            with st.spinner("Extracting learnings…"):
                new_learnings = learn_from_resolution(
                    customer_id=active_cid,
                    conversation=current_active_msgs,
                )
                icon = "💡" if new_learnings else "✅"
                msg  = f"Retained {len(new_learnings)} durable learnings!" if new_learnings else "Learnings stored in Hindsight."
                st.toast(msg, icon=icon)
                time.sleep(0.4)
                st.rerun()
        else:
            st.warning("Start a conversation with this customer first.")

    if st.button(f"🔄  Clear {cname.split()[0]}'s Chat", use_container_width=True):
        st.session_state.user_conversations[active_cid] = []
        st.session_state.latest_memories_used = []
        st.toast(f"Cleared chat history for {cname}.", icon="🧹")
        st.rerun()

    if st.button("🌱  Re-seed Customer History", use_container_width=True):
        seed_customer_history(active_cid)
        st.success(f"History re-seeded for {cname}!")
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# CHAT PANEL
# ════════════════════════════════════════════════════════════════════
with chat_col:
    active_cid = st.session_state.customer_id
    active_user_tuple = st.session_state.customers.get(active_cid, (active_cid, "Customer"))
    cname, crole = active_user_tuple
    mem_state_txt = "🟢 Memory ON" if st.session_state.memory_enabled else "🔴 Memory OFF"

    # Get conversation for currently active customer
    current_msgs = st.session_state.user_conversations.setdefault(active_cid, [])
    st.session_state.messages = current_msgs

    # Chat header
    topbar_html = (
        f'<div class="chat-topbar">'
        f'<div>'
        f'<div class="chat-title">💬 Chat with {cname}</div>'
        f'<div class="chat-subtitle">{crole} · {mem_state_txt} · {len(current_msgs)} messages</div>'
        f'</div>'
        f'<div class="status-dot">'
        f'<span class="dot-green"></span>'
        f'Ava is online'
        f'</div>'
        f'</div>'
    )
    st.markdown(topbar_html, unsafe_allow_html=True)

    # ── Render Messages ──
    if not current_msgs:
        empty_html = (
            f'<div class="empty-state" style="padding: 80px 0;">'
            f'<div class="empty-icon">💬</div>'
            f'<div class="empty-title">Conversation with {cname}</div>'
            f'<div class="empty-sub">'
            f'Ask Ava anything on behalf of {cname}. With Hindsight memory ON, she will recall past tickets, '
            f'preferences, and fixes without asking twice.'
            f'</div>'
            f'</div>'
        )
        st.markdown(empty_html, unsafe_allow_html=True)
    else:
        for msg in current_msgs:
            with st.chat_message(
                msg["role"],
                avatar="🧑‍💻" if msg["role"] == "user" else "🤖"
            ):
                if msg["role"] == "assistant":
                    mems = msg.get("memories_used", [])
                    was_on = msg.get("memory_enabled", True)
                    if was_on and mems:
                        st.markdown(
                            f'<div class="mem-tag mem-tag-on">🧠 {len(mems)} memories recalled from Hindsight</div>',
                            unsafe_allow_html=True,
                        )
                    elif not was_on:
                        st.markdown(
                            '<div class="mem-tag mem-tag-off">⚠️ Memory OFF — no customer context</div>',
                            unsafe_allow_html=True,
                        )
                st.markdown(msg["content"])

    # ── Input ──
    user_input = st.chat_input(f"Message Ava as {cname}…")
    active_prompt = st.session_state.pop("demo_input", None) or user_input

    if active_prompt:
        # Add user message to active customer's persistent conversation
        current_msgs.append({"role": "user", "content": active_prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(active_prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Ava is thinking…"):
                response_data = reply(
                    customer_id=active_cid,
                    message=active_prompt,
                    memory_enabled=st.session_state.memory_enabled,
                    customer_name=cname,
                    customer_role=crole,
                )
                answer    = response_data["answer"]
                mems_used = response_data["memories_used"]
                st.session_state.latest_memories_used = mems_used

                if st.session_state.memory_enabled and mems_used:
                    st.markdown(
                        f'<div class="mem-tag mem-tag-on">🧠 {len(mems_used)} memories recalled from Hindsight</div>',
                        unsafe_allow_html=True,
                    )
                elif not st.session_state.memory_enabled:
                    st.markdown(
                        '<div class="mem-tag mem-tag-off">⚠️ Memory OFF — no customer context</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown(answer)

        # Add assistant message to active customer's persistent conversation
        current_msgs.append({
            "role": "assistant",
            "content": answer,
            "memories_used": mems_used,
            "memory_enabled": st.session_state.memory_enabled,
        })
        st.session_state.user_conversations[active_cid] = current_msgs
        st.session_state.messages = current_msgs
        st.rerun()
