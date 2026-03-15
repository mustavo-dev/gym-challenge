from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .models import Membership, Cycle, Submission, Correction, MembershipEvent


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

def load_corrections(rows: list[dict[str, Any]]) -> list[Correction]:
    out: list[Correction] = []
    for r in rows:
        out.append(
            Correction(
                correction_id=r["correction_id"],
                cycle_id=r["cycle_id"],
                participant_id=r["participant_id"],
                score_day=date.fromisoformat(r["score_day"]),
                new_points=int(r["new_points"]),
                reason=r["reason"],
                created_at=datetime.fromisoformat(r["created_at"]),
                admin=r.get("admin", "admin"),
            )
        )
    return out

def load_membership_events(rows: list[dict[str, Any]]) -> list[MembershipEvent]:
    out: list[MembershipEvent] = []
    for r in rows:
        out.append(
            MembershipEvent(
                event_id=r["event_id"],
                cycle_id=r["cycle_id"],
                participant_id=r["participant_id"],
                event_type=r["event_type"],
                effective_score_day=date.fromisoformat(r["effective_score_day"]),
                reason=r["reason"],
                created_at=datetime.fromisoformat(r["created_at"]),
                actor=r["actor"],
            )
        )
    return out

def load_system_events(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []

    for row in rows:
        out.append(
            {
                "event_id": row["event_id"],
                "event_type": row["event_type"],
                "participant_id": row.get("participant_id"),
                "reason": row.get("reason", ""),
                "created_at": datetime.fromisoformat(str(row["created_at"])),
                "actor": row.get("actor", "system"),
            }
        )

    return out
