# utils/timestamp_utils.py
from datetime import datetime, timezone

def current_utc_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')