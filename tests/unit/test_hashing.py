from src.shared.hashing import payload_hash, stable_event_id

def test_payload_hash_is_canonical():
    p1 = {"a": 1, "b": 2}
    p2 = {"b": 2, "a": 1}
    assert payload_hash(p1) == payload_hash(p2)

def test_event_id_stable_without_idempotency_key():
    payload_sha = payload_hash({"x": 1})
    eid1 = stable_event_id("demo", "t", "u1", "2025-01-01T00:00:00Z", payload_sha, None)
    eid2 = stable_event_id("demo", "t", "u1", "2025-01-01T00:00:00Z", payload_sha, None)
    assert eid1 == eid2

def test_event_id_uses_idempotency_key_when_present():
    payload_sha = payload_hash({"x": 1})
    eid1 = stable_event_id("demo", "t", "u1", "2025-01-01T00:00:00Z", payload_sha, "KEY123")
    eid2 = stable_event_id("demo", "t", "u1", "2025-01-01T00:00:00Z", payload_sha, "KEY123")
    assert eid1 == eid2

    # different idempotency key => different id
    eid3 = stable_event_id("demo", "t", "u1", "2025-01-01T00:00:00Z", payload_sha, "KEY999")
    assert eid1 != eid3
