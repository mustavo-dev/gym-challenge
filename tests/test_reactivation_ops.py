import unittest
from datetime import date, datetime

from gymchallenge.models import Membership
from gymchallenge.scoring_engine import DailyScore
from gymchallenge.reactivation_ops import detect_auto_reactivate


class TestReactivationOps(unittest.TestCase):
    def test_detects_earliest_valid_submission_day(self):
        memberships = [
            Membership(
                cycle_id="c1",
                participant_id="p1",
                active_in_cycle=False,
                joined_at=datetime.fromisoformat("2026-03-01T20:00:00+01:00"),
                left_at=None,
                inactive_reason="auto",
                inactive_effective_score_day=date(2026, 3, 5),
            )
        ]

        daily = {
            "p1": {
                date(2026, 3, 5): DailyScore(points=2, participated=False),
                date(2026, 3, 6): DailyScore(points=1, participated=True),
                date(2026, 3, 7): DailyScore(points=3, participated=True),
            }
        }

        updates = detect_auto_reactivate(
            memberships=memberships,
            daily=daily,
            from_day=date(2026, 3, 1),
            to_day=date(2026, 3, 7),
        )

        self.assertEqual(updates, {"p1": date(2026, 3, 6)})

    def test_does_not_reactivate_on_correction_only_day(self):
        memberships = [
            Membership(
                cycle_id="c1",
                participant_id="p1",
                active_in_cycle=False,
                joined_at=datetime.fromisoformat("2026-03-01T20:00:00+01:00"),
                left_at=None,
                inactive_reason="auto",
                inactive_effective_score_day=date(2026, 3, 5),
            )
        ]

        daily = {
            "p1": {
                date(2026, 3, 5): DailyScore(points=2, participated=False),
                date(2026, 3, 6): DailyScore(points=2, participated=False),
                date(2026, 3, 7): DailyScore(points=3, participated=True),
            }
        }

        updates = detect_auto_reactivate(
            memberships=memberships,
            daily=daily,
            from_day=date(2026, 3, 1),
            to_day=date(2026, 3, 7),
        )

        self.assertEqual(updates, {"p1": date(2026, 3, 7)})


if __name__ == "__main__":
    unittest.main()
