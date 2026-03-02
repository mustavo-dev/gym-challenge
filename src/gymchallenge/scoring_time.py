from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo


def _to_tz(dt: datetime, tz: ZoneInfo) -> datetime:
    """
    Return dt converted to tz.

    Requirements:
    - dt must be timezone-aware (dt.tzinfo is not None)
    - Result must be tz-aware in the target timezone
    """
    if dt.tzinfo is None:
        raise ValueError("dt must be timezone-aware")
    return dt.astimezone(tz)


def is_within_checkin_window(dt: datetime, tz: ZoneInfo) -> bool:
    """
    Check-in window is:
      - from 20:00 (inclusive) to 12:00 next day (exclusive) in tz.

    That means valid times are:
      - 20:00–23:59:59...
      - 00:00–11:59:59...

    Invalid times are:
      - 12:00–19:59:59...

    Return True if dt is within the window, else False.
    """
    local = _to_tz(dt, tz)
    t = local.timetz()

    # Valid if time >= 20:00 OR time < 12:00
    return (t >= time(20, 0, tzinfo=local.tzinfo)) or (t < time(12, 0, tzinfo=local.tzinfo))


def score_day_for_timestamp(dt: datetime, tz: ZoneInfo) -> date | None:
    """
    Map a timestamp to a "score day" label (date).

    Rule:
    - If dt is outside the check-in window (12:00–19:59), return None.
    - If dt local time is 20:00–23:59 => score_day = local date of dt
    - If dt local time is 00:00–11:59 => score_day = local date of dt minus 1 day

    Examples (Berlin):
    - 2026-03-02 20:00 => score_day 2026-03-02
    - 2026-03-03 01:00 => score_day 2026-03-02
    - 2026-03-03 12:00 => None
    """
    if not is_within_checkin_window(dt, tz):
        return None

    local = _to_tz(dt, tz)
    local_time = local.timetz()

    if local_time >= time(20, 0, tzinfo=local.tzinfo):
        return local.date()

    # local_time must be < 12:00 here
    return (local.date() - timedelta(days=1))
