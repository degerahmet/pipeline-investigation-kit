from datetime import timezone
from src.shared.timeutil import parse_iso_utc, iso_utc, day_str, hour_str

def test_parse_iso_utc_accepts_z():
    dt = parse_iso_utc("2025-12-28T23:59:59Z")
    assert dt.tzinfo == timezone.utc
    assert iso_utc(dt) == "2025-12-28T23:59:59Z"

def test_day_and_hour():
    dt = parse_iso_utc("2025-12-28T03:04:05Z")
    assert day_str(dt) == "2025-12-28"
    assert hour_str(dt) == "03"
