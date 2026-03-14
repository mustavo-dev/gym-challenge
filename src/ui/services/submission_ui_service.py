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

    submission_rows = load_list(data_path("submissions.json"))
    submissions = load_submissions(submission_rows)

    items: list[dict[str, Any]] = []

    for submission in submissions:
        items.append(
            {
                "submission_id": submission.submission_id,
                "cycle_id": submission.cycle_id,
                "participant_id": submission.participant_id,
                "display_name": display_name_map.get(
                    submission.participant_id,
                    submission.participant_id,
                ),
                "submitted_display": submission.submitted_at.isoformat(sep=" ", timespec="minutes"),
                "points": submission.points,
                "source": submission.source,
            }
        )

    items.sort(key=lambda item: item["submitted_display"], reverse=True)
    return items
