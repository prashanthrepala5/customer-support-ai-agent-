"""
seed_history.py - Pre-seeds realistic customer interaction history
for demo customers (Maya Chen, Alex Rivera, Jordan Taylor).

Provides rich context so judges and users can immediately witness
multi-week memory recall, past ticket referencing, and style adaptation.
"""

import sys
import logging
from memory import remember, get_all_memories, bank_for, _get_hindsight_client

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("seed_history")

DEMO_CUSTOMER_ID = "maya-chen-brightpath"

# Rich historical memories per customer
CUSTOMER_SEED_MAP = {
    "maya-chen-brightpath": [
        "FACT: Customer: Maya Chen (Ops Lead, Brightpath Fitness - SaaS Billing Customer). "
        "Plan: Growth Tier ($499/mo). Primary Stack: Stripe Webhooks on Node.js/Express (v18, AWS ECS Fargate). "
        "Webhook Endpoint: https://api.brightpathfit.com/v1/stripe/webhooks. "
        "Database: PostgreSQL on RDS. Communication preference: Email / direct technical summary.",

        "TICKET: Ticket #1042 (2026-01-08) - Issue: Recurring Webhook 401 Unauthorized errors during subscription renewal webhook delivery. "
        "Logs: 'Webhook signature verification failed: timestamp outside tolerance or secret mismatch'. "
        "Cause: Expired Stripe webhook signing secret following quarterly key rotation; .env was not updated in AWS ECS task. "
        "Fix: Regenerated STRIPE_WEBHOOK_SECRET in Stripe dashboard and pushed updated ECS task definition with new secret. Resolved in 12 mins.",

        "TICKET: Ticket #1057 (2026-01-15) - Issue: Duplicate customer charge records appearing during peak hour billing sync. "
        "Logs: 'POST /webhooks/stripe 200 OK - duplicate entry for invoice.payment_succeeded evt_3Pq8...'. "
        "Cause: Network retries from Stripe webhook dispatch without application-level deduplication. "
        "Fix: Implemented Redis-backed idempotency check using event ID `evt_*` with 24-hour expiration TTL before DB writes. Fully verified.",

        "TICKET: Ticket #1063 (2026-01-22) - Issue: Delayed webhook event delivery alerts (5-8 minute delivery lag) during morning class booking spikes. "
        "Logs: 'SQS queue depth: 4,200 pending messages, processing latency high'. "
        "Cause: Webhook receiver worker concurrency bottleneck on single ECS Fargate task. "
        "Fix: Scaled ECS worker task count from 2 to 6 tasks and attached AWS Target Tracking Auto-scaling policy based on queue backlog. Resolved.",

        "LEARNING: Maya Chen strongly prefers short, numbered diagnostic steps and direct CLI/code snippets. "
        "Hates being asked generic questions like 'What is your stack?' or having to re-explain previous resolutions. "
        "Values speed, minimal fluff, and operational precision.",

        "SENTIMENT: Frustration rising across January (this is her 3rd contact this month). "
        "Expressed concern to account manager regarding infrastructure stability ahead of Brightpath's national New Year marketing campaign. "
        "Needs calm, reassuring tone and proactive root-cause resolution without bureaucratic runaround."
    ],
    "alex-rivera-fintech": [
        "FACT: Customer: Alex Rivera (VP Engineering, FlowPay - Fintech Payment Platform). "
        "Plan: Enterprise Tier ($2,499/mo). Stack: Go microservices, Kubernetes on GCP (GKE), Google Cloud SQL Postgres. "
        "API Integration: High-throughput payment routing gateway processing ~12,000 req/sec.",

        "TICKET: Ticket #1012 (2026-01-10) - Issue: Connection pool starvation under spike traffic. "
        "Fix: Adjusted PgBouncer max client connections and enabled transaction pooling mode.",

        "TICKET: Ticket #1089 (2026-02-02) - Issue: Idempotency key hash collisions in checkout API. "
        "Fix: Upgraded SHA-256 header hashing to include client merchant ID in payload salt.",

        "LEARNING: Alex Rivera prefers architecture diagrams, benchmark metrics, and Go code snippets. "
        "Appreciates deep technical root-cause explanations over surface-level advice."
    ],
    "jordan-taylor-cloud": [
        "FACT: Customer: Jordan Taylor (Product Lead, NovaCloud - Collaborative Workspace). "
        "Plan: Pro Tier ($199/mo). Stack: Next.js frontend, Python FastAPI backend on AWS Lambda.",

        "TICKET: Ticket #994 (2025-12-18) - Issue: Okta SAML 2.0 single sign-on redirect loop after certificate update. "
        "Fix: Uploaded renewed X.509 certificate into identity provider configuration and purged cached metadata.",

        "LEARNING: Jordan prefers high-level executive summaries followed by clear bulleted action items."
    ]
}


def seed_customer_history(customer_id: str = DEMO_CUSTOMER_ID):
    """
    Idempotently seeds memories into the Hindsight memory bank for the specified customer.
    If a memory is already present, it is not duplicated.
    """
    bank_id = bank_for(customer_id)
    customer_label = customer_id.replace("-", " ").title()
    logger.info("========================================================")
    logger.info("🌱 Seeding Hindsight Memory Bank: [%s]", bank_id)
    logger.info("Customer: %s", customer_label)
    logger.info("========================================================")

    # Ensure bank is created in Hindsight Cloud
    client = _get_hindsight_client()
    if client and hasattr(client, "create_bank"):
        try:
            client.create_bank(bank_id=bank_id, name=customer_label)
        except Exception:
            pass

    seed_items = CUSTOMER_SEED_MAP.get(customer_id, [
        f"FACT: Customer profile initialized for {customer_label}.",
        f"LEARNING: New customer session with active Hindsight long-term memory."
    ])

    existing_memories = set(get_all_memories(customer_id))
    added_count = 0
    skipped_count = 0

    for item in seed_items:
        if item in existing_memories:
            tag = item.split(":")[0]
            logger.info("  ⏭️  Skipped existing %s: %s...", tag, item[:65])
            skipped_count += 1
        else:
            success = remember(customer_id, item)
            tag = item.split(":")[0]
            if success:
                logger.info("  ✅ Retained %s: %s...", tag, item[:65])
                added_count += 1
            else:
                logger.info("  ⚠️  Fallback saved %s: %s...", tag, item[:65])
                added_count += 1

    logger.info("✨ Seeding Complete! Added: %d | Skipped: %d | Total: %d",
                added_count, skipped_count, len(get_all_memories(customer_id)))


if __name__ == "__main__":
    cust_id = sys.argv[1] if len(sys.argv) > 1 else DEMO_CUSTOMER_ID
    seed_customer_history(cust_id)
