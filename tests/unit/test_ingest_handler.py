import json
from types import SimpleNamespace
from unittest.mock import patch

from src.ingest.app import handler

# Mock environment variables
import os

os.environ["RAW_BUCKET"] = "test-bucket"
os.environ["EVENTS_TABLE"] = "events-table"
os.environ["DEDUPE_TABLE"] = "dedupe-table"

def _lambda_event(body: dict) -> dict:
    return {"body": json.dumps(body)}

def _ctx():
    return SimpleNamespace(aws_request_id="req-123")

@patch("src.ingest.app.emf")
@patch("src.ingest.app.put_json_immutable")
@patch("src.ingest.app.put")
@patch("src.ingest.app.conditional_put")
def test_ingest_handler_accepted_writes_s3_and_ddb(mock_cond_put, mock_put, mock_s3_put, mock_emf):
    mock_cond_put.return_value = True  # first time seen => ACCEPTED

    body = {
        "source": "demo",
        "event_type": "heartbeat",
        "entity_id": "user_123",
        "event_time": "2025-12-28T23:59:59Z",
        "payload": {"a": 1},
    }

    resp = handler(_lambda_event(body), _ctx())
    assert resp["statusCode"] == 200

    out = json.loads(resp["body"])
    assert out["status"] == "ACCEPTED"
    assert "event_id" in out

    # Dedupe gate called
    assert mock_cond_put.called

    # Accepted => S3 write
    assert mock_s3_put.called

    # EventsTable write always
    assert mock_put.called

    # Metrics emitted
    assert mock_emf.called

@patch("src.ingest.app.emf")
@patch("src.ingest.app.put_json_immutable")
@patch("src.ingest.app.put")
@patch("src.ingest.app.conditional_put")
def test_ingest_handler_duplicate_does_not_write_s3_but_writes_ddb(mock_cond_put, mock_put, mock_s3_put, mock_emf):
    mock_cond_put.return_value = False  # duplicate

    body = {
        "source": "demo",
        "event_type": "heartbeat",
        "entity_id": "user_123",
        "event_time": "2025-12-28T23:59:59Z",
        "payload": {"a": 1},
    }

    resp = handler(_lambda_event(body), _ctx())
    assert resp["statusCode"] == 200

    out = json.loads(resp["body"])
    assert out["status"] == "DUPLICATE"

    # Duplicate => should NOT write raw event again
    assert mock_s3_put.called is False

    # But should still write index row
    assert mock_put.called is True

    assert mock_emf.called is True

def test_ingest_handler_invalid_json_returns_400():
    resp = handler({"body": "{not-json"}, _ctx())
    assert resp["statusCode"] == 400
    out = json.loads(resp["body"])
    assert "error" in out

def test_ingest_handler_schema_invalid_returns_400():
    # missing payload
    body = {
        "source": "demo",
        "event_type": "heartbeat",
        "entity_id": "user_123",
        "event_time": "2025-12-28T23:59:59Z",
    }
    resp = handler(_lambda_event(body), _ctx())
    assert resp["statusCode"] == 400
    out = json.loads(resp["body"])
    assert "error" in out
