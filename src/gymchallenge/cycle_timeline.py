from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from .models import Cycle


def cycle_window_start(cycle: Cycle, tz: ZoneInfo) -> datetime:
    """
    A cycle becomes active at 20:00 configured gym timezone on start_day.
    """
    return datetime.combine(cycle.start_day, time(20, 0), tzinfo=tz)


def cycle_window_end(cycle: Cycle, tz: ZoneInfo) -> datetime:
    """
    A cycle becomes closed at 12:00 configured gym timezone on the day after end_day.
    """
    end_plus_one = cycle.end_day + timedelta(days=1)
    return datetime.combine(end_plus_one, time(12, 0), tzinfo=tz)


def cycle_status(cycle: Cycle, now: datetime, tz: ZoneInfo) -> str:
    """
    Derived cycle status:
    - planned: now < active window start
    - active: start <= now < end
    - closed: now >= active window end
    """
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")

    local_now = now.astimezone(tz)
    start_dt = cycle_window_start(cycle, tz)
    end_dt = cycle_window_end(cycle, tz)

    if local_now < start_dt:
        return "planned"
    if local_now >= end_dt:
        return "closed"
    return "active"


def windows_overlap(start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime) -> bool:
    """
    Half-open interval overlap:
    [start_a, end_a) overlaps [start_b, end_b)
    """
    return start_a < end_b and start_b < end_a


def cycle_overlaps_existing(new_cycle: Cycle, existing_cycles: list[Cycle], tz: ZoneInfo) -> bool:
    """
    Returns True if the new cycle's active window overlaps any existing cycle's active window.
    """
    new_start = cycle_window_start(new_cycle, tz)
    new_end = cycle_window_end(new_cycle, tz)

    for cycle in existing_cycles:
        existing_start = cycle_window_start(cycle, tz)
        existing_end = cycle_window_end(cycle, tz)

        if windows_overlap(new_start, new_end, existing_start, existing_end):
            return True

    return False
