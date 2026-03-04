from __future__ import annotations

from typing import Any

from gymchallenge.storage_json import load_list, save_list


def append_row(path: str, row: dict[str, Any]) -> None:
    rows = load_list(path)
    rows.append(row)
    save_list(path, rows)
