from __future__ import annotations

from datetime import date
from typing import Dict

from .models import Membership
from .scoring_engine import DailyScore


def detect_auto_reactivate(
    memberships: list[Membership],
    daily: Dict[str, Dict[date, DailyScore]],
    from_day: date,
    to_day: date,
) -> dict[str, date]:
    """
    Detect earliest valid submission day that should auto-reactivate an inactive member.

    Rules:
    - member must currently be inactive
    - member must have inactive_effective_score_day
    - earliest day d where:
        d >= inactive_effective_score_day
        and daily[participant_id][d].participated is True
      becomes the reactivation day
    """
    updates: dict[str, date] = {}

    for m in memberships:
        if m.active_in_cycle:
            continue
        if m.inactive_effective_score_day is None:
            continue

        per_day = daily.get(m.participant_id, {})
        d = max(from_day, m.inactive_effective_score_day)

        while d <= to_day:
            day_score = per_day.get(d)
            if day_score is not None and day_score.participated:
                updates[m.participant_id] = d
                break
            d = date.fromordinal(d.toordinal() + 1)

    return updates
