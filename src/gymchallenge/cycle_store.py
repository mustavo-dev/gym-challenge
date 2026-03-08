from __future__ import annotations

from typing import Any


def find_cycle_row(rows: list[dict[str, Any]], cycle_id: str) -> dict[str, Any] | None:
    for row in rows:
        if row.get("cycle_id") == cycle_id:
            return row
    return None
