import json
import boto3
from typing import Any
from boto3.dynamodb.conditions import Key

from src.shared import config
from src.shared.logging import info
from src.shared.metrics import emf
from src.shared.timeutil import parse_iso_utc, iso_utc

from src.replay.logic import build_replay_messages

sqs = boto3.client("sqs")
ddb = boto3.resource("dynamodb")

NAMESPACE = "PipelineInvestigationKit"

def _resp(code: int, body: dict[str, Any]):
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }

def handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except Exception:
        return _resp(400, {"error": "Invalid JSON body"})

    entity_id = body.get("entity_id")
    start_time = body.get("start_time")
    end_time = body.get("end_time")
    limit = int(body.get("limit") or 500)
    include_duplicates = bool(body.get("include_duplicates") or False)

    if not entity_id or not start_time or not end_time:
        return _resp(400, {"error": "entity_id, start_time, end_time are required"})
    
    # Local/dev mode: don't touch AWS resources
    if config.is_dry_run():
        return _resp(200, {
            "entity_id": entity_id,
            "start_time": start_time,
            "end_time": end_time,
            "scanned": 0,
            "sent": 0,
            "dry_run": True,
        })

    start_iso = iso_utc(parse_iso_utc(start_time))
    end_iso = iso_utc(parse_iso_utc(end_time))

    pk = f"ENTITY#{entity_id}"
    table = ddb.Table(config.EVENTS_TABLE)

    sk_start = f"TS#{start_iso}"
    sk_end = f"TS#{end_iso}"

    resp = table.query(
        KeyConditionExpression=Key("PK").eq(pk) & Key("SK").between(sk_start, sk_end),
        Limit=limit
    )

    items = resp.get("Items", [])
    msgs = build_replay_messages(items, include_duplicates=include_duplicates, limit=limit)

    sent = 0
    for msg in msgs:
        sqs.send_message(
            QueueUrl=config.REPLAY_QUEUE_URL,
            MessageBody=json.dumps(msg, separators=(",", ":"))
        )
        sent += 1

    emf(NAMESPACE, {"ReplayRequestedCount": 1, "ReplayMessageCount": sent}, {"Function": "replay"})

    info("replay_enqueued", entity_id=entity_id, start=start_iso, end=end_iso, scanned=len(items), sent=sent)

    return _resp(200, {
        "entity_id": entity_id,
        "start_time": start_iso,
        "end_time": end_iso,
        "scanned": len(items),
        "sent": sent,
    })
