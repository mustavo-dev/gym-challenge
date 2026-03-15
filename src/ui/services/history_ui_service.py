"""UI service functions for admin history views."""
from __future__ import annotations

from src.gymchallenge.data_paths import data_path
from src.gymchallenge.display_names import build_display_name_map
from src.gymchallenge.loaders import load_corrections
from src.gymchallenge.storage_json import load_list


def get_history_for_list() -> list[dict[str, str]]:
    """Return admin history rows for display."""
    correction_rows = load_list(data_path("corrections.json"))
    corrections = load_corrections(correction_rows)

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
