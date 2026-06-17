"""Time utility functions."""
from datetime import datetime, timezone


def now_utc() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    if dt is None:
        return None
    return dt.strftime(fmt)


def iso_format(dt: datetime) -> str:
    """Format datetime to ISO 8601 string."""
    if dt is None:
        return None
    return dt.isoformat()
