from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List
from zoneinfo import ZoneInfo
from dataclasses import dataclass

from gymchallenge.models import Submission, Membership, Correction
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
    corrections: List[Correction] | None = None,
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

    # 4) Apply corrections (points only; does NOT change participated)
    if corrections:
        # latest correction wins => sort by created_at ascending and overwrite as we go
        corrections_sorted = sorted(corrections, key=lambda c: c.created_at)

        for corr in corrections_sorted:
            if corr.participant_id not in result:
                continue

            if not score_day_in_cycle(corr.score_day, cycle_start, cycle_end):
                continue

            existing = result[corr.participant_id].get(corr.score_day)
            if existing is None:
                # if the day isn't present for some reason, create an entry as non-participated
                result[corr.participant_id][corr.score_day] = DailyScore(
                    points=corr.new_points,
                    participated=False,
                )
            else:
                # override points, keep participated flag unchanged
                result[corr.participant_id][corr.score_day] = DailyScore(
                    points=corr.new_points,
                    participated=existing.participated,
                )

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

def apply_auto_inactive(
    memberships: List[Membership],
    updates: Dict[str, date],
) -> List[Membership]:
    """Apply auto-inactive updates to memberships (pure; returns a new list)."""
    new_list: List[Membership] = []

    for m in memberships:
        if m.participant_id in updates:
            new_list.append(
                Membership(
                    cycle_id=m.cycle_id,
                    participant_id=m.participant_id,
                    active_in_cycle=False,
                    joined_at=m.joined_at,
                    left_at=m.left_at,
                    inactive_reason="auto",
                    inactive_effective_score_day=updates[m.participant_id],
                )
            )
        else:
            new_list.append(m)

    return new_list


def reactivate_member(
    memberships: List[Membership],
    participant_id: str,
    effective_day: date,
    reason: str,
) -> List[Membership]:
    """Reactivate a member (pure; returns a new list). Reason is required."""
    if not reason.strip():
        raise ValueError("reason is required")

    new_list: List[Membership] = []
    for m in memberships:
        if m.participant_id == participant_id:
            new_list.append(
                Membership(
                    cycle_id=m.cycle_id,
                    participant_id=m.participant_id,
                    active_in_cycle=True,
                    joined_at=m.joined_at,
                    left_at=m.left_at,
                    inactive_reason=m.inactive_reason,  # keep historical reason
                    inactive_effective_score_day=None,  # no longer currently inactive
                )
            )
        else:
            new_list.append(m)

    return new_list

def build_leaderboard(
    memberships: List[Membership],
    daily: Dict[str, Dict[date, DailyScore]],
    from_day: date,
    to_day: date,
    tz: ZoneInfo,
    include_inactive: bool = True,
) -> List[tuple[str, int]]:
    """
    Build a leaderboard: list of (participant_id, total_points) sorted by total desc,
    then participant_id asc for deterministic ties.

    Rules:
    - If include_inactive is False: omit members where active_in_cycle is False.
    - If include_inactive is True: include everyone, but for inactive members only count
      days strictly before inactive_effective_score_day (exclude day D and beyond).
    - Active members count all days in [from_day, to_day].
    """
    # 1) Determine which members are included
    included: List[Membership] = []
    for m in memberships:
        if not include_inactive and not m.active_in_cycle:
            continue
        included.append(m)

    # 2) Sum points per included member within allowed day range
    results: List[tuple[str, int]] = []

    for m in included:
        pid = m.participant_id

        # Compute membership start day (inclusive)
        join_sd = score_day_for_timestamp(m.joined_at, tz)
        start_day = max(from_day, join_sd if join_sd is not None else from_day)

        total = 0

        # If left_at exists, determine the first score day that should be excluded.
        # Days on/after left_sd do not count.
        left_sd = None
        if m.left_at is not None:
            left_sd = score_day_for_timestamp(m.left_at, tz)

        # Track whether the member is currently inactive.
        # If inactive_effective_score_day exists, they become inactive starting on that day.
        currently_inactive = False

        d = start_day
        while d <= to_day:
            # Do not count days on/after left score day
            if left_sd is not None and d >= left_sd:
                break

            # Enter inactive state on the effective day
            if m.inactive_effective_score_day is not None and d >= m.inactive_effective_score_day:
                currently_inactive = True

            day_score = daily.get(pid, {}).get(d)

            if day_score is not None:
                if currently_inactive:
                    # Only a real participant submission reactivates and counts
                    if day_score.participated:
                        total += day_score.points
                        currently_inactive = False
                    # participated=False while inactive => skip day
                else:
                    total += day_score.points

            d += timedelta(days=1)

        results.append((pid, total))

    # 3) Sort: total desc, then participant_id asc
    results.sort(key=lambda x: (-x[1], x[0]))
    return results
