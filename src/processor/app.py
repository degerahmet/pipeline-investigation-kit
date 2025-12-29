import json
import boto3
from datetime import datetime, timezone

from src.shared import config
from src.shared.logging import info, error
from src.shared.metrics import emf
from src.shared.s3util import get_json

from src.processor.logic import group_events_by_entity_day, build_aggregate_item

ddb = boto3.resource("dynamodb")
NAMESPACE = "PipelineInvestigationKit"

def handler(event, context):
    if config.is_dry_run():
        info("processor_dry_run", ok=True)
        return {"ok": True, "processed": 0, "errors": 0, "groups": 0, "dry_run": True}
    
    records = event.get("Records", []) or []
    info("processor_start", records=len(records))

    table = ddb.Table(config.AGG_TABLE)

    processed = 0
    errors = 0
    raws = []

    for record in records:
        try:
            msg = json.loads(record["body"])
            raw = get_json(msg["s3_bucket"], msg["s3_key"])
            raws.append(raw)
            processed += 1
            info(
                "processor_record_loaded",
                event_id=raw.get("event_id"),
                entity_id=raw.get("entity_id"),
                event_time=raw.get("event_time"),
                s3_bucket=msg.get("s3_bucket"),
                s3_key=msg.get("s3_key"),
            )
        except Exception as e:
            errors += 1
            error("processor_record_failed", err=str(e))
            continue

    groups = group_events_by_entity_day(raws)
    now = datetime.now(timezone.utc)

    # Simple versioning: unix seconds (later we can implement "query latest +1")
    version = int(now.timestamp())
    
    info("processor_grouped", groups=len(groups))
    for (entity_id, day), rs in groups.items():
        item = build_aggregate_item(entity_id=entity_id, day=day, raws=rs, now=now, version=version)
        table.put_item(Item=item)
        info(
            "processor_aggregate_written",
            entity_id=entity_id,
            day=day,
            version=version,
            metric_name=item["metric_name"],
            value=item["value"],
            input_count=item["input_count"],
            inputs_hash=item["inputs_hash"],
            window_start=item["window_start"],
            window_end=item["window_end"],
        )

    emf(NAMESPACE, {"ProcessorMessageCount": processed, "ProcessorErrorCount": errors}, {"Function": "processor"})

    return {"ok": True, "processed": processed, "errors": errors, "groups": len(groups)}
