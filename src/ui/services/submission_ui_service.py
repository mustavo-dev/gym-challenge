"""UI service functions for admin submission views."""

from __future__ import annotations

from typing import Any

from src.gymchallenge.data_paths import data_path
from src.gymchallenge.display_names import build_display_name_map
from src.gymchallenge.loaders import load_submissions
from src.gymchallenge.storage_json import load_list


def get_submissions_for_list() -> list[dict[str, Any]]:
    """Return submission rows formatted for admin list display."""
    participant_rows = load_list(data_path("participants.json"))
    display_name_map = build_display_name_map(participant_rows)

    name_counts: dict[str, int] = {}
    for display_name in display_name_map.values():
        name_counts[display_name] = name_counts.get(display_name, 0) + 1

    submission_rows = load_list(data_path("submissions.json"))
    submissions = load_submissions(submission_rows)

    items: list[dict[str, Any]] = []

    for submission in submissions:
        display_name = display_name_map.get(
            submission.participant_id,
            submission.participant_id,
        )

        items.append(
            {
                "submission_id": submission.submission_id,
                "participant_id": submission.participant_id,
                "display_name": display_name,
                "show_participant_id": name_counts.get(display_name, 0) > 1,
                "submitted_display": submission.submitted_at.isoformat(sep=" ", timespec="minutes"),
                "submitted_at_faw": submission.submitted_at.isoformat(),
                "points": submission.points,
                "source": submission.source,
            }
        )

    items.sort(key=lambda item: item["submitted_display"], reverse=True)
    return items

def filter_and_sort_submissions_for_view(
    submissions: list[dict[str, str]],
    participant_id: str,
    points_value: str,
    sort_value: str,
) -> list[dict[str, str]]:
    """Filter and sort submission rows for admin display."""
    rows = submissions

    if participant_id:
        rows = [row for row in rows if row.get("participant_id") == participant_id]

    if points_value != "":
        try:
            points_int = int(points_value)
            rows = [row for row in rows if row.get("points") == points_int]
        except ValueError:
            pass

    if sort_value == "oldest":
        rows = sorted(rows, key=lambda row: row.get("submitted_at_raw", ""))
    elif sort_value == "highest_points":
        rows = sorted(rows, key=lambda row: row.get("points", 0), reverse=True)
    elif sort_value == "lowest_points":
        rows = sorted(rows, key=lambda row: row.get("points", 0))
    elif sort_value == "name_az":
        rows = sorted(rows, key=lambda row: row.get("display_name", "").lower())
    else:
        # default newest first
        rows = sorted(rows, key=lambda row: row.get("submitted_at_raw", ""), reverse=True)

    return rows
