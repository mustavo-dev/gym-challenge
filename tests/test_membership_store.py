from __future__ import annotations

from typing import Any


def find_membership_index(rows: list[dict[str, Any]], cycle_id: str, participant_id: str) -> int | None:
    for i, r in enumerate(rows):
        if r.get("cycle_id") == cycle_id and r.get("participant_id") == participant_id:
            return i
    return None
