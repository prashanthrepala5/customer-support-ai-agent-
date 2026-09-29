"""
agent.py - Core agent loop and learning extractor for Ava Support Agent.

Pipeline:
1. RECALL relevant customer history from Hindsight (or bypass if memory is toggled off)
2. Inject retrieved memories into system prompt
3. GENERATE response via Groq API (openai/gpt-oss-120b with retries and fallbacks)
4. RETAIN customer message and Ava's response into Hindsight
5. Learn durable facts upon ticket resolution (learn_from_resolution)
"""

import os
import time
import logging
from datetime import date
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

from memory import remember, recall, is_hindsight_cloud_configured

# Explicitly load .env from the support-agent folder or parent
ENV_PATH = Path(__file__).resolve().parent / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

# The official Groq Python SDK automatically reads GROQ_BASE_URL from os.environ.
# If GROQ_BASE_URL contains '/openai/v1', the SDK will append '/openai/v1/chat/completions',
# causing a 404 URL error. Sanitize os.environ so Groq SDK routes to official endpoint.
if "GROQ_BASE_URL" in os.environ and "openai/v1" in os.environ["GROQ_BASE_URL"]:
    del os.environ["GROQ_BASE_URL"]

logger = logging.getLogger("ava.agent")

# Groq Client setup
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

_groq_client = None


def get_groq_client() -> Groq:
    """Returns an initialized Groq client."""
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client


# System prompt configured for friendly, conversational customer support messages
AVA_SYSTEM_PROMPT = """You are Ava, a senior customer support agent.
Your objective is to help the customer solve their issue quickly in a friendly, conversational chat message format.

CRITICAL RULES:
- Output ONLY natural chat messages (like in WhatsApp, Zendesk, or Intercom).
- DO NOT use code blocks, terminal bash scripts, or SQL query boxes (never use ``` code blocks).
- Explain all troubleshooting steps in simple, plain, friendly English that anyone can follow.
- Address the current customer by their actual name from CURRENT CUSTOMER.
- NEVER mix up customers or refer to someone by another customer's name.
- Use CUSTOMER MEMORY before asking the customer anything.
- NEVER ask for information they've already given in past tickets or notes.
- Reference past tickets naturally when relevant ("Last time this was caused by...").
- Match your tone to the customer's frustration level with patience and reassurance.
- End every reply with one clear, friendly next step or check-in.
"""

# Models for Groq inference
PRIMARY_MODEL = "openai/gpt-oss-120b"
FALLBACK_MODELS = ["qwen/qwen3-32b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]


def _clean_message_format(text: str) -> str:
    """
    Ensures Ava's response is formatted strictly as a friendly customer chat message,
    converting any raw code fences into clean conversational instructions.
    """
    if not text:
        return ""
    lines = []
    for line in text.splitlines():
        if line.strip().startswith("```"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def _call_groq_with_fallback(messages: List[Dict[str, str]], temperature: float = 0.3) -> str:
    """
    Executes a Groq chat completion with 2 retries on the primary model,
    followed by fallback models, and finally a graceful fallback message.
    Guarantees the UI will never crash under demo conditions.
    """
    client = get_groq_client()
    models_to_try = [PRIMARY_MODEL] + FALLBACK_MODELS

    for model in models_to_try:
        # Up to 2 attempts per model
        for attempt in range(2):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=1024,
                )
                if response and response.choices and len(response.choices) > 0:
                    content = response.choices[0].message.content
                    if content and content.strip():
                        return content.strip()
            except Exception as e:
                logger.warning(f"Groq API call attempt {attempt + 1} failed on model {model}: {e}")
                time.sleep(0.5)

    # Ultimate graceful fallback if all network/API calls fail
    return (
        "I am reviewing your account details and past configuration right now. "
        "It looks like there is a temporary connection hiccup with our inference gateway. "
        "Please check your endpoint logs or retry in a moment, and I will be right here with you."
    )


def reply(
    customer_id: str,
    message: str,
    memory_enabled: bool = True,
    customer_name: Optional[str] = None,
    customer_role: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Agent loop (fixed pipeline):
    1. RECALL: query Hindsight with customer message (skip if memory_enabled is False).
    2. Format prompt with CURRENT CUSTOMER and CUSTOMER MEMORY block.
    3. GENERATE: call Groq LLM with Ava's system prompt.
    4. RETAIN: record customer message and agent reply into Hindsight memory bank.
    5. Return {"answer": str, "memories_used": List[str]}.
    """
    memories_used: List[str] = []
    
    # Step 1: RECALL memories if enabled
    if memory_enabled:
        try:
            memories_used = recall(customer_id=customer_id, query=message, k=8)
        except Exception as e:
            logger.warning(f"Recall step encountered exception: {e}")
            memories_used = []

    # Step 2: Inject memory block into prompt
    if memory_enabled and memories_used:
        memory_block = "\n".join(f"- {m}" for m in memories_used)
    else:
        memory_block = "(no prior history)"

    display_name = customer_name or customer_id.replace("-", " ").title()
    customer_header = f"CURRENT CUSTOMER: {display_name}"
    if customer_role:
        customer_header += f" ({customer_role})"

    user_prompt = f"{customer_header}\n\nCUSTOMER MEMORY:\n{memory_block}\n\nCUSTOMER MESSAGE:\n{message}"

    messages = [
        {"role": "system", "content": AVA_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    # Step 3: GENERATE reply
    raw_answer = _call_groq_with_fallback(messages, temperature=0.3)
    answer = _clean_message_format(raw_answer)

    # Step 4: RETAIN interactions into Hindsight (only when memory is enabled)
    if memory_enabled:
        today_str = date.today().isoformat()
        try:
            remember(customer_id, f"FACT: On {today_str}, customer reported: \"{message}\"")
            remember(customer_id, f"FACT: On {today_str}, Ava recommended: \"{answer[:200]}...\"")
        except Exception as e:
            logger.warning(f"Retain step encountered exception: {e}")

    return {
        "answer": answer,
        "memories_used": memories_used,
        "memory_enabled": memory_enabled,
    }


def learn_from_resolution(customer_id: str, conversation: List[Dict[str, str]]) -> List[str]:
    """
    Learning Extractor:
    Makes a lightweight LLM call after ticket resolution to extract ONLY durable facts:
    - What fixed the issue
    - Customer preferences
    - Sentiment trend
    - Recurring patterns

    Stores each item into Hindsight with the 'LEARNING:' prefix so future conversations
    are even sharper and cleaner.
    """
    if not conversation:
        return []

    # Build dialogue transcript for extractor
    transcript_lines = []
    for msg in conversation:
        role = msg.get("role", "user")
        speaker = "Customer" if role == "user" else "Ava"
        content = msg.get("content", "")
        transcript_lines.append(f"{speaker}: {content}")
    dialogue = "\n".join(transcript_lines)

    extractor_prompt = f"""You are a Knowledge Extraction system for customer support.
Analyze the following resolved customer support interaction:

---
{dialogue}
---

Extract durable facts from this resolution:
1. What specifically fixed the issue (root cause and resolution)
2. Discovered customer preferences or operating constraints
3. Sentiment trend or recurring operational patterns

Output ONLY 1 to 3 concise bullet points starting with a dash (-).
Do not include conversational filler or preambles.
Example format:
- Fix: Webhook 401 resolved by refreshing key and restarting worker.
- Customer prefers direct curl command diagnostics over UI walkthroughs.
- Webhook key rotation frequently precedes these failures; recommend proactive monitoring.
"""

    messages = [
        {"role": "system", "content": "You are a concise knowledge distillation assistant."},
        {"role": "user", "content": extractor_prompt},
    ]

    extracted_text = _call_groq_with_fallback(messages, temperature=0.1)

    # Parse bullet points and retain in Hindsight
    new_learnings = []
    for line in extracted_text.splitlines():
        line = line.strip()
        if line.startswith("-") or line.startswith("*"):
            bullet = line.lstrip("-* ").strip()
            if bullet:
                formatted_learning = f"LEARNING: {bullet}"
                remember(customer_id, formatted_learning)
                new_learnings.append(formatted_learning)

    # If parsing produced no bullets, store the distilled text directly
    if not new_learnings and extracted_text:
        formatted_learning = f"LEARNING: {extracted_text.strip()}"
        remember(customer_id, formatted_learning)
        new_learnings.append(formatted_learning)

    return new_learnings
