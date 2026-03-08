from __future__ import annotations

from datetime import date
from typing import Any


SEASONS = {"spring", "summer", "fall", "winter"}


def build_cycle_id(season: str, year: int) -> str:
    season_n = season.strip().lower()
    if season_n not in SEASONS:
        raise ValueError("season must be one of: spring, summer, fall, winter")

    if year < 2000 or year > 2099:
        raise ValueError("year must be between 2000 and 2099")

    return f"{season_n}{year % 100:02d}"


def build_cycle_name(season: str, year: int) -> str:
    season_n = season.strip().lower()
    if season_n not in SEASONS:
        raise ValueError("season must be one of: spring, summer, fall, winter")

    return f"{season_n.capitalize()} {year}"


def has_active_cycle(rows: list[dict[str, Any]]) -> bool:
    for r in rows:
        if r.get("active") is True:
            return True
    return False

def has_cycle_id(rows: list[dict[str, Any]], cycle_id: str) -> bool:
    for r in rows:
        if r.get("cycle_id") == cycle_id:
            return True
    return False
