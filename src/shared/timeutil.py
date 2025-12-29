from datetime import datetime, timezone

def parse_iso_utc(s: str) -> datetime:
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def day_str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")

def hour_str(dt: datetime) -> str:
    return dt.strftime("%H")
