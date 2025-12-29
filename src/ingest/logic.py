from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.shared.hashing import payload_hash, stable_event_id
from src.shared.timeutil import parse_iso_utc, iso_utc, day_str, hour_str

def build_ingest_artifacts(body: dict[str, Any], ingest_time_dt: datetime) -> dict[str, Any]:
    """
    Pure function:
    - computes payload_sha, stable event_id
    - computes lag_ms
    - builds s3_key (partition-friendly)
    - builds DynamoDB items (EventsTable + DedupeTable)
    No AWS side effects here. Easy to unit test.
    """
    if ingest_time_dt.tzinfo is None:
        ingest_time_dt = ingest_time_dt.replace(tzinfo=timezone.utc)
    ingest_time_dt = ingest_time_dt.astimezone(timezone.utc)

    source = str(body["source"])
    event_type = str(body["event_type"])
    entity_id = str(body["entity_id"])
    event_time_dt = parse_iso_utc(str(body["event_time"]))
    event_time_iso = iso_utc(event_time_dt)
    ingest_time_iso = iso_utc(ingest_time_dt)

    payload = body["payload"]
    payload_sha = payload_hash(payload)
    idempotency_key = body.get("idempotency_key")

    event_id = stable_event_id(source, event_type, entity_id, event_time_iso, payload_sha, idempotency_key)

    lag_ms = int((ingest_time_dt - event_time_dt).total_seconds() * 1000)
    if lag_ms < 0:
        # if producer clock is ahead, clamp to 0 for metrics sanity
        lag_ms = 0

    ev_day = day_str(event_time_dt)
    ing_day = day_str(ingest_time_dt)
    ev_hour = hour_str(event_time_dt)

    s3_key = (
        f"raw/source={source}/event_type={event_type}/"
        f"event_date={ev_day}/ingest_date={ing_day}/hour={ev_hour}/"
        f"event_id={event_id}.json"
    )

    pk = f"ENTITY#{entity_id}"
    sk = f"TS#{event_time_iso}#EID#{event_id}"

    gsi1pk = f"SRC#{source}#TYPE#{event_type}#DAY#{ev_day}"
    gsi1sk = f"LAG#{lag_ms}#TS#{ingest_time_iso}#EID#{event_id}"

    events_item = {
        "PK": pk,
        "SK": sk,
        "event_id": event_id,
        "source": source,
        "event_type": event_type,
        "entity_id": entity_id,
        "event_time": event_time_iso,
        "ingest_time": ingest_time_iso,
        "ingest_lag_ms": lag_ms,
        "payload_sha": payload_sha,
        "day": ev_day,
        "hour": ev_hour,
        "s3_key": s3_key,
        "GSI1PK": gsi1pk,
        "GSI1SK": gsi1sk,
        # status gets set in the AWS layer once we know dedupe result
        "status": "PENDING",
    }

    dedupe_item = {
        "event_id": event_id,
        "first_seen_ingest_time": ingest_time_iso,
        "entity_id": entity_id,
        "source": source,
        "event_type": event_type,
        "event_time": event_time_iso,
        # default: 30 days (can be overridden by env later)
        "ttl_epoch": int(ingest_time_dt.timestamp()) + 30 * 86400,
    }

    return {
        "event_id": event_id,
        "payload_sha": payload_sha,
        "lag_ms": lag_ms,
        "s3_key": s3_key,
        "event_time_iso": event_time_iso,
        "ingest_time_iso": ingest_time_iso,
        "events_item": events_item,
        "dedupe_item": dedupe_item,
    }
