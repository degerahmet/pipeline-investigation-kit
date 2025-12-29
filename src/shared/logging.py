import json
import logging
import os
from datetime import datetime, timezone

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL)

def log_json(level: int, message: str, **fields):
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "msg": message,
        **fields,
    }
    logging.log(level, json.dumps(payload, separators=(",", ":")))

def info(message: str, **fields): log_json(logging.INFO, message, **fields)
def warn(message: str, **fields): log_json(logging.WARNING, message, **fields)
def error(message: str, **fields): log_json(logging.ERROR, message, **fields)
