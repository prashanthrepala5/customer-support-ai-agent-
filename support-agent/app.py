"""
app.py - Streamlit UI for Ava: Customer Support Agent with Hindsight Memory.

Features:
- Live Chat interface with Ava
- Interactive Memory Panel showcasing Hindsight memory recall in real time
- Memory ON / OFF comparison toggle
- 'What Ava Knows' tab grouping facts, tickets, learnings, and sentiment
- 'Mark Resolved & Learn' button triggering autonomous learning extraction
- Quick-demo chips for instant judge evaluation
"""

import streamlit as st
import time
from typing import List, Dict, Any

from agent import reply, learn_from_resolution, PRIMARY_MODEL
from memory import (
    get_all_memories,
    bank_for,
    is_hindsight_cloud_configured,
    remember,
)
from seed_history import seed_customer_history

# Page configuration
st.set_page_config(
    page_title="Ava | Customer Support Agent with Hindsight",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern, premium appearance
st.markdown("""
<style>
    /* Main container and font styles */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Header card */
    .header-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    .header-title {
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .header-tagline {
        font-size: 0.95rem;
        color: #94a3b8;
        margin: 4px 0 0 0;
    }
    
    /* Memory pill badges */
    .mem-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-right: 6px;
    }
    .badge-fact { background-color: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
    .badge-ticket { background-color: rgba(251, 146, 60, 0.15); color: #fb923c; border: 1px solid rgba(251, 146, 60, 0.3); }
    .badge-learning { background-color: rgba(74, 222, 128, 0.15); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.3); }
    .badge-sentiment { background-color: rgba(192, 132, 252, 0.15); color: #c084fc; border: 1px solid rgba(192, 132, 252, 0.3); }
    .badge-generic { background-color: rgba(148, 163, 184, 0.15); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.3); }

    /* Memory cards in right panel */
    .memory-card {
        background: rgba(30, 41, 59, 0.65);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 10px;
        font-size: 0.88rem;
        line-height: 1.45;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .memory-card:hover {
        border-color: rgba(56, 189, 248, 0.4);
        background: rgba(30, 41, 59, 0.85);
    }
    .memory-card-highlight {
        border-left: 4px solid #38bdf8;
        background: rgba(14, 165, 233, 0.08);
    }
    .memory-card-learning {
        border-left: 4px solid #4ade80;
        background: rgba(34, 197, 94, 0.08);
    }

    /* Badge on chat response */
    .recalled-chip {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.76rem;
        margin-bottom: 8px;
        font-weight: 500;
    }
    .recalled-chip-on {
        background-color: rgba(14, 165, 233, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    .recalled-chip-off {
        background-color: rgba(244, 63, 94, 0.15);
        color: #fb7185;
        border: 1px solid rgba(244, 63, 94, 0.3);
    }

    /* Sidebar info boxes */
    .status-card {
        background: rgba(15, 23, 42, 0.6);
        border-radius: 8px;
        padding: 10px 12px;
        border: 1px solid rgba(148, 163, 184, 0.2);
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------
DEMO_CUSTOMERS = {
    "maya-chen-brightpath": "Maya Chen (Ops Lead @ Brightpath Fitness)",
    "alex-rivera-fintech": "Alex Rivera (VP Eng @ FlowPay)",
    "new-customer-trial": "Fresh Customer (No Past History)",
}

if "customer_id" not in st.session_state:
    st.session_state.customer_id = "maya-chen-brightpath"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "latest_memories_used" not in st.session_state:
    st.session_state.latest_memories_used = []

if "memory_enabled" not in st.session_state:
    st.session_state.memory_enabled = True

if "seeded_customers" not in st.session_state:
    st.session_state.seeded_customers = set()

# Pre-seed default customer history once on load
if "maya-chen-brightpath" not in st.session_state.seeded_customers:
    seed_customer_history("maya-chen-brightpath")
    st.session_state.seeded_customers.add("maya-chen-brightpath")


# ---------------------------------------------------------------------------
# Sidebar: Setup Status, Quick Demo & Controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🤖 Ava Support Agent")
    st.markdown(
        "**Long-term Agent Memory Powered by Hindsight**\n\n"
        "Ava never makes a customer repeat their story. She remembers past tickets, "
        "root fixes, and behavioral nuances."
    )
    
    st.divider()
    
    st.markdown("#### ⚡ System Status")
    
    # Groq Status
    st.markdown(
        """
        <div class="status-card">
            <span style="color:#4ade80;">●</span> <b>LLM:</b> Groq Cloud<br>
            <small style="color:#94a3b8;">Model: <code>openai/gpt-oss-120b</code></small>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Hindsight Status
    is_cloud = is_hindsight_cloud_configured()
    cloud_label = "Hindsight Cloud (Connected)" if is_cloud else "Hindsight Engine (Ready / Local Sync)"
    cloud_color = "#38bdf8" if is_cloud else "#4ade80"
    st.markdown(
        f"""
        <div class="status-card">
            <span style="color:{cloud_color};">●</span> <b>Memory:</b> {cloud_label}<br>
            <small style="color:#94a3b8;">Bank: <code>{bank_for(st.session_state.customer_id)}</code></small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown("#### 🎬 60-Second Demo Script")
    st.markdown("""
    1. **Memory ON**: Send *"The webhook sync is failing again."*
       - Ava cites **Ticket #1042**, gives short numbered steps, zero generic questions.
    2. **Toggle Memory OFF**: Send the exact same message.
       - Ava asks generic questions *"What is your payment provider and stack?"*
    3. Click **"Mark Resolved & Learn"**:
       - Ava extracts durable learnings into Hindsight for future encounters.
    """)

    st.divider()
    if st.button("🌱 Re-seed Demo History", use_container_width=True):
        seed_customer_history(st.session_state.customer_id)
        st.success("Re-seeded ~3 weeks of tickets & preferences!")
        st.rerun()


# ---------------------------------------------------------------------------
# Header & Control Bar
# ---------------------------------------------------------------------------
st.markdown("""
<div class="header-card">
    <h1 class="header-title">Ava — AI Support Agent with Hindsight Memory</h1>
    <p class="header-tagline">"A support agent that never makes a customer repeat their story — it remembers every ticket, every fix that worked, and every frustration."</p>
</div>
""", unsafe_allow_html=True)

# Top Bar Controls
ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([1.8, 1.2, 1.4, 1.0])

with ctrl_col1:
    selected_cust = st.selectbox(
        "Active Customer Profile:",
        options=list(DEMO_CUSTOMERS.keys()),
        format_func=lambda x: DEMO_CUSTOMERS[x],
        index=list(DEMO_CUSTOMERS.keys()).index(st.session_state.customer_id),
    )
    if selected_cust != st.session_state.customer_id:
        st.session_state.customer_id = selected_cust
        st.session_state.messages = []
        st.session_state.latest_memories_used = []
        if selected_cust == "maya-chen-brightpath":
            seed_customer_history("maya-chen-brightpath")
        st.rerun()

with ctrl_col2:
    # Prominent Memory Toggle
    mem_toggle = st.toggle(
        "🧠 Hindsight Memory",
        value=st.session_state.memory_enabled,
        help="Turn OFF to see how a stateless chatbot fails. Turn ON to see Hindsight recall context.",
    )
    if mem_toggle != st.session_state.memory_enabled:
        st.session_state.memory_enabled = mem_toggle
        st.rerun()

with ctrl_col3:
    st.write("")  # alignment spacer
    if st.button("✅ Mark Resolved & Learn", type="primary", use_container_width=True, help="Autonomous learning extractor extracts durable facts into Hindsight"):
        if st.session_state.messages:
            with st.spinner("Extracting durable learnings into Hindsight..."):
                new_learnings = learn_from_resolution(
                    customer_id=st.session_state.customer_id,
                    conversation=st.session_state.messages,
                )
                if new_learnings:
                    st.toast(f"Retained {len(new_learnings)} durable learnings!", icon="💡")
                else:
                    st.toast("Learnings extracted & recorded in Hindsight bank.", icon="✅")
                time.sleep(0.5)
                st.rerun()
        else:
            st.warning("Start a conversation first before marking resolved.")

with ctrl_col4:
    st.write("")  # alignment spacer
    if st.button("🔄 Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.latest_memories_used = []
        st.rerun()


# Demo Quick-Prompt Buttons
st.markdown("<small style='color:#94a3b8;'>One-click demo triggers:</small>", unsafe_allow_html=True)
qp_col1, qp_col2, qp_col3 = st.columns([1.5, 1.5, 2.0])

demo_input = None
with qp_col1:
    if st.button("👉 'The webhook sync is failing again.'", use_container_width=True):
        demo_input = "The webhook sync is failing again."

with qp_col2:
    if st.button("👉 'Can you remind me how we solved #1042?'", use_container_width=True):
        demo_input = "Can you remind me how we solved #1042?"

with qp_col3:
    if st.button("👉 'We saw duplicate billing entries again today.'", use_container_width=True):
        demo_input = "We saw duplicate billing entries again today."


# ---------------------------------------------------------------------------
# Main Layout: Left (Chat) & Right (Memory Panel)
# ---------------------------------------------------------------------------
chat_col, memory_col = st.columns([1.2, 1.0], gap="large")


# ---------------------------------------------------------------------------
# LEFT COLUMN: Live Chat with Ava
# ---------------------------------------------------------------------------
with chat_col:
    st.markdown("### 💬 Conversation with Ava")

    # Render previous conversation history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"):
            if msg["role"] == "assistant":
                mems = msg.get("memories_used", [])
                was_enabled = msg.get("memory_enabled", True)
                if was_enabled and mems:
                    st.markdown(
                        f"""<div class="recalled-chip recalled-chip-on">
                            🧠 <b>{len(mems)} memories recalled</b> from Hindsight bank
                        </div>""",
                        unsafe_allow_html=True,
                    )
                elif not was_enabled:
                    st.markdown(
                        """<div class="recalled-chip recalled-chip-off">
                            ⚠️ <b>Memory OFF</b> — Zero customer context used
                        </div>""",
                        unsafe_allow_html=True,
                    )
            st.markdown(msg["content"])

    # Handle Input (either from quick buttons or standard chat input)
    user_input = st.chat_input("Type Maya's message (e.g., 'The webhook sync is failing again.')...")
    active_prompt = demo_input or user_input

    if active_prompt:
        # Display user message immediately
        st.session_state.messages.append({"role": "user", "content": active_prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(active_prompt)

        # Agent inference loop
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Ava is recalling customer history & generating response..."):
                response_data = reply(
                    customer_id=st.session_state.customer_id,
                    message=active_prompt,
                    memory_enabled=st.session_state.memory_enabled,
                )
                answer = response_data["answer"]
                mems_used = response_data["memories_used"]
                st.session_state.latest_memories_used = mems_used

                # Recalled badge
                if st.session_state.memory_enabled and mems_used:
                    st.markdown(
                        f"""<div class="recalled-chip recalled-chip-on">
                            🧠 <b>{len(mems_used)} memories recalled</b> from Hindsight bank
                        </div>""",
                        unsafe_allow_html=True,
                    )
                elif not st.session_state.memory_enabled:
                    st.markdown(
                        """<div class="recalled-chip recalled-chip-off">
                            ⚠️ <b>Memory OFF</b> — Zero customer context used
                        </div>""",
                        unsafe_allow_html=True,
                    )

                st.markdown(answer)

        # Append assistant message to state
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "memories_used": mems_used,
            "memory_enabled": st.session_state.memory_enabled,
        })
        st.rerun()


# ---------------------------------------------------------------------------
# RIGHT COLUMN: 🧠 Hindsight Memory Panel (The Star of the Show)
# ---------------------------------------------------------------------------
with memory_col:
    st.markdown("### 🧠 Hindsight Memory Panel")
    
    tab_recalled, tab_bank, tab_loop = st.tabs([
        "⚡ Recalled for Latest Reply",
        "📚 What Ava Knows About Customer",
        "🔄 Learning Loop (Hindsight)",
    ])

    # Tab 1: Exact memories recalled for latest message
    with tab_recalled:
        if not st.session_state.memory_enabled:
            st.warning("⚠️ **Hindsight Memory is currently TOGGLED OFF.**")
            st.info(
                "When memory is disabled, Ava acts like a stateless chatbot. "
                "She has no access to past tickets (#1042, #1057), stack specs, "
                "or Maya's preference for numbered steps."
            )
        elif st.session_state.latest_memories_used:
            st.success(f"🎯 **{len(st.session_state.latest_memories_used)} memories** surfaced by Hindsight multi-strategy retrieval:")
            for mem in st.session_state.latest_memories_used:
                tag = "GENERIC"
                css_class = "badge-generic"
                if mem.startswith("FACT:"):
                    tag = "FACT"
                    css_class = "badge-fact"
                elif mem.startswith("TICKET:"):
                    tag = "TICKET"
                    css_class = "badge-ticket"
                elif mem.startswith("LEARNING:"):
                    tag = "LEARNING"
                    css_class = "badge-learning"
                elif mem.startswith("SENTIMENT:"):
                    tag = "SENTIMENT"
                    css_class = "badge-sentiment"

                content = mem[len(tag) + 1:].strip() if mem.startswith(f"{tag}:") else mem
                st.markdown(
                    f"""
                    <div class="memory-card memory-card-highlight">
                        <span class="mem-badge {css_class}">{tag}</span>
                        {content}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info(
                "Send a message or click one of the quick-demo buttons to see "
                "Hindsight retrieve relevant memories in real time."
            )

    # Tab 2: Complete persistent knowledge in Customer's Hindsight bank
    with tab_bank:
        all_mems = get_all_memories(st.session_state.customer_id)
        if all_mems:
            facts = [m for m in all_mems if m.startswith("FACT:")]
            tickets = [m for m in all_mems if m.startswith("TICKET:")]
            learnings = [m for m in all_mems if m.startswith("LEARNING:")]
            sentiments = [m for m in all_mems if m.startswith("SENTIMENT:")]
            others = [m for m in all_mems if not any(m.startswith(p) for p in ("FACT:", "TICKET:", "LEARNING:", "SENTIMENT:"))]

            with st.expander(f"📋 System & Account Facts ({len(facts)})", expanded=True):
                for f in facts:
                    st.markdown(f"""<div class="memory-card"><span class="mem-badge badge-fact">FACT</span>{f[5:].strip()}</div>""", unsafe_allow_html=True)

            with st.expander(f"🎫 Past Tickets & Fixes ({len(tickets)})", expanded=True):
                for t in tickets:
                    st.markdown(f"""<div class="memory-card"><span class="mem-badge badge-ticket">TICKET</span>{t[7:].strip()}</div>""", unsafe_allow_html=True)

            with st.expander(f"💡 Durable Learnings & Preferences ({len(learnings)})", expanded=True):
                for l in learnings:
                    st.markdown(f"""<div class="memory-card memory-card-learning"><span class="mem-badge badge-learning">LEARNING</span>{l[9:].strip()}</div>""", unsafe_allow_html=True)

            with st.expander(f"📈 Sentiment & Frustration Context ({len(sentiments)})", expanded=True):
                for s in sentiments:
                    st.markdown(f"""<div class="memory-card"><span class="mem-badge badge-sentiment">SENTIMENT</span>{s[10:].strip()}</div>""", unsafe_allow_html=True)

            if others:
                with st.expander(f"💬 Recent Interactions ({len(others)})", expanded=False):
                    for o in others:
                        st.markdown(f"""<div class="memory-card"><span class="mem-badge badge-generic">EVENT</span>{o}</div>""", unsafe_allow_html=True)
        else:
            st.info("No memories currently stored in this customer's bank. Click 'Re-seed Demo History' in the sidebar.")

    # Tab 3: Visual architecture of Hindsight's Learning Loop
    with tab_loop:
        st.markdown("""
        #### How Hindsight Powers Ava's Self-Improvement
        ```
        Customer Message ("The webhook sync is failing again")
           │
           ▼
        1. RECALL (Hindsight Multi-Strategy Search)
           ├── Semantic vector search
           ├── Keyword & tag filtering (TICKET, LEARNING)
           └── Temporal & entity graph linking
           │
           ▼
        2. INJECT INTO SYSTEM PROMPT
           "CUSTOMER MEMORY:
            - Ticket #1042: 401 caused by expired webhook signing key
            - Preference: Wants short numbered steps, no repeat questions"
           │
           ▼
        3. GENERATE (Groq openai/gpt-oss-120b)
           Ava provides instant, personalized, empathetic diagnosis
           │
           ▼
        4. RETAIN (Hindsight Bank: customer-maya-chen-brightpath)
           Interactions stored safely
           │
           ▼
        5. RESOLUTION LEARNING EXTRACTOR (Mark Resolved & Learn)
           Autonomous LLM extracts durable facts:
           → "LEARNING: Webhook failures recur with key rotations; proactively monitor."
        ```
        """)
        st.info("💡 **Key Differentiator:** Unlike static vector databases that dump raw chat logs, Hindsight consolidates observations and distills learnings so memory gets cleaner and more intelligent over time.")
