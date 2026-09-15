from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
try:
    from zoneinfo import ZoneInfo
    try:
        IST = ZoneInfo("Asia/Kolkata")
    except Exception:
        IST = timezone(timedelta(hours=5, minutes=30))
except ImportError:
    IST = timezone(timedelta(hours=5, minutes=30))

def format_registration_time(val):
    if not val:
        return 'N/A'
    
    dt = None
    if isinstance(val, datetime):
        dt = val
    elif isinstance(val, str):
        try:
            # Handle ISO format strings (with or without 'Z' or offset)
            dt = datetime.fromisoformat(val.replace('Z', '+00:00'))
        except Exception:
            pass

    if dt is not None:
        # If timezone-naive, treat as UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # Convert to Asia/Kolkata (IST = UTC+5:30)
        dt_ist = dt.astimezone(IST)
        return dt_ist.strftime('%d %B %Y, %I:%M %p')
    
    return str(val)

# Test 1: Current IST time creation
now_ist = datetime.now(IST)
iso_ist = now_ist.isoformat()
print("New IST creation:", iso_ist)
print("New IST formatted:", format_registration_time(iso_ist))

# Test 2: Existing legacy UTC ISO string without offset (e.g. 09:00 UTC = 14:30 IST)
utc_str_naive = "2026-09-11T09:00:00"
print("Legacy UTC formatted:", format_registration_time(utc_str_naive))

# Test 3: Existing legacy UTC ISO string with 'Z'
utc_str_z = "2026-09-11T09:00:00Z"
print("Legacy UTC Z formatted:", format_registration_time(utc_str_z))
