from __future__ import annotations

from typing import Any


def find_participant_index(rows: list[dict[str, Any]], participant_id: str) -> int | None:
    for i, row in enumerate(rows):
        if row.get("participant_id") == participant_id:
            return i
    return None


def archive_participant_row(rows: list[dict[str, Any]], participant_id: str) -> bool:
    index = find_participant_index(rows, participant_id)
    if index is None:
        return False

    rows[index]["archived"] = True
    return True


def restore_participant_row(rows: list[dict[str, Any]], participant_id: str) -> bool:
    index = find_participant_index(rows, participant_id)
    if index is None:
        return False

    rows[index]["archived"] = False
    return True
