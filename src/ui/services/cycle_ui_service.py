"""UI service functions for admin cycle views."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from src.gymchallenge.cycle_timeline import cycle_status
from src.gymchallenge.data_paths import data_path
from src.gymchallenge.loaders import load_cycles
from src.gymchallenge.storage_json import load_list
from src.ui.config import get_ui_timezone

def get_cycles_for_list() -> list[dict[str, Any]]:
    """Return cycle rows formatted for admin list display."""
    cycle_rows = load_list(data_path("cycles.json"))
    cycles = load_cycles(cycle_rows)
    ui_tz = get_ui_timezone()
    now = datetime.now(ui_tz)

    items: list[dict[str, Any]] = []

    for cycle in cycles:
        items.append(
            {
                "cycle_id": cycle.cycle_id,
                "name": cycle.name,
                "start_day": cycle.start_day.isoformat(),
                "end_day": cycle.end_day.isoformat(),
                "created_display": cycle.created_at.date().isoformat(),
                "status_label": cycle_status(cycle, now, ui_tz).title(),
            }
        )

    items.sort(key=lambda item: item["start_day"])
    return items

def find_cycle_id_for_score_day(score_day: date) -> str | None:
    """Return the cycle_id whose start/end day contains the given score day."""
    cycle_rows = load_list(data_path("cycles.json"))
    cycles = load_cycles(cycle_rows)

    matches = [
        cycle
        for cycle in cycles
        if cycle.start_day <= score_day <= cycle.end_day
    ]

    if len(matches) == 1:
        return matches[0].cycle_id

    return None
