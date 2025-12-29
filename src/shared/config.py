import os

def env(name: str, default: str | None = None) -> str:
    v = os.getenv(name, default)
    if v is None:
        raise RuntimeError(f"Missing required env var: {name}")
    return v

# Lazy resolution (runtime'da kullanılır)
RAW_BUCKET = os.getenv("RAW_BUCKET")
EVENTS_TABLE = os.getenv("EVENTS_TABLE")
DEDUPE_TABLE = os.getenv("DEDUPE_TABLE")
AGG_TABLE = os.getenv("AGG_TABLE")
REPLAY_QUEUE_URL = os.getenv("REPLAY_QUEUE_URL")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def is_dry_run() -> bool:
    return os.getenv("DRY_RUN", "false").lower() == "true"
