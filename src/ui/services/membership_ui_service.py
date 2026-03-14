"""UI service functions for admin membership views."""

from __future__ import annotations

from typing import Any

from src.gymchallenge.data_paths import data_path
from src.gymchallenge.display_names import build_display_name_map
from src.gymchallenge.storage_json import load_list
from src.gymchallenge.loaders import load_memberships


def get_memberships_for_list() -> list[dict[str, Any]]:
    """Return membership rows formatted for admin list display."""
    participant_rows = load_list(data_path("participants.json"))
    display_name_map = build_display_name_map(participant_rows)

    membership_rows = load_list(data_path("memberships.json"))
    memberships = load_memberships(membership_rows)

    items: list[dict[str, Any]] = []

    for membership in memberships:
        joined_at = membership.joined_at.isoformat() if membership.joined_at else ""
        left_at = membership.left_at.isoformat() if membership.left_at else ""

        items.append(
            {
                "cycle_id": membership.cycle_id,
                "participant_id": membership.participant_id,
                "display_name": display_name_map.get(
                    membership.participant_id,
                    membership.participant_id,
                ),
                "status_label": "Active" if membership.active_in_cycle else "Inactive",
                "joined_display": joined_at[:10] if joined_at else "",
                "left_display": left_at[:10] if left_at else "",
                "inactive_reason": membership.inactive_reason or "",
                "inactive_effective_score_day": (
                    membership.inactive_effective_score_day.isoformat()
                    if membership.inactive_effective_score_day
                    else ""
                ),
            }
        )

    items.sort(key=lambda item: (item["cycle_id"], item["display_name"].lower()))
    return items
