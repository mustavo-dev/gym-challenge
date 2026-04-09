from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass(frozen=True)
class Participant:
    participant_id: str
    first_name: str
    last_name: str
    created_at: datetime
    active: bool = True

    @property
    def display_name(self) -> str:
        """Canonical display name used throughout the system."""
        return f"{self.last_name}, {self.first_name}"


@dataclass(frozen=True)
class Cycle:
    cycle_id: str
    name: str
    start_day: date
    end_day: date
    created_at: datetime
    active: bool = True


@dataclass(frozen=True)
class Membership:
    cycle_id: str
    participant_id: str
    active_in_cycle: bool
    joined_at: datetime
    left_at: Optional[datetime] = None

    # Inactive tracking (per-cycle)
    inactive_reason: Optional[str] = None  # "manual" | "auto"
    inactive_effective_score_day: Optional[date] = None


@dataclass(frozen=True)
class Submission:
    submission_id: str
    cycle_id: str
    participant_id: str
    submitted_at: datetime  # tz-aware
    points: int  # -3..5
    source: str  # manual|import|future:google


@dataclass(frozen=True)
class Correction:
    correction_id: str
    cycle_id: str
    participant_id: str
    score_day: date
    new_points: int
    reason: str  # REQUIRED
    created_at: datetime
    admin: str

@dataclass(frozen=True)
class MembershipEvent:
    event_id: str
    cycle_id: str
    participant_id: str
    event_type: str  # auto_inactive | manual_inactive | manual_reactivate | auto_reactivate_submission
    effective_score_day: date
    reason: str
    created_at: datetime
    actor: str  # system | configured admin actor
