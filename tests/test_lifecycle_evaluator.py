import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

from src.gymchallenge.models import Membership
from src.gymchallenge.scoring_engine import DailyScore
from src.gymchallenge.lifecycle_evaluator import evaluate_lifecycle

BERLIN = ZoneInfo("Europe/Berlin")

class TestLifecycleEvaluator(unittest.TestCase):
    def test_reconstructs_multiple_lifecycle_transitions(self):
        membership = Membership(
            cycle_id="c1",
            participant_id="p1",
            active_in_cycle=True,
            joined_at=datetime.fromisoformat("2026-03-01T20:00:00+01:00"),
            left_at=None,
            inactive_reason=None,
            inactive_effective_score_day=None,
        )

        daily = {"p1": {}}

        for day in range(1, 18):
            daily["p1"][date(2026, 3, day)] = DailyScore(
                points=-3,
                participated=False,
            )

        daily["p1"][date(2026, 3, 8)] = DailyScore(
            points=3,
            participated=True,
        )
        daily["p1"][date(2026, 3, 16)] = DailyScore(
            points=2,
            participated=True,
        )

        cycle_start = date(2026, 3, 1)
        cycle_end = date(2026, 3, 17)
        as_of = datetime(2026, 3, 17, 12, 0, tzinfo=BERLIN)

        expected_transitions = [
            ("p1", "auto_inactive", date(2026, 3, 5)),
            ("p1", "auto_reactivate_submission", date(2026, 3, 8)),
            ("p1", "auto_inactive", date(2026, 3, 13)),
            ("p1", "auto_reactivate_submission", date(2026, 3, 16)),
        ]

        transitions = evaluate_lifecycle(
            membership=membership,
            daily=daily,
            cycle_start=cycle_start,
            cycle_end=cycle_end,
            as_of=as_of,
            tz=BERLIN,
        )

        actual_transitions = []

        for transition in transitions:
            actual_transitions.append((
                transition.participant_id,
                transition.event_type,
                transition.effective_score_day,
            ))

        self.assertEqual(actual_transitions, expected_transitions)

    def test_four_completed_misses_generate_first_inactivity(self):
        membership = Membership(
            cycle_id="c1",
            participant_id="p1",
            active_in_cycle=True,
            joined_at=datetime.fromisoformat("2026-03-01T20:00:00+01:00"),
            left_at=None,
            inactive_reason=None,
            inactive_effective_score_day=None,
        )

        daily = {"p1": {}}

        for day in range(1, 5):
            daily["p1"][date(2026, 3, day)] = DailyScore(
                points=-3,
                participated=False,
            )

        cycle_start = date(2026, 3, 1)
        cycle_end = date(2026, 3, 7)
        as_of = datetime(2026, 3, 5, 12, 0, tzinfo=BERLIN)

        expected_transitions = [
            ("p1", "auto_inactive", date(2026, 3, 5)),
        ]

        transitions = evaluate_lifecycle(
            membership=membership,
            daily=daily,
            cycle_start=cycle_start,
            cycle_end=cycle_end,
            as_of=as_of,
            tz=BERLIN,
        )

        actual_transitions = []

        for transition in transitions:
            actual_transitions.append((
                transition.participant_id,
                transition.event_type,
                transition.effective_score_day,
            ))

        self.assertEqual(actual_transitions, expected_transitions)

if __name__ == "__main__":
    unittest.main()
