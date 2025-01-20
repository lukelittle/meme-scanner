"""
Time-related utility functions for the meme scanner application.
"""

from datetime import datetime, timezone
import pytz

def format_timestamp(unix_timestamp: int | None) -> str:
    """
    Convert a Unix timestamp to a formatted Eastern Time string.

    Args:
        unix_timestamp: Unix timestamp in seconds, or None

    Returns:
        str: Formatted datetime string in ET timezone (e.g., "2023-12-25 02:30:45 PM ET")
              Returns "N/A" if timestamp is None
    """
    if not unix_timestamp:
        return "N/A"
    utc_time = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    eastern = pytz.timezone('America/New_York')
    eastern_time = utc_time.astimezone(eastern)
    return eastern_time.strftime("%Y-%m-%d %I:%M:%S %p ET")

def get_current_time() -> str:
    """
    Get the current time in Eastern Time zone.

    Returns:
        str: Current time formatted as "YYYY-MM-DD HH:MM:SS AM/PM ET"
    """
    eastern = pytz.timezone('America/New_York')
    return datetime.now(eastern).strftime("%Y-%m-%d %I:%M:%S %p ET")
