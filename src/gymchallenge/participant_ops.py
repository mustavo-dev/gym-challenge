from __future__ import annotations

import re
from typing import List, Dict


def normalize_name(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", "-", s)
    return s


def generate_participant_id(first: str, last: str, existing_rows: List[Dict]) -> str:
    """
    Generates collision-safe participant_id like:
    smith-john-01
    smith-john-02
    """

    first_n = normalize_name(first)
    last_n = normalize_name(last)

    base = f"{last_n}-{first_n}"

    existing_ids = {r["participant_id"] for r in existing_rows}

    i = 1
    while True:
        pid = f"{base}-{i:02d}"
        if pid not in existing_ids:
            return pid
        i += 1
