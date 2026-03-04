from __future__ import annotations

from typing import Any


def has_membership(rows: list[dict[str, Any]], cycle_id: str, participant_id: str) -> bool:
    for r in rows:
        if r.get("cycle_id") == cycle_id and r.get("participant_id") == participant_id:
            return True
    return False
