from __future__ import annotations

from datetime import datetime

from src.gymchallenge.cycle_timeline import cycle_status
from src.gymchallenge.data_paths import data_path
from src.gymchallenge.display_names import build_display_name_map
from src.gymchallenge.loaders import load_cycles, load_memberships
from src.gymchallenge.storage_json import load_list
from src.ui.config import get_ui_timezone

def get_submit_page_context() -> dict:
    """Return active-cycle submit context for the participant submit page."""
    cycle_rows = load_list(data_path("cycles.json"))
    membership_rows = load_list(data_path("memberships.json"))
    participant_rows = load_list(data_path("participants.json"))

    archived_map = {
        row["participant_id"]: bool(row.get("archived", False))
        for row in participant_rows
    }

    cycles = load_cycles(cycle_rows)
    memberships = load_memberships(membership_rows)
    display_name_map = build_display_name_map(participant_rows)
    
    ui_tz = get_ui_timezone()
    now = datetime.now(ui_tz)

    active_cycles = [
        cycle
        for cycle in cycles
        if cycle_status(cycle, now, ui_tz) == "active"
    ]

    if not active_cycles:
        return {
            "active_cycle": None,
            "participant_choices": [],
            "submit_enabled": False,
            "submit_message": "No active cycle is currently accepting submissions.",
        }

    active_cycle = active_cycles[0]

    cycle_memberships = [
        membership
        for membership in memberships
        if membership.cycle_id == active_cycle.cycle_id
    ]

    participant_choices = []
    seen_ids = set()

    for membership in cycle_memberships:
        participant_id = membership.participant_id
        if participant_id in seen_ids:
            continue

        if archived_map.get(participant_id, False):
            continue

        participant_choices.append(
            {
                "participant_id": participant_id,
                "display_name": display_name_map.get(participant_id, participant_id),
            }
        )
        seen_ids.add(participant_id)

    participant_choices.sort(key=lambda row: row["display_name"].lower())

    return {
        "active_cycle": active_cycle,
        "participant_choices": participant_choices,
        "submit_enabled": True,
        "submit_message": "",
    }
