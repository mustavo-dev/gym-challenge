from __future__ import annotations

from datetime import date, datetime
from typing import Any

from gymchallenge.id_ops import new_membership_event_id
from gymchallenge.storage_ops import append_row


def append_membership_event(
    path: str,
    cycle_id: str,
    participant_id: str,
    event_type: str,
    effective_score_day: date,
    reason: str,
    created_at: datetime,
    actor: str,
) -> dict[str, Any]:
    row = {
        "event_id": new_membership_event_id(),
        "cycle_id": cycle_id,
        "participant_id": participant_id,
        "event_type": event_type,
        "effective_score_day": effective_score_day.isoformat(),
        "reason": reason,
        "created_at": created_at.isoformat(),
        "actor": actor,
    }

    append_row(path, row)
    return row
