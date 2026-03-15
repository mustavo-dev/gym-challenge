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

def get_participant_choices() -> list[dict[str, str]]:
    """Return participants formatted for admin dropdown choices."""
    participant_rows = load_list(data_path("participants.json"))
    display_name_map = build_display_name_map(participant_rows)

    items: list[dict[str, str]] = []

    for row in participant_rows:
        participant_id = row["participant_id"]
        items.append(
            {
                "participant_id": participant_id,
                "display_name": display_name_map.get(participant_id, participant_id),
            }
        )

    items.sort(key=lambda item: item["display_name"].lower())
    return items

def filter_participants_for_view(
    participants: list[dict[str, str]],
    search_value: str,
) -> list[dict[str, str]]:
    """Filter participant rows by display name."""
    if not search_value:
        return participants

    term = search_value.lower()

    return [
        row
        for row in participants
        if term in row.get("display_name", "").lower()
    ]
