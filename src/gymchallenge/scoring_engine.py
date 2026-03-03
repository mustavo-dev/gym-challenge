from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List
from zoneinfo import ZoneInfo

from gymchallenge.models import Submission
from gymchallenge.scoring_time import score_day_for_timestamp
from gymchallenge.cycle_rules import score_day_in_cycle


def _date_range(start: date, end: date) -> List[date]:
    days = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def compute_daily_scores(
    participant_ids: List[str],
    submissions: List[Submission],
    tz: ZoneInfo,
    cycle_start: date,
    cycle_end: date,
    missing_points: int,
) -> Dict[str, Dict[date, int]]:
    """
    Return:
      {
        participant_id: {
            score_day: points,
            ...
        }
      }
    """
    # 1) Build list of score days for the cycle
    score_days = _date_range(cycle_start, cycle_end)

    # 2) Initialize result grid: everyone starts with missing_points each day
    result: Dict[str, Dict[date, int]] = {}
    for pid in participant_ids:
        result[pid] = {}
        for d in score_days:
            result[pid][d] = missing_points

    # 3) Overlay valid submissions onto the grid
    for sub in submissions:
        # ignore submissions for participants we aren't scoring
        if sub.participant_id not in result:
            continue

        sd = score_day_for_timestamp(sub.submitted_at, tz)
        # ignore invalid window timestamps
        if sd is None:
            continue

        # ignore submissions outside the cycle score-day range
        if not score_day_in_cycle(sd, cycle_start, cycle_end):
            continue

        # set the score for that day
        result[sub.participant_id][sd] = sub.points

    return result
