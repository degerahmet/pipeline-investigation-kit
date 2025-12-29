import hashlib
import json
from typing import Any

def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def payload_hash(payload: Any) -> str:
    return sha256_hex(canonical_json_bytes(payload))

def stable_event_id(source: str, event_type: str, entity_id: str, event_time_iso: str, payload_sha: str, idempotency_key: str | None) -> str:
    if idempotency_key:
        base = f"IDEMPOTENCY|{source}|{event_type}|{entity_id}|{idempotency_key}"
    else:
        base = f"HASH|{source}|{event_type}|{entity_id}|{event_time_iso}|{payload_sha}"
    return sha256_hex(base.encode("utf-8"))
