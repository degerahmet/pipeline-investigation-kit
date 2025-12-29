from datetime import datetime, timezone
from src.processor.logic import group_events_by_entity_day, build_aggregate_item

def test_group_events_by_entity_day():
    raws = [
        {
            "event_id": "e1",
            "entity_id": "user_1",
            "event_time": "2025-12-28T00:00:00Z",
            "payload_sha": "p1",
            "source": "demo",
            "event_type": "heartbeat",
        },
        {
            "event_id": "e2",
            "entity_id": "user_1",
            "event_time": "2025-12-28T01:00:00Z",
            "payload_sha": "p2",
            "source": "demo",
            "event_type": "heartbeat",
        },
        {
            "event_id": "e3",
            "entity_id": "user_2",
            "event_time": "2025-12-29T00:00:00Z",
            "payload_sha": "p3",
            "source": "demo",
            "event_type": "heartbeat",
        },
    ]
    groups = group_events_by_entity_day(raws)
    assert ("user_1", "2025-12-28") in groups
    assert ("user_2", "2025-12-29") in groups
    assert len(groups[("user_1", "2025-12-28")]) == 2

def test_build_aggregate_item_is_deterministic_for_same_inputs():
    raws = [
        {"event_id": "e2", "event_time": "2025-12-28T01:00:00Z", "payload_sha": "p2", "entity_id": "user_1"},
        {"event_id": "e1", "event_time": "2025-12-28T00:00:00Z", "payload_sha": "p1", "entity_id": "user_1"},
    ]
    now = datetime(2025, 12, 30, 0, 0, 0, tzinfo=timezone.utc)

    item1 = build_aggregate_item(entity_id="user_1", day="2025-12-28", raws=raws, now=now, version=1)
    item2 = build_aggregate_item(entity_id="user_1", day="2025-12-28", raws=raws, now=now, version=1)

    assert item1["PK"] == "ENTITY#user_1"
    assert item1["SK"] == "DAY#2025-12-28#VER#1"
    assert item1["metric_name"] == "daily_event_count"
    assert item1["value"] == 2
    assert item1["inputs_hash"] == item2["inputs_hash"]
    assert item1["sample_event_ids"] == ["e1", "e2"]  # sorted by time
