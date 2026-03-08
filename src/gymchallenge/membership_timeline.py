from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable

from zoneinfo import ZoneInfo

from gymchallenge.models import Membership, MembershipEvent
from gymchallenge.scoring_time import score_day_for_timestamp


INACTIVE_EVENT_TYPES = {"auto_inactive", "manual_inactive"}
ACTIVE_EVENT_TYPES = {"manual_reactivate", "auto_reactivate_submission"}


def build_active_day_map(
    membership: Membership,
    events: list[MembershipEvent],
    from_day: date,
    to_day: date,
    tz: ZoneInfo,
) -> dict[date, bool]:
    """
    Return a mapping of score_day -> whether the member is active on that day.

    Rules:
    - Member becomes eligible starting on joined_at score-day.
    - Member stops being eligible on/after left_at score-day.
    - Inactive events make them inactive on/after effective_score_day.
    - Reactivate events make them active on/after effective_score_day.
    - If multiple events occur, later effective_score_day transitions apply as the loop advances.
    """
    joined_sd = score_day_for_timestamp(membership.joined_at, tz)
    if joined_sd is None:
        joined_sd = from_day

    left_sd = None
    if membership.left_at is not None:
        left_sd = score_day_for_timestamp(membership.left_at, tz)

    relevant_events = sorted(events, key=lambda e: (e.effective_score_day, e.created_at))

    result: dict[date, bool] = {}
    current_active = membership.active_in_cycle

    # Baseline should be active from joined day unless an event changes it later.
    # For MVP timeline reconstruction, start active if the member has joined and not left.
    current_active = True

    event_idx = 0
    d = from_day

    while d <= to_day:
        # Before joined day => inactive
        if d < joined_sd:
            result[d] = False
            d += timedelta(days=1)
            continue

        # On/after left day => inactive forever
        if left_sd is not None and d >= left_sd:
            result[d] = False
            d += timedelta(days=1)
            continue

        # Apply all events effective on this day
        while event_idx < len(relevant_events) and relevant_events[event_idx].effective_score_day == d:
            evt = relevant_events[event_idx]
            if evt.event_type in INACTIVE_EVENT_TYPES:
                current_active = False
            elif evt.event_type in ACTIVE_EVENT_TYPES:
                current_active = True
            event_idx += 1

        result[d] = current_active
        d += timedelta(days=1)

    return result
