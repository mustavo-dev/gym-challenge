from __future__ import annotations

import json
import os
from typing import Any


def load_list(path: str) -> list[dict[str, Any]]:
    """
    Load a JSON file containing a top-level list of objects.

    - If the file does not exist: returns []
    - If the file exists but is empty/invalid: raises ValueError
    """
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Expected JSON list in {path}, got {type(data).__name__}")

    # Ensure each element is a dict (MVP assumption)
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"Expected list of objects in {path}; item {i} is {type(item).__name__}")

    return data


def save_list(path: str, rows: list[dict[str, Any]]) -> None:
    """
    Save a list of dict rows to JSON.

    Writes atomically by writing to a temporary file then replacing.
    Creates parent directory if needed.
    """
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
        f.write("\n")

    os.replace(tmp_path, path)
