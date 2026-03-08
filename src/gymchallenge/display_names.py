from __future__ import annotations

from typing import Any


def build_display_name_map(participant_rows: list[dict[str, Any]]) -> dict[str, str]:
    """
    Build participant_id -> display name.

    Default display:
      Last, First

    If multiple participants share the same Last, First:
      Last, First (NN)

    Where NN comes from the numeric suffix already present in participant_id,
    e.g. smith-john-01 -> (01)
    """
    base_name_by_id: dict[str, str] = {}
    counts: dict[str, int] = {}

    for row in participant_rows:
        first = row["first_name"].strip()
        last = row["last_name"].strip()
        base = f"{last}, {first}"
        pid = row["participant_id"]

        base_name_by_id[pid] = base
        counts[base] = counts.get(base, 0) + 1

    display_map: dict[str, str] = {}

    for row in participant_rows:
        pid = row["participant_id"]
        base = base_name_by_id[pid]

        if counts[base] == 1:
            display_map[pid] = base
            continue

        suffix = pid.rsplit("-", 1)[-1]
        display_map[pid] = f"{base} ({suffix})"

    return display_map
