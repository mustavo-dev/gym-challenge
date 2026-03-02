from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from gymchallenge.scoring_time import score_day_for_timestamp


def score_day_in_cycle(score_day: date, cycle_start: date, cycle_end: date) -> bool:
    """
    Return True if score_day is within the cycle boundaries (inclusive).
    """
    return cycle_start <= score_day <= cycle_end


def cycle_accepts_timestamp(
    dt: datetime,
    tz: ZoneInfo,
    cycle_start: date,
    cycle_end: date,
) -> tuple[bool, date | None]:
    """
    Determine whether the cycle accepts this timestamp.

    Return:
      (accepted, score_day)

    Rules:
    - Use score_day_for_timestamp(dt, tz)
      - If it returns None => invalid check-in window => (False, None)
    - If score_day is outside [cycle_start, cycle_end] => (False, score_day)
    - Else => (True, score_day)
    """
    score_day = score_day_for_timestamp(dt, tz)
    if score_day is None:
        return (False, None)

    if not score_day_in_cycle(score_day, cycle_start, cycle_end):
        return (False, score_day)

    return (True, score_day)
