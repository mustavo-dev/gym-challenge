"""UI service functions for admin history views."""

from __future__ import annotations

from typing import Any

from src.gymchallenge.data_paths import data_path
from src.gymchallenge.display_names import build_display_name_map
from src.gymchallenge.loaders import load_corrections, load_membership_events
from src.gymchallenge.storage_json import load_list


def get_history_for_list() -> list[dict[str, Any]]:
    """Return a unified admin history list for corrections and membership events."""
    participant_rows = load_list(data_path("participants.json"))
    display_name_map = build_display_name_map(participant_rows)

    items: list[dict[str, Any]] = []

    correction_rows = load_list(data_path("corrections.json"))
    corrections = load_corrections(correction_rows)

    for correction in corrections:
        items.append(
            {
                "entry_type": "Correction",
                "display_name": display_name_map.get(
                    correction.participant_id,
                    correction.participant_id,
                ),
                "event_label": f"Correction to {correction.new_points} points",
                "date_label": correction.created_at.isoformat(sep=" ", timespec="minutes"),
                "detail_1": f"Score Day: {correction.score_day.isoformat()}",
                "detail_2": f"Reason: {correction.reason}",
                "detail_3": f"Admin: {correction.admin.title()}",
            }
        )

    membership_event_rows = load_list(data_path("membership_events.json"))
    membership_events = load_membership_events(membership_event_rows)

    for event in membership_events:
        items.append(
            {
                "entry_type": "Membership Event",
                "display_name": display_name_map.get(
                    event.participant_id,
                    event.participant_id,
                ),
                "event_label": event.event_type.replace("_", " ").title(),
                "date_label": event.created_at.isoformat(sep=" ", timespec="minutes"),
                "detail_1": f"Effective Score Day: {event.effective_score_day.isoformat()}",
                "detail_2": f"Reason: {event.reason}",
                "detail_3": f"Actor: {event.actor.title()}",
            }
        )

    items.sort(key=lambda item: item["date_label"], reverse=True)
    return items
