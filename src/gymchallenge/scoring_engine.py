from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List
from zoneinfo import ZoneInfo
from dataclasses import dataclass

from gymchallenge.models import Submission
from gymchallenge.scoring_time import score_day_for_timestamp
from gymchallenge.cycle_rules import score_day_in_cycle

@dataclass(frozen=True)
class DailyScore:
    points: int
    participated: bool

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
) -> Dict[str, Dict[date, DailyScore]]:
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
    result: Dict[str, Dict[date, DailyScore]] = {}
    for pid in participant_ids:
        result[pid] = {}
        for d in score_days:
            result[pid][d] = DailyScore(points=missing_points, participated=False)

    # 3) Overlay valid submissions onto the grid
    # Sort submissions by submitted_at ascending so earliest appear first.
    submissions_sorted = sorted(submissions, key=lambda s: s.submitted_at)

    # Track which (participant_id, score_day) pairs we've already applied from submissions.
    seen: set[tuple[str, date]] = set()

    for sub in submissions_sorted:
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

        key = (sub.participant_id, sd)
        if key in seen:
            # we've already applied an earlier submission for this participant+day
            continue

        # apply the earliest submission for this participant+score_day
        result[sub.participant_id][sd] = DailyScore(points=sub.points, participated=True)
        seen.add(key)

    return result

def detect_auto_inactive(
    daily: Dict[str, Dict[date, DailyScore]],
    cycle_start: date,
    cycle_end: date,
    streak_required: int = 4,
) -> Dict[str, date]:
    """
    Return mapping of participant_id -> inactive_effective_score_day.
    A participant becomes inactive after `streak_required` consecutive days with participated=False.
    Inactivity becomes effective the next score day (the day after the streak completes).
    """
    updates: Dict[str, date] = {}

    score_days = _date_range(cycle_start, cycle_end)

    for pid, per_day in daily.items():
        streak = 0

        for d in score_days:
            # If the day is missing from the dict, treat as not participated
            day_score = per_day.get(d, DailyScore(points=0, participated=False))

            if day_score.participated:
                streak = 0
                continue

            streak += 1

            if streak >= streak_required:
                updates[pid] = d + timedelta(days=1)
                break  # stop scanning this participant after first trigger

    return updates
