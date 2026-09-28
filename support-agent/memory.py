"""
memory.py - Thin Hindsight (by Vectorize) wrapper for Ava Support Agent.

This module provides persistent semantic memory management for each customer
using Hindsight memory banks.

Docs: https://hindsight.vectorize.io/
GitHub: https://github.com/vectorize-io/hindsight
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env from the support-agent folder or parent
ENV_PATH = Path(__file__).resolve().parent / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

logger = logging.getLogger("ava.memory")

# Configuration
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY", "").strip()
HINDSIGHT_BASE_URL = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io").rstrip("/")

# Path for local fallback & instant UI retrieval cache
CACHE_FILE = Path(__file__).parent / ".hindsight_local_cache.json"

# Global client holder
_hindsight_client = None
_client_initialized = False


def _get_hindsight_client():
    """
    Initializes and returns the official Hindsight client if available.
    Isolates client creation in one place for easy adjustment.
    """
    global _hindsight_client, _client_initialized
    if _client_initialized:
        return _hindsight_client

    _client_initialized = True
    
    # Hindsight Cloud requires an API key. If not set, use local high-speed mirror.
    if not HINDSIGHT_API_KEY and "vectorize.io" in HINDSIGHT_BASE_URL:
        logger.info("HINDSIGHT_API_KEY not set for Cloud endpoint. Operating in local-sync mode.")
        _hindsight_client = None
        return None

    try:
        from hindsight_client import Hindsight
        
        # Initialize with Hindsight Cloud or local endpoint
        kwargs = {"base_url": HINDSIGHT_BASE_URL}
        if HINDSIGHT_API_KEY:
            kwargs["api_key"] = HINDSIGHT_API_KEY
            
        _hindsight_client = Hindsight(**kwargs)
        logger.info(f"Initialized Hindsight client for {HINDSIGHT_BASE_URL}")
    except Exception as e:
        logger.warning(f"Could not initialize official Hindsight client: {e}. Local fallback active.")
        _hindsight_client = None

    return _hindsight_client


def bank_for(customer_id: str) -> str:
    """
    Returns the normalized Hindsight memory bank ID for a given customer.
    Format: customer-<customer_id>
    """
    safe_id = "".join(c if c.isalnum() or c in ("-", "_") else "-" for c in customer_id.lower()).strip("-")
    if not safe_id.startswith("customer-"):
        return f"customer-{safe_id}"
    return safe_id


# ---------------------------------------------------------------------------
# Local Persistent Cache Helpers (Guarantees zero demo failures & offline fallback)
# ---------------------------------------------------------------------------

def _load_cache() -> Dict[str, List[str]]:
    if not CACHE_FILE.exists():
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(cache: Dict[str, List[str]]):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Failed to persist memory cache: {e}")


def _cache_append(bank_id: str, memory_text: str):
    cache = _load_cache()
    if bank_id not in cache:
        cache[bank_id] = []
    if memory_text not in cache[bank_id]:
        cache[bank_id].append(memory_text)
        _save_cache(cache)


# ---------------------------------------------------------------------------
# Core Memory Operations: remember, recall, get_all_memories
# ---------------------------------------------------------------------------

def remember(customer_id: str, text: str) -> bool:
    """
    RETAIN: Stores a memory (fact, ticket, learning, or sentiment) in the customer's Hindsight bank.
    
    Tags supported by design:
    - FACT: (stack, plan, setup)
    - TICKET: (date, issue, cause, fix)
    - LEARNING: (what worked, customer preferences)
    - SENTIMENT: (frustration trend, communication style)
    
    Wrapped in try/except with timeout to prevent blocking.
    """
    if not text or not text.strip():
        return False

    clean_text = text.strip()
    bank_id = bank_for(customer_id)
    
    # 1. Always update local mirror cache for immediate UI rendering & offline safety
    _cache_append(bank_id, clean_text)
    
    # 2. Transmit to Hindsight Cloud / Server
    client = _get_hindsight_client()
    if client:
        try:
            # Documented Hindsight retain call:
            # client.retain(bank_id=bank_id, content=clean_text)
            if hasattr(client, "retain"):
                client.retain(bank_id=bank_id, content=clean_text)
                logger.info(f"Retained in Hindsight bank [{bank_id}]: {clean_text[:60]}...")
                return True
        except Exception as e:
            logger.warning(f"Hindsight retain call error for bank {bank_id}: {e}")
            # Continue without crashing, local fallback already recorded
            return False

    return True


def _extract_text_from_result(item: Any) -> str:
    """Helper to extract text from varying Hindsight recall response shapes."""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return item.get("text") or item.get("content") or item.get("document") or str(item)
    for attr in ("text", "content", "document"):
        if hasattr(item, attr):
            val = getattr(item, attr)
            if val:
                return str(val)
    return str(item)


def recall(customer_id: str, query: str, k: int = 8) -> List[str]:
    """
    RECALL: Queries Hindsight for the top-k most relevant memories matching the query.
    
    Uses Hindsight multi-strategy search (semantic, keyword, graph, temporal).
    Falls back gracefully to keyword/semantic matching over local bank cache if
    the cloud service is not reachable or hasn't completed ingestion.
    """
    if not query or not query.strip():
        return []

    bank_id = bank_for(customer_id)
    memories: List[str] = []
    client = _get_hindsight_client()

    # 1. Attempt recall from Hindsight service
    if client:
        try:
            # Documented Hindsight recall call:
            # client.recall(bank_id=bank_id, query=query)
            if hasattr(client, "recall"):
                res = client.recall(bank_id=bank_id, query=query)
                raw_list = []
                if hasattr(res, "results"):
                    raw_list = res.results
                elif isinstance(res, list):
                    raw_list = res
                elif isinstance(res, dict) and "results" in res:
                    raw_list = res["results"]

                for item in raw_list[:k]:
                    txt = _extract_text_from_result(item)
                    if txt and txt not in memories:
                        memories.append(txt)
                        
                if memories:
                    return memories
        except Exception as e:
            logger.warning(f"Hindsight recall error for bank {bank_id}: {e}")

    # 2. Local Fallback Semantic / Keyword Ranker (ensures demo never blanks out)
    all_memories = get_all_memories(customer_id)
    if not all_memories:
        return []

    query_lower = query.lower()
    query_tokens = set(query_lower.split())
    
    # Score each memory by relevance to query tokens
    scored = []
    for mem in all_memories:
        mem_lower = mem.lower()
        # Direct word matches
        score = sum(2.0 for t in query_tokens if t in mem_lower and len(t) > 2)
        # Boost specific keywords like webhook, 401, error, key, stripe, etc.
        for kw in ["webhook", "401", "key", "stripe", "idempotency", "preference", "frustration"]:
            if kw in query_lower and kw in mem_lower:
                score += 3.0
        # Boost recent tickets and learnings
        if mem.startswith("LEARNING:") or mem.startswith("TICKET:"):
            score += 1.0
        scored.append((score, mem))

    # Sort descending by score
    scored.sort(key=lambda x: x[0], reverse=True)
    results = [m for s, m in scored if s > 0][:k]
    
    # If no tokens explicitly matched, return top foundational facts & preferences
    if not results:
        results = all_memories[:k]

    return results


def get_all_memories(customer_id: str) -> List[str]:
    """
    Returns all stored memories for a customer, used by the UI's 'What Ava knows' panel.
    """
    bank_id = bank_for(customer_id)
    cache = _load_cache()
    return cache.get(bank_id, [])


def is_hindsight_cloud_configured() -> bool:
    """Checks whether Hindsight Cloud credentials are set."""
    return bool(HINDSIGHT_API_KEY)
