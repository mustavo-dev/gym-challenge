from __future__ import annotations

from datetime import datetime, date
from typing import Any

from gymchallenge.membership_event_store import has_matching_event
from gymchallenge.membership_event_ops import append_membership_event


def append_missing_auto_inactive_events(
    path: str,
    existing_rows: list[dict[str, Any]],
    cycle_id: str,
    updates: dict[str, date],
    created_at: datetime,
) -> list[dict[str, Any]]:
    """
    For each participant_id -> effective_score_day in updates,
    append an auto_inactive event only if an identical event is not already present.
    Returns the list of newly written event rows.
    """
    written: list[dict[str, Any]] = []

    for participant_id, effective_day in updates.items():
        effective_day_str = effective_day.isoformat()

        if has_matching_event(
            existing_rows,
            cycle_id=cycle_id,
            participant_id=participant_id,
            event_type="auto_inactive",
            effective_score_day=effective_day_str,
        ):
            continue

        row = append_membership_event(
            path=path,
            cycle_id=cycle_id,
            participant_id=participant_id,
            event_type="auto_inactive",
            effective_score_day=effective_day,
            reason="4 consecutive missed days",
            created_at=created_at,
            actor="system",
        )
        written.append(row)
        existing_rows.append(row)

    return written
