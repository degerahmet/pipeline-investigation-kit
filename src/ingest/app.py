import json
from typing import Any

from src.shared import config
from src.shared.logging import info, warn
from src.shared.metrics import emf
from src.shared.validation import validate_event
from src.shared.s3util import put_json_immutable
from src.shared.ddb import conditional_put, put
from src.shared.timeutil import utc_now, iso_utc

from src.ingest.logic import build_ingest_artifacts



NAMESPACE = "PipelineInvestigationKit"

def _resp(code: int, body: dict[str, Any]):
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }

def handler(event, context):
    request_id = getattr(context, "aws_request_id", "unknown")
    info("dry_run_status", dry_run=config.is_dry_run())

    # 1) Parse JSON
    try:
        body = json.loads(event.get("body") or "{}")
    except Exception:
        emf(NAMESPACE, {"InvalidCount": 1}, {"Function": "ingest", "Reason": "invalid_json"})
        return _resp(400, {"error": "Invalid JSON body"})

    # 2) Validate minimal schema
    ok, reason = validate_event(body)
    if not ok:
        warn("event_invalid", request_id=request_id, reason=reason)
        emf(NAMESPACE, {"InvalidCount": 1}, {"Function": "ingest", "Reason": "schema"})
        return _resp(400, {"error": reason})

    # 3) Build pure artifacts (testable)
    ingest_time_dt = utc_now()
    artifacts = build_ingest_artifacts(body, ingest_time_dt)

    event_id = artifacts["event_id"]
    lag_ms = artifacts["lag_ms"]
    s3_key = artifacts["s3_key"]

    # 4) Dedupe gate
    if config.is_dry_run():
        dedupe_inserted = True
    else:
        dedupe_inserted = conditional_put(
            config.DEDUPE_TABLE,
            item=artifacts["dedupe_item"],
            condition_expression="attribute_not_exists(event_id)",
        )

    status = "ACCEPTED" if dedupe_inserted else "DUPLICATE"

    # 5) Write raw to S3 only if first seen (immutable-by-key)
    if dedupe_inserted and (not config.is_dry_run()):
        raw_record = {
            **body,
            "event_id": event_id,
            "event_time": artifacts["event_time_iso"],
            "ingest_time": artifacts["ingest_time_iso"],
            "payload_sha": artifacts["payload_sha"],
        }
        put_json_immutable(config.RAW_BUCKET, s3_key, raw_record)

    # 6) Write index row to EventsTable (always)
    events_item = artifacts["events_item"]
    events_item["s3_bucket"] = config.RAW_BUCKET
    events_item["status"] = status

    if not config.is_dry_run():
        put(config.EVENTS_TABLE, events_item)

    # 7) Metrics
    dims = {"Function": "ingest", "Source": events_item["source"], "Type": events_item["event_type"]}
    emf(NAMESPACE, {
        "IngestCount": 1,
        "DuplicateCount": 0 if dedupe_inserted else 1,
        "IngestLagMs": lag_ms,
    }, dims)

    info("event_ingested", request_id=request_id, event_id=event_id, status=status, lag_ms=lag_ms, s3_key=s3_key)

    return _resp(200, {
        "event_id": event_id,
        "status": status,
        "ingest_lag_ms": lag_ms,
        "s3_key": s3_key,
    })
