from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .models import Membership, Cycle, Submission


def load_memberships(rows: list[dict[str, Any]]) -> list[Membership]:
    out: list[Membership] = []
    for r in rows:
        out.append(
            Membership(
                cycle_id=r["cycle_id"],
                participant_id=r["participant_id"],
                active_in_cycle=bool(r["active_in_cycle"]),
                joined_at=datetime.fromisoformat(r["joined_at"]),
                left_at=datetime.fromisoformat(r["left_at"]) if r.get("left_at") else None,
                inactive_reason=r.get("inactive_reason"),
                inactive_effective_score_day=date.fromisoformat(r["inactive_effective_score_day"])
                if r.get("inactive_effective_score_day")
                else None,
            )
        )
    return out

def load_cycles(rows: list[dict[str, Any]]) -> list[Cycle]:
    out: list[Cycle] = []
    for r in rows:
        out.append(
            Cycle(
                cycle_id=r["cycle_id"],
                name=r["name"],
                start_day=date.fromisoformat(r["start_day"]),
                end_day=date.fromisoformat(r["end_day"]),
                created_at=datetime.fromisoformat(r["created_at"]),
                active=bool(r.get("active", True)),
            )
        )
    return out

def load_submissions(rows: list[dict[str, Any]]) -> list[Submission]:
    out: list[Submission] = []
    for r in rows:
        out.append(
            Submission(
                submission_id=r["submission_id"],
                cycle_id=r["cycle_id"],
                participant_id=r["participant_id"],
                submitted_at=datetime.fromisoformat(r["submitted_at"]),
                points=int(r["points"]),
                source=r.get("source", "manual"),
            )
        )
    return out
