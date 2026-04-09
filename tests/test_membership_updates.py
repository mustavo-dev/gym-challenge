import unittest
from datetime import date, datetime

from src.gymchallenge.models import Membership
from src.gymchallenge.scoring_engine import apply_auto_inactive, reactivate_member


class TestMembershipUpdates(unittest.TestCase):
    def test_apply_auto_inactive_sets_fields(self):
        memberships = [
            Membership(
                cycle_id="c1",
                participant_id="p1",
                active_in_cycle=True,
                joined_at=datetime.fromisoformat("2026-03-01T20:00:00+01:00"),
                left_at=None,
                inactive_reason=None,
                inactive_effective_score_day=None,
            )
        ]

        updates = {"p1": date(2026, 3, 5)}
        new_memberships = apply_auto_inactive(memberships, updates)

        self.assertFalse(new_memberships[0].active_in_cycle)
        self.assertEqual(new_memberships[0].inactive_reason, "auto")
        self.assertEqual(new_memberships[0].inactive_effective_score_day, date(2026, 3, 5))

    def test_reactivate_keeps_inactive_reason_but_clears_effective_day(self):
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

        new_memberships = reactivate_member(
            memberships,
            participant_id="p1",
            effective_day=date(2026, 3, 6),
            reason="Admin override",
        )

        self.assertTrue(new_memberships[0].active_in_cycle)
        self.assertEqual(new_memberships[0].inactive_reason, "auto")   # kept as history
        self.assertIsNone(new_memberships[0].inactive_effective_score_day)

    def test_reactivate_requires_reason(self):
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

        with self.assertRaises(ValueError):
            reactivate_member(
                memberships,
                participant_id="p1",
                effective_day=date(2026, 3, 6),
                reason="",
            )


if __name__ == "__main__":
    unittest.main()
