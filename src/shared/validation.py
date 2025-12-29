from typing import Any
from .timeutil import parse_iso_utc

REQUIRED = ["source", "event_type", "entity_id", "event_time", "payload"]

def validate_event(body: dict[str, Any]) -> tuple[bool, str]:
    for k in REQUIRED:
        if k not in body:
            return False, f"Missing required field: {k}"

    if not isinstance(body["payload"], (dict, list)):
        return False, "payload must be an object or array"

    try:
        parse_iso_utc(str(body["event_time"]))
    except Exception:
        return False, "event_time must be ISO-8601 (e.g. 2025-12-28T23:59:59Z)"

    return True, ""
