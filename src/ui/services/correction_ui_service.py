"""UI service functions for admin correction views."""

from __future__ import annotations

from typing import Any

from src.gymchallenge.data_paths import data_path
from src.gymchallenge.display_names import build_display_name_map
from src.gymchallenge.loaders import load_corrections
from src.gymchallenge.storage_json import load_list


def get_corrections_for_list() -> list[dict[str, Any]]:
    """Return correction rows formatted for admin list display."""
    participant_rows = load_list(data_path("participants.json"))
    display_name_map = build_display_name_map(participant_rows)

    correction_rows = load_list(data_path("corrections.json"))
    corrections = load_corrections(correction_rows)

    items: list[dict[str, Any]] = []

    for correction in corrections:
        items.append(
            {
                "correction_id": correction.correction_id,
                "cycle_id": correction.cycle_id,
                "participant_id": correction.participant_id,
                "display_name": display_name_map.get(
                    correction.participant_id,
                    correction.participant_id,
                ),
                "score_day": correction.score_day.isoformat(),
                "new_points": correction.new_points,
                "reason": correction.reason,
                "created_display": correction.created_at.isoformat(sep=" ", timespec="minutes"),
                "admin_display": correction.admin.title(),
            }
        )

    items.sort(key=lambda item: item["created_display"], reverse=True)
    return items
