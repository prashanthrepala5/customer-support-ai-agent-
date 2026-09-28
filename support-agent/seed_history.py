"""
seed_history.py - Pre-seeds ~3 weeks of realistic customer interaction history
for customer "Maya Chen, Ops Lead at Brightpath Fitness".

This script provides instant, rich context so judges can immediately witness
multi-week memory recall, past ticket referencing, and style adaptation.

Run via:
    python seed_history.py
"""

import sys
import logging
from memory import remember, get_all_memories, bank_for

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("seed_history")

DEMO_CUSTOMER_ID = "maya-chen-brightpath"

# 3 weeks of realistic production SaaS customer memories
SEED_DATA = [
    # 1. Technical Stack & Account Facts
    "FACT: Customer: Maya Chen (Ops Lead, Brightpath Fitness - SaaS Billing Customer). "
    "Plan: Growth Tier ($499/mo). Primary Stack: Stripe Webhooks on Node.js/Express (v18, AWS ECS Fargate). "
    "Webhook Endpoint: https://api.brightpathfit.com/v1/stripe/webhooks. "
    "Database: PostgreSQL on RDS. Communication preference: Email / direct technical summary.",

    # 2. Ticket #1042 (Jan 8, 2026) - The recurring 401 webhook issue
    "TICKET: Ticket #1042 (2026-01-08) - Issue: Recurring Webhook 401 Unauthorized errors during subscription renewal webhook delivery. "
    "Logs: 'Webhook signature verification failed: timestamp outside tolerance or secret mismatch'. "
    "Cause: Expired Stripe webhook signing secret following quarterly key rotation; .env was not updated in AWS ECS task. "
    "Fix: Regenerated STRIPE_WEBHOOK_SECRET in Stripe dashboard and pushed updated ECS task definition with new secret. Resolved in 12 mins.",

    # 3. Ticket #1057 (Jan 15, 2026) - Duplicate charge syncs & idempotency
    "TICKET: Ticket #1057 (2026-01-15) - Issue: Duplicate customer charge records appearing during peak hour billing sync. "
    "Logs: 'POST /webhooks/stripe 200 OK - duplicate entry for invoice.payment_succeeded evt_3Pq8...'. "
    "Cause: Network retries from Stripe webhook dispatch without application-level deduplication. "
    "Fix: Implemented Redis-backed idempotency check using event ID `evt_*` with 24-hour expiration TTL before DB writes. Fully verified.",

    # 4. Ticket #1063 (Jan 22, 2026) - Delivery latency & queue worker scaling
    "TICKET: Ticket #1063 (2026-01-22) - Issue: Delayed webhook event delivery alerts (5-8 minute delivery lag) during morning class booking spikes. "
    "Logs: 'SQS queue depth: 4,200 pending messages, processing latency high'. "
    "Cause: Webhook receiver worker concurrency bottleneck on single ECS Fargate task. "
    "Fix: Scaled ECS worker task count from 2 to 6 tasks and attached AWS Target Tracking Auto-scaling policy based on queue backlog. Resolved.",

    # 5. Customer Behavioral Preferences & Communication Style
    "LEARNING: Maya Chen strongly prefers short, numbered diagnostic steps and direct CLI/code snippets. "
    "Hates being asked generic questions like 'What is your stack?' or having to re-explain previous resolutions. "
    "Values speed, minimal fluff, and operational precision.",

    # 6. Sentiment & Relationship Context
    "SENTIMENT: Frustration rising across January (this is her 3rd contact this month). "
    "Expressed concern to account manager regarding infrastructure stability ahead of Brightpath's national New Year marketing campaign. "
    "Needs calm, reassuring tone and proactive root-cause resolution without bureaucratic runaround."
]


def seed_customer_history(customer_id: str = DEMO_CUSTOMER_ID):
    """
    Idempotently seeds memories into the Hindsight memory bank for the demo customer.
    If a memory is already present, it is not duplicated.
    """
    bank_id = bank_for(customer_id)
    print(f"\n========================================================")
    print(f"🌱 Seeding Hindsight Memory Bank: [{bank_id}]")
    print(f"Customer: Maya Chen (Brightpath Fitness)")
    print(f"========================================================\n")

    existing_memories = set(get_all_memories(customer_id))
    added_count = 0
    skipped_count = 0

    for item in SEED_DATA:
        if item in existing_memories:
            tag = item.split(":")[0]
            print(f"  ⏭️  Skipped existing {tag}: {item[:65]}...")
            skipped_count += 1
        else:
            success = remember(customer_id, item)
            tag = item.split(":")[0]
            if success:
                print(f"  ✅ Retained {tag}: {item[:65]}...")
                added_count += 1
            else:
                print(f"  ⚠️  Fallback saved {tag}: {item[:65]}...")
                added_count += 1

    print(f"\n✨ Seeding Complete!")
    print(f"   • Added: {added_count} memories")
    print(f"   • Skipped: {skipped_count} (idempotent)")
    print(f"   • Total in bank: {len(get_all_memories(customer_id))} memories\n")


if __name__ == "__main__":
    cust_id = sys.argv[1] if len(sys.argv) > 1 else DEMO_CUSTOMER_ID
    seed_customer_history(cust_id)
