from __future__ import annotations

from typing import Any


def has_matching_event(
    rows: list[dict[str, Any]],
    cycle_id: str,
    participant_id: str,
    event_type: str,
    effective_score_day: str,
) -> bool:
    for r in rows:
        if (
            r.get("cycle_id") == cycle_id
            and r.get("participant_id") == participant_id
            and r.get("event_type") == event_type
            and r.get("effective_score_day") == effective_score_day
        ):
            return True
    return False
