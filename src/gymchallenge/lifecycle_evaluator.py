from dataclasses import dataclass
from datetime import date, time, timedelta

@dataclass(frozen=True)
class LifecycleTransition:
    participant_id: str
    event_type: str
    effective_score_day: date

def evaluate_lifecycle(
    membership,
    daily,
    cycle_start,
    cycle_end,
    as_of,
    tz,
):
    transitions = []
    active = True
    missed_streak = 0

    per_day = daily.get(membership.participant_id, {})

    local_as_of = as_of.astimezone(tz)

    if local_as_of.time() < time(12, 0):
        last_completed_day = local_as_of.date() - timedelta(days=2)
    else:
        last_completed_day = local_as_of.date() - timedelta(days=1)

    evaluation_end = min(cycle_end, last_completed_day)

    if local_as_of.time() >= time(20, 0):
        last_started_day = local_as_of.date()
    else:
        last_started_day = local_as_of.date() - timedelta(days=1)

    last_day_to_visit = min(cycle_end, last_started_day)

    d = cycle_start

    while d <= last_day_to_visit:
        day_score = per_day.get(d)

        if day_score is not None and day_score.participated:
            if not active:
                transitions.append(
                    LifecycleTransition(
                        participant_id=membership.participant_id,
                        event_type="auto_reactivate_submission",
                        effective_score_day=d,
                    )
                )
                active = True

            missed_streak = 0

        d += timedelta(days=1)

    return transitions