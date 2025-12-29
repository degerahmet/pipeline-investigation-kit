from src.shared.validation import validate_event

def test_validate_event_ok():
    body = {
        "source": "demo",
        "event_type": "heartbeat",
        "entity_id": "user_1",
        "event_time": "2025-12-28T23:59:59Z",
        "payload": {"a": 1}
    }
    ok, reason = validate_event(body)
    assert ok is True
    assert reason == ""

def test_validate_event_missing_field():
    body = {
        "source": "demo",
        "event_type": "heartbeat",
        "entity_id": "user_1",
        "event_time": "2025-12-28T23:59:59Z"
        # payload missing
    }
    ok, reason = validate_event(body)
    assert ok is False
    assert "Missing required field" in reason

def test_validate_event_payload_must_be_obj_or_array():
    body = {
        "source": "demo",
        "event_type": "heartbeat",
        "entity_id": "user_1",
        "event_time": "2025-12-28T23:59:59Z",
        "payload": "nope"
    }
    ok, reason = validate_event(body)
    assert ok is False
    assert "payload must be" in reason

def test_validate_event_event_time_must_be_iso():
    body = {
        "source": "demo",
        "event_type": "heartbeat",
        "entity_id": "user_1",
        "event_time": "28-12-2025",
        "payload": {"a": 1}
    }
    ok, reason = validate_event(body)
    assert ok is False
    assert "event_time must be ISO-8601" in reason
