from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .models import Membership


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
