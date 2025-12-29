from src.replay.logic import build_replay_messages


def test_build_replay_messages_dedupes_by_event_id_and_formats_payload():
    items = [
        {
            "event_id": "e1",
            "entity_id": "user_1",
            "event_time": "2025-12-28T00:00:00Z",
            "source": "demo",
            "event_type": "heartbeat",
            "s3_bucket": "b",
            "s3_key": "k1",
            "status": "ACCEPTED",
        },
        # same event_id appears again (simulate duplicates / replays / retries)
        {
            "event_id": "e1",
            "entity_id": "user_1",
            "event_time": "2025-12-28T00:00:00Z",
            "source": "demo",
            "event_type": "heartbeat",
            "s3_bucket": "b",
            "s3_key": "k1",
            "status": "DUPLICATE",
        },
        # different event_id should be kept
        {
            "event_id": "e2",
            "entity_id": "user_1",
            "event_time": "2025-12-28T01:00:00Z",
            "source": "demo",
            "event_type": "heartbeat",
            "s3_bucket": "b",
            "s3_key": "k2",
            "status": "ACCEPTED",
        },
    ]

    # include_duplicates=False => de-dupe by event_id within this batch
    msgs = build_replay_messages(items, include_duplicates=False)
    assert len(msgs) == 2
    assert [m["event_id"] for m in msgs] == ["e1", "e2"]

    # payload format sanity
    assert msgs[0]["event_id"] == "e1"
    assert msgs[0]["s3_key"] == "k1"
    assert msgs[0]["s3_bucket"] == "b"

    # include_duplicates=True => keep all (including repeated event_id)
    msgs2 = build_replay_messages(items, include_duplicates=True)
    assert len(msgs2) == 3


def test_build_replay_messages_limits():
    items = []
    for i in range(10):
        items.append(
            {
                "event_id": f"e{i}",
                "entity_id": "user_1",
                "event_time": "2025-12-28T00:00:00Z",
                "source": "demo",
                "event_type": "heartbeat",
                "s3_bucket": "b",
                "s3_key": f"k{i}",
                "status": "ACCEPTED",
            }
        )

    msgs = build_replay_messages(items, include_duplicates=False, limit=3)
    assert len(msgs) == 3
    assert msgs[0]["event_id"] == "e0"
