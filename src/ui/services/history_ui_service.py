"""UI service functions for admin history views."""
from __future__ import annotations

from src.gymchallenge.data_paths import data_path
from src.gymchallenge.display_names import build_display_name_map
from src.gymchallenge.loaders import load_corrections, load_system_events
from src.gymchallenge.storage_json import load_list


def get_history_for_list() -> list[dict[str, str]]:
    """Return admin history rows for display."""
    correction_rows = load_list(data_path("corrections.json"))
    corrections = load_corrections(correction_rows)

    system_event_rows = load_list(data_path("system_events.json"))
    system_events = load_system_events(system_event_rows)

    participant_rows = load_list(data_path("participants.json"))
    display_name_map = build_display_name_map(participant_rows)

    items: list[dict[str, str]] = []

    for correction in corrections:
        admin_display = correction.admin.title() if correction.admin else "Admin"

        items.append(
            {
                "entry_type": "Correction",
                "entry_type_key": "correction",
                "participant_id": correction.participant_id,
                "display_name": display_name_map.get(
                    correction.participant_id,
                    correction.participant_id,
                ),
                "event_label": f"Correction to {correction.new_points} points",
                "date_label": correction.created_at.strftime("%Y-%m-%d %H:%M%z"),
                "date_raw": correction.created_at.isoformat(),
                "detail_1": f"Score Day: {correction.score_day.isoformat()}",
                "detail_2": f"Reason: {correction.reason}",
                "detail_3": f"Admin: {admin_display}",
            }
        )

    for event in system_events:
        participant_id = str(event.get("participant_id") or "")
        event_type = str(event.get("event_type") or "")
        actor = str(event.get("actor") or "system").title()
        created_at = event["created_at"]

        if event_type == "participant_archived":
            entry_type = "System"
            event_label = "Participant archived"
        elif event_type == "participant_restored":
            entry_type = "System"
            event_label = "Participant restored"
        elif event_type == "dataset_reset":
            entry_type = "System"
            event_label = "Dataset reset"
        else:
            entry_type = "System"
            event_label = event_type.replace("_", " ").title()

        items.append(
            {
                "entry_type": entry_type,
                "entry_type_key": "system",
                "participant_id": participant_id,
                "display_name": display_name_map.get(participant_id, participant_id) if participant_id else "System",
                "event_label": event_label,
                "date_label": created_at.strftime("%Y-%m-%d %H:%M%z"),
                "date_raw": created_at.isoformat(),
                "detail_1": f"Reason: {event.get('reason', '')}",
                "detail_2": f"Actor: {actor}",
                "detail_3": "",
            }
        )

    items.sort(key=lambda row: row["date_raw"], reverse=True)
    return items


def filter_and_sort_history_for_view(
    history_entries: list[dict[str, str]],
    entry_type: str,
    participant_id: str,
    sort_value: str,
) -> list[dict[str, str]]:
    """Filter and sort history rows for admin display."""
    rows = history_entries

    if entry_type and entry_type != "all":
        rows = [row for row in rows if row.get("entry_type_key") == entry_type]

    if participant_id:
        rows = [row for row in rows if row.get("participant_id") == participant_id]

    if sort_value == "oldest":
        rows = sorted(rows, key=lambda row: row.get("date_raw", ""))
    else:
        rows = sorted(rows, key=lambda row: row.get("date_raw", ""), reverse=True)

    return rows
