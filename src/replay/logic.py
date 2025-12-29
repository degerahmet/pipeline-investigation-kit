from __future__ import annotations
from typing import Any

def build_replay_messages(items, include_duplicates: bool, limit: int = 500):
    """
    Build replay messages from DynamoDB items.

    Ruleset (intentional, domain-agnostic):
      1) Require event_id. If missing -> skip.
      2) When include_duplicates=False:
         - Deduplicate by event_id within this replay batch (local de-dupe).
         - NOTE: We do NOT filter by 'status' (ACCEPTED/DUPLICATE) because
           some systems may write status differently or not at all.
      3) Require s3_bucket + s3_key (replay is about rehydrating raw events).
         If missing -> skip.
      4) Emit minimal message shape (event_id, entity_id, event_time, s3 refs).
      5) Enforce limit (first N after filtering).
    """
    messages = []
    seen = set()

    for item in items:
        event_id = item.get("event_id")
        if not event_id:
            continue

        # event_id deduplication
        if not include_duplicates and event_id in seen:
            continue
        seen.add(event_id)

        bucket = item.get("s3_bucket")
        key = item.get("s3_key")

        if not bucket or not key:
            continue

        messages.append({
            "event_id": event_id,
            "entity_id": item.get("entity_id"),
            "event_time": item.get("event_time"),
            "s3_bucket": bucket,
            "s3_key": key,
        })

        if len(messages) >= limit:
            break

    return messages
