from datetime import datetime, timezone
from src.ingest.logic import build_ingest_artifacts

def test_build_ingest_artifacts_generates_stable_event_id_and_keys():
    body = {
        "source": "demo",
        "event_type": "heartbeat",
        "entity_id": "user_123",
        "event_time": "2025-12-28T23:59:59Z",
        "payload": {"b": 2, "a": 1},  # intentionally unordered
    }

    ingest_time = datetime(2025, 12, 29, 0, 0, 59, tzinfo=timezone.utc)

    out1 = build_ingest_artifacts(body, ingest_time)
    out2 = build_ingest_artifacts(body, ingest_time)

    assert out1["event_id"] == out2["event_id"]
    assert out1["payload_sha"] == out2["payload_sha"]
    assert out1["lag_ms"] == 60_000  # 1 minute

    # S3 layout checks
    assert out1["s3_key"].startswith("raw/source=demo/event_type=heartbeat/")
    assert "event_date=2025-12-28" in out1["s3_key"]
    assert "ingest_date=2025-12-29" in out1["s3_key"]
    assert "hour=23" in out1["s3_key"]
    assert out1["s3_key"].endswith(f"event_id={out1['event_id']}.json")

def test_build_ingest_artifacts_uses_idempotency_key_when_present():
    body = {
        "source": "demo",
        "event_type": "heartbeat",
        "entity_id": "user_123",
        "event_time": "2025-12-28T23:59:59Z",
        "payload": {"a": 1},
        "idempotency_key": "ABC-123",
    }
    ingest_time = datetime(2025, 12, 29, 0, 0, 0, tzinfo=timezone.utc)

    out = build_ingest_artifacts(body, ingest_time)
    assert out["event_id"]  # non-empty
    # if payload changes but idempotency_key same, event_id stays same
    body2 = {**body, "payload": {"a": 999}}
    out2 = build_ingest_artifacts(body2, ingest_time)
    assert out["event_id"] == out2["event_id"]

def test_build_ingest_artifacts_builds_ddb_items():
    body = {
        "source": "demo",
        "event_type": "heartbeat",
        "entity_id": "user_123",
        "event_time": "2025-12-28T23:59:59Z",
        "payload": {"a": 1},
    }
    ingest_time = datetime(2025, 12, 29, 0, 0, 0, tzinfo=timezone.utc)

    out = build_ingest_artifacts(body, ingest_time)
    ev = out["events_item"]
    dd = out["dedupe_item"]

    assert ev["PK"] == "ENTITY#user_123"
    assert ev["event_type"] == "heartbeat"
    assert ev["source"] == "demo"
    assert "GSI1PK" in ev and "GSI1SK" in ev

    assert dd["event_id"] == out["event_id"]
    assert dd["entity_id"] == "user_123"
    assert dd["ttl_epoch"] > 0
