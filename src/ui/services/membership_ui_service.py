"""UI service functions for admin membership views."""

from __future__ import annotations

from typing import Any
from datetime import datetime
from zoneinfo import ZoneInfo

from src.gymchallenge.cycle_timeline import cycle_status
from src.gymchallenge.loaders import load_cycles
from src.gymchallenge.data_paths import data_path
from src.gymchallenge.display_names import build_display_name_map
from src.gymchallenge.storage_json import load_list
from src.gymchallenge.loaders import load_memberships

BERLIN = ZoneInfo("Europe/Berlin")

def get_memberships_for_list() -> list[dict[str, Any]]:
    """Return membership rows formatted for admin list display."""
    participant_rows = load_list(data_path("participants.json"))
    display_name_map = build_display_name_map(participant_rows)
    archived_map = {
        row["participant_id"]: bool(row.get("archived", False))
        for row in participant_rows
    }

    membership_rows = load_list(data_path("memberships.json"))
    memberships = load_memberships(membership_rows)

    cycle_rows = load_list(data_path("cycles.json"))
    cycles = load_cycles(cycle_rows)
    cycle_map = {cycle.cycle_id: cycle for cycle in cycles}
    now = datetime.now(BERLIN)

    items: list[dict[str, Any]] = []

    for membership in memberships:
        joined_at = membership.joined_at.isoformat() if membership.joined_at else ""
        left_at = membership.left_at.isoformat() if membership.left_at else ""
        if archived_map.get(membership.participant_id, False):
            continue

        cycle = cycle_map.get(membership.cycle_id)
        cycle_status_label = cycle_status(cycle, now, BERLIN).title() if cycle else "Unknown"

        items.append(
            {
                "cycle_id": membership.cycle_id,
                "participant_id": membership.participant_id,
                "display_name": display_name_map.get(
                    membership.participant_id,
                    membership.participant_id,
                ),
                "status_label": "Active" if membership.active_in_cycle else "Inactive",
                "cycle_status": cycle_status_label,
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

def filter_memberships_for_view(
    memberships: list[dict[str, str]],
    filter_value: str,
) -> list[dict[str, str]]:
    """Filter membership rows for admin display."""
    if not filter_value or filter_value == "all":
        return memberships

    if filter_value == "active":
        return [m for m in memberships if m.get("cycle_status") == "Active"]

    if filter_value == "planned":
        return [m for m in memberships if m.get("cycle_status") == "Planned"]

    if filter_value == "closed":
        return [m for m in memberships if m.get("cycle_status") == "Closed"]

    return [m for m in memberships if m.get("cycle_id") == filter_value]
