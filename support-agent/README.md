# 🧠 Ava — AI Customer Support Agent with Hindsight Memory

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Hindsight Memory](https://img.shields.io/badge/Memory-Hindsight%20Cloud-6366F1?style=for-the-badge&logo=vectorize&logoColor=white)](https://hindsight.vectorize.io)
[![Groq LLM](https://img.shields.io/badge/LLM-Groq%20Cloud%20(120B)-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com)
[![Streamlit UI](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

**"A support agent that never makes a customer repeat their story — it remembers every ticket, every fix that worked, and every frustration, and gets sharper with each interaction."**

*Built for the **Vectorize Hindsight Hackathon: AI Agents That Learn Using Hindsight**.*

[Live Demo](#-60-second-demo-script-for-judges) • [Architecture](#-architecture) • [How Hindsight Memory is Used](#-how-hindsight-memory-is-used) • [Quickstart](#-quickstart--installation) • [Judging Criteria](#-judging-criteria-alignment)

</div>

---

## 📌 Executive Summary & The Problem

Nothing damages customer trust faster than being forced to repeat your story across multiple tickets, agents, and weeks. 

Standard LLM chatbots are **stateless**: every interaction starts from blank context. They ask customers for their environment, tech stack, and recent changes repeatedly — even after three previous escalations.

**Ava changes this paradigm** by using **[Hindsight by Vectorize](https://hindsight.vectorize.io/)** as a dedicated long-term cognitive layer:
- **Zero Repetition:** Ava never asks for customer stack details, payment providers, or endpoints.
- **Deep Multi-Week Recall:** Remembers Ticket #1042 from 3 weeks ago where webhook 401 errors were caused by expired signing secrets after quarterly key rotation.
- **Adaptive Behavioral Tone:** Senses customer frustration trend (3rd contact this month) and automatically adopts preferred communication style (concise numbered diagnostic steps, zero bureaucratic runaround).
- **Autonomous Learning Loop:** When a ticket is resolved, Ava extracts durable facts into Hindsight so the agent becomes permanently smarter for future interactions.

---

## 🏗️ Architecture

```
                                  CUSTOMER CHAT (Streamlit)
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       │                                           │
             [Memory Toggle = ON]                        [Memory Toggle = OFF]
                       │                                           │
                       ▼                                           ▼
            1. RECALL FROM HINDSIGHT                   Bypass Hindsight Memory
        Multi-Strategy Search (k=8)                                │
        Bank: customer-maya-chen-brightpath                        │
                       │                                           │
                       ▼                                           ▼
            2. INJECT SYSTEM PROMPT                     Standard Generic Prompt
        • System Facts (Stack, Webhook URL, Tier)       (No customer context)
        • Past Tickets (#1042, #1057, #1063)                       │
        • Customer Preferences (Numbered steps)                    │
        • Sentiment Context (Rising frustration)                   │
                       │                                           │
                       └─────────────────────┬─────────────────────┘
                                             │
                                             ▼
                               3. GENERATE WITH GROQ
                         Model: openai/gpt-oss-120b
                         (Ultra-fast, low-latency inference)
                                             │
                                             ▼
                                4. RETAIN INTO HINDSIGHT
                       Store customer prompt & Ava's response
                                             │
                                             ▼
                           5. RESOLUTION LEARNING LOOP
                         Autonomous Distillation on Resolution
                         Extracts durable facts → LEARNING: ...
```

---

## 🧠 Memory Design (Hindsight Memory Banks)

Ava creates an **isolated memory bank per customer**: `customer-<customer_id>` (e.g. `customer-maya-chen-brightpath`). 

Every memory is structured and categorized using clear domain prefixes:

| Category | Prefix | Purpose | Example |
|---|---|---|---|
| **Facts** | `FACT:` | Core technical environment, plan tier, endpoints | `FACT: Primary Stack: Stripe Webhooks on Node.js/Express (AWS ECS Fargate).` |
| **Tickets** | `TICKET:` | Historical tickets, root causes, and verified fixes | `TICKET: Ticket #1042 (Jan 8) - 401 Unauthorized caused by expired signing secret after key rotation. Fixed.` |
| **Learnings** | `LEARNING:` | Behavioral preferences, operating constraints, patterns | `LEARNING: Maya Chen strongly prefers short numbered steps and direct CLI snippets. Hates generic questions.` |
| **Sentiment** | `SENTIMENT:` | Frustration trend, urgency, and communication cues | `SENTIMENT: Frustration rising across January (3rd contact). Needs calm, reassuring tone and fast resolution.` |

---

## 🎬 60-Second Demo Script (For Judges)

### Scenario:
*Maya Chen (Ops Lead at Brightpath Fitness) has experienced webhook delivery issues three times this month. Watch her fourth interaction.*

| Step | Action | With Hindsight Memory (ON) | Without Memory (OFF) |
|---|---|---|---|
| **1** | Maya types: *"The webhook sync is failing again."* | **Personalized & Direct:** Ava greets Maya by name, notes this is her 3rd contact this month, references past **Ticket #1042** (expired signing secret) and **Ticket #1057** (idempotency key), and outputs short numbered diagnostic commands. Asks **0 generic questions**. | **Generic & Frustrating:** *"I'm sorry to hear that. Could you share your payment provider, endpoint URL, and error message?"* |
| **2** | Inspect **Memory Panel** | The **"Recalled for Latest Reply"** panel highlights the 7 memories Hindsight retrieved in real time. | Panel displays: *"Memory disabled — zero customer context used."* |
| **3** | Click **"Mark Resolved & Learn"** | Ava runs an autonomous LLM distillation that extracts: `LEARNING: Rotated Stripe signing secret to restore 200 OK. Key rotation frequently precedes failures; proactive expiry monitoring recommended.` | Nothing is learned or saved. Next ticket starts from scratch. |

---

## 🔍 How Hindsight Memory is Used

Hindsight is the central pillar of Ava's architecture, accounting for all personalization and context awareness:

### 1. Isolated Per-Customer Memory Banks
Each customer is allocated a distinct Hindsight bank (`customer-<customer_id>`). This prevents cross-tenant contamination, guarantees compliance, and ensures retrieval is scoped strictly to the relevant organization.

### 2. Multi-Strategy Recall-Before-Reply
Before formulating an answer, Ava queries Hindsight via `recall(bank_id, query, k=8)`. Hindsight uses:
- **Semantic Vector Search:** Retrieves semantically relevant past error symptoms.
- **Keyword & Tag Matching:** Surfaces relevant `TICKET:`, `LEARNING:`, and `FACT:` entries.
- **Temporal & Graph Reasoning:** Understands chronological incident progression (Jan 8 → Jan 15 → Jan 22).

The recalled memories are injected into Ava's system prompt under a `CUSTOMER MEMORY` block.

### 3. Retain-After-Reply
After each turn, `remember(bank_id, text)` records the interaction into Hindsight with date timestamps to maintain continuity.

### 4. Continuous Learning Extractor (`learn_from_resolution`)
Dumping raw chat transcripts creates noisy, bloated vector memory. Ava solves this with an **autonomous post-resolution learning loop**:
- When the support session is resolved, a lightweight LLM call analyzes the dialogue.
- It extracts **only durable facts** (root cause, verified solution, customer preferences, and recurrence patterns).
- These are committed as `LEARNING:` items in Hindsight, ensuring memory gets **cleaner and more accurate over time**.

### 5. Instant A/B Memory Verification
The top-bar **Hindsight Memory Toggle** allows anyone to switch between stateful (Hindsight ON) and stateless (Hindsight OFF) generation in real time, proving that memory is responsible for 100% of the customer experience improvement.

---

## 🚀 Quickstart & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/prashanthrepala5/customer-support-ai-agent-.git
cd customer-support-ai-agent-
```

### 2. Setup Virtual Environment
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env`:
```ini
# Groq API Key (get from console.groq.com)
GROQ_API_KEY=your_groq_api_key
GROQ_BASE_URL=https://api.groq.com

# Hindsight Cloud Configuration
# Sign up at https://ui.hindsight.vectorize.io and use promo code MEMHACK99 in Billing for $50 free credits!
HINDSIGHT_API_KEY=your_hindsight_api_key
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
```
*(Note: A local mirror cache is built into `memory.py` so the demo works right out of the box even before cloud credentials are added!)*

### 4. Seed Realistic Customer History
Pre-seeds ~3 weeks of realistic production support tickets for customer **Maya Chen (Brightpath Fitness)**:
```bash
python seed_history.py
```

### 5. Launch the Streamlit Application
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 📊 Judging Criteria Alignment

| Criteria | Weight | How Ava Exceeds Expectations |
|---|---|---|
| **Innovation** | 30% | Dual-phase memory architecture: live contextual multi-strategy recall paired with autonomous post-resolution distillation. |
| **Use of Hindsight Memory** | 25% | Memory is the central star: tenant bank isolation, categorized tags (`FACT`, `TICKET`, `LEARNING`, `SENTIMENT`), and a live side-by-side memory inspector panel. |
| **Technical Implementation** | 20% | Clean, modular Python; automatic Groq model fallback (`openai/gpt-oss-120b` → `qwen/qwen3.8-27b`); zero crash tolerance; idempotent seeding. |
| **User Experience** | 15% | Modern dark-mode UI; real-time memory badges on responses; one-click prompt triggers for judges; visual Hindsight learning loop diagram. |
| **Real-world Impact** | 10% | Solves the #1 complaint in B2B SaaS customer support: having to re-explain technical context across multiple tickets. |

---

## 🛠️ Tech Stack
- **Memory Engine:** [Hindsight](https://hindsight.vectorize.io/) by Vectorize (`hindsight-client`)
- **LLM Inference:** [Groq](https://groq.com/) Cloud (`openai/gpt-oss-120b`)
- **Frontend / UI:** [Streamlit](https://streamlit.io/)
- **Language:** Python 3.11+

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
