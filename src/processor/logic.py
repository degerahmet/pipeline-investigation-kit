from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from src.shared.timeutil import parse_iso_utc, day_str, iso_utc
from src.shared.hashing import sha256_hex, canonical_json_bytes

def group_events_by_entity_day(raws: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in raws:
        entity_id = str(r["entity_id"])
        dt = parse_iso_utc(str(r["event_time"]))
        day = day_str(dt)
        groups[(entity_id, day)].append(r)
    return groups

def _inputs_hash(raws: list[dict[str, Any]]) -> str:
    # stable hash over ordered list of (event_id, payload_sha)
    ordered = sorted(raws, key=lambda x: (x["event_time"], x["event_id"]))
    minimal = [{"event_id": r["event_id"], "payload_sha": r.get("payload_sha", "")} for r in ordered]
    return sha256_hex(canonical_json_bytes(minimal))

def build_aggregate_item(*, entity_id: str, day: str, raws: list[dict[str, Any]], now: datetime, version: int) -> dict[str, Any]:
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now_iso = iso_utc(now)

    ordered = sorted(raws, key=lambda x: (x["event_time"], x["event_id"]))
    inputs_hash = _inputs_hash(ordered)

    return {
        "PK": f"ENTITY#{entity_id}",
        "SK": f"DAY#{day}#VER#{version}",
        "entity_id": entity_id,
        "day": day,
        "metric_name": "daily_event_count",
        "value": len(raws),
        "inputs_hash": inputs_hash,
        "computed_at": now_iso,
        "window_start": f"{day}T00:00:00Z",
        "window_end": f"{day}T23:59:59Z",
        "input_count": len(raws),
        "sample_event_ids": [r["event_id"] for r in ordered[:10]],
    }
