import os
import json
from unittest.mock import patch

os.environ["RAW_BUCKET"] = "raw-bucket"
os.environ["AGG_TABLE"] = "agg-table"

from src.processor.app import handler

def _sqs_event(msgs):
    return {
        "Records": [{"body": json.dumps(m)} for m in msgs]
    }

@patch("src.processor.app.emf")
@patch("src.processor.app.ddb")
@patch("src.processor.app.get_json")
def test_processor_handler_reads_raw_and_writes_aggregate(mock_get_json, mock_ddb, mock_emf):
    # Each SQS message points to an S3 object
    msgs = [
        {"s3_bucket": "raw-bucket", "s3_key": "k1"},
        {"s3_bucket": "raw-bucket", "s3_key": "k2"},
    ]

    # Mock S3 raw events (same entity+day)
    mock_get_json.side_effect = [
        {"event_id": "e1", "entity_id": "user_1", "event_time": "2025-12-28T00:00:00Z", "payload_sha": "p1"},
        {"event_id": "e2", "entity_id": "user_1", "event_time": "2025-12-28T01:00:00Z", "payload_sha": "p2"},
    ]

    table = mock_ddb.Table.return_value

    out = handler(_sqs_event(msgs), None)
    assert out["ok"] is True
    assert out["processed"] == 2
    assert out["errors"] == 0
    assert table.put_item.called is True
    assert mock_emf.called is True
