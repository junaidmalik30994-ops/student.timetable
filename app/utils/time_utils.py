from datetime import datetime, timezone, timedelta

# Define Indian Standard Time (IST = UTC+05:30, Asia/Kolkata)
IST = timezone(timedelta(hours=5, minutes=30))
try:
    from zoneinfo import ZoneInfo
    try:
        IST = ZoneInfo("Asia/Kolkata")
    except Exception:
        IST = timezone(timedelta(hours=5, minutes=30))
except ImportError:
    IST = timezone(timedelta(hours=5, minutes=30))


def get_ist_now():
    """Return current timezone-aware datetime in Indian Standard Time (IST)."""
    return datetime.now(IST)


def get_ist_now_iso():
    """Return current IST datetime as an ISO-8601 string."""
    return get_ist_now().isoformat()


def format_registration_time(val):
    """
    Format student registration timestamp into IST string format:
    'DD Month YYYY, hh:mm AM/PM' (e.g. '11 September 2026, 02:30 PM').
    Supports legacy UTC ISO strings, ISO strings with offsets, and datetime objects.
    """
    if not val:
        return 'N/A'

    dt = None
    if isinstance(val, datetime):
        dt = val
    elif isinstance(val, str):
        val_str = val.strip()
        if val_str:
            try:
                # Handle ISO format string with or without Z
                dt = datetime.fromisoformat(val_str.replace('Z', '+00:00'))
            except Exception:
                pass

    if dt is not None:
        # If naive (no timezone information attached), assume it was saved in UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # Convert to Asia/Kolkata (IST)
        dt_ist = dt.astimezone(IST)
        return dt_ist.strftime('%d %B %Y, %I:%M %p')

    return str(val)
