import os
import json
from types import SimpleNamespace
from unittest.mock import patch

# env (config import safe ama handler runtime için set ediyoruz)
os.environ["EVENTS_TABLE"] = "events-table"
os.environ["REPLAY_QUEUE_URL"] = "https://sqs.fake/queue"

from src.replay.app import handler

def _lambda_event(body: dict) -> dict:
    return {"body": json.dumps(body)}

def _ctx():
    return SimpleNamespace(aws_request_id="req-1")

@patch("src.replay.app.emf")
@patch("src.replay.app.sqs")
@patch("src.replay.app.ddb")
def test_replay_handler_queries_and_sends_messages(mock_ddb, mock_sqs, mock_emf):
    # Mock DynamoDB table query result
    table = mock_ddb.Table.return_value
    table.query.return_value = {
        "Items": [
            {
                "event_id": "e1",
                "entity_id": "user_1",
                "event_time": "2025-12-28T00:00:00Z",
                "source": "demo",
                "event_type": "heartbeat",
                "s3_bucket": "b",
                "s3_key": "k1",
                "status": "ACCEPTED",
                "PK": "ENTITY#user_1",
                "SK": "TS#2025-12-28T00:00:00Z#EID#e1",
            }
        ]
    }

    body = {
        "entity_id": "user_1",
        "start_time": "2025-12-28T00:00:00Z",
        "end_time": "2025-12-29T00:00:00Z",
        "limit": 100,
        "include_duplicates": False,
    }

    resp = handler(_lambda_event(body), _ctx())
    assert resp["statusCode"] == 200
    out = json.loads(resp["body"])
    assert out["sent"] == 1

    # should send 1 message to SQS
    assert mock_sqs.send_message.called is True
    assert mock_emf.called is True

def test_replay_handler_missing_fields_returns_400():
    resp = handler(_lambda_event({"entity_id": "u"}), _ctx())
    assert resp["statusCode"] == 400
