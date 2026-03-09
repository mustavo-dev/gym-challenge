from __future__ import annotations

import random
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo


FIRST_NAMES = [
    "John", "Jane", "Michael", "Emily", "Chris", "Sarah", "David", "Laura",
    "James", "Olivia", "Daniel", "Sophia", "Matthew", "Emma", "Andrew", "Mia",
    "Joseph", "Ava", "Ryan", "Charlotte", "Noah", "Amelia", "Ethan", "Harper",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin",
]


def _dt_at_berlin(day: date, hour: int, minute: int, tz: ZoneInfo) -> datetime:
    return datetime.combine(day, time(hour, minute), tzinfo=tz)


def generate_demo_participants(count: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    rows: list[dict] = []

    name_counts: dict[tuple[str, str], int] = {}

    for i in range(count):
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)

        key = (first, last)
        name_counts[key] = name_counts.get(key, 0) + 1
        suffix = f"{name_counts[key]:02d}"

        participant_id = f"{last.lower()}-{first.lower()}-{suffix}"

        rows.append(
            {
                "participant_id": participant_id,
                "first_name": first,
                "last_name": last,
                "created_at": datetime(2026, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("Europe/Berlin")).isoformat(),
                "active": True,
            }
        )

    return rows


def generate_demo_memberships(
    cycle_id: str,
    participant_rows: list[dict],
) -> list[dict]:
    rows: list[dict] = []

    for p in participant_rows:
        rows.append(
            {
                "cycle_id": cycle_id,
                "participant_id": p["participant_id"],
                "active_in_cycle": True,
                "joined_at": datetime(2026, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("Europe/Berlin")).isoformat(),
                "left_at": None,
                "inactive_reason": None,
                "inactive_effective_score_day": None,
            }
        )

    return rows


def generate_demo_submissions(
    cycle_id: str,
    participant_rows: list[dict],
    from_day: date,
    to_day: date,
    seed: int,
    miss_rate: float,
    tz: ZoneInfo,
) -> list[dict]:
    rng = random.Random(seed)
    rows: list[dict] = []

    current = from_day
    submission_counter = 1

    while current <= to_day:
        for p in participant_rows:
            if rng.random() < miss_rate:
                continue

            points = rng.randint(0, 5)
            submitted_minute = rng.randint(0, 59)

            submitted_at = _dt_at_berlin(current, 20, submitted_minute, tz)

            rows.append(
                {
                    "submission_id": f"sub_demo_{submission_counter:06d}",
                    "cycle_id": cycle_id,
                    "participant_id": p["participant_id"],
                    "submitted_at": submitted_at.isoformat(),
                    "points": points,
                    "source": "demo",
                }
            )
            submission_counter += 1

        current += timedelta(days=1)

    return rows
