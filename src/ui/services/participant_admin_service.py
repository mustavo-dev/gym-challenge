"""UI service functions for admin participant views."""

from __future__ import annotations

from typing import Any

from src.gymchallenge.data_paths import data_path
from src.gymchallenge.display_names import build_display_name_map
from src.gymchallenge.storage_json import load_list


def get_participants_for_list() -> list[dict[str, Any]]:
    """Return participant rows formatted for admin list display."""
    participant_rows = load_list(data_path("participants.json"))
    display_name_map = build_display_name_map(participant_rows)

    participants: list[dict[str, Any]] = []

    for row in participant_rows:
        participant_id = row["participant_id"]
        created_at = row.get("created_at", "")
        created_display = created_at[:10] if created_at else ""

        participants.append(
            {
                "participant_id": participant_id,
                "display_name": display_name_map.get(participant_id, participant_id),
                "status_label": "Active" if bool(row.get("active", True)) else "Inactive",
                "created_display": created_display,
            }
        )

    participants.sort(key=lambda p: p["display_name"].lower())
    return participants
