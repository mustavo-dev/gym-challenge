import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

from gymchallenge.models import Membership
from gymchallenge.scoring_engine import DailyScore, build_leaderboard

BERLIN = ZoneInfo("Europe/Berlin")


class TestLeaderboardAutoReactivate(unittest.TestCase):
    def test_valid_submission_on_inactive_day_reactivates_same_day(self):
        memberships = [
            Membership(
                cycle_id="c1",
                participant_id="p1",
                active_in_cycle=False,
                joined_at=datetime.fromisoformat("2026-03-01T20:00:00+01:00"),
                left_at=None,
                inactive_reason="auto",
                inactive_effective_score_day=date(2026, 3, 6),
            )
        ]

        daily = {
            "p1": {
                date(2026, 3, 1): DailyScore(points=1, participated=True),
                date(2026, 3, 2): DailyScore(points=1, participated=True),
                date(2026, 3, 3): DailyScore(points=-3, participated=False),
                date(2026, 3, 4): DailyScore(points=-3, participated=False),
                date(2026, 3, 5): DailyScore(points=-3, participated=False),
                date(2026, 3, 6): DailyScore(points=2, participated=True),   # should reactivate here
                date(2026, 3, 7): DailyScore(points=3, participated=True),   # should count too
            }
        }

        lb = build_leaderboard(
            memberships=memberships,
            daily=daily,
            from_day=date(2026, 3, 1),
            to_day=date(2026, 3, 7),
            tz=BERLIN,
            include_inactive=True,
        )

        # Count all active days up to 3/5, then 3/6 reactivates and counts, 3/7 counts too
        # => 1 + 1 - 3 - 3 - 3 + 2 + 3 = -2
        self.assertEqual(lb, [("p1", -2)])

    def test_correction_only_day_does_not_reactivate(self):
        memberships = [
            Membership(
                cycle_id="c1",
                participant_id="p1",
                active_in_cycle=False,
                joined_at=datetime.fromisoformat("2026-03-01T20:00:00+01:00"),
                left_at=None,
                inactive_reason="auto",
                inactive_effective_score_day=date(2026, 3, 6),
            )
        ]

        daily = {
            "p1": {
                date(2026, 3, 1): DailyScore(points=1, participated=True),
                date(2026, 3, 2): DailyScore(points=1, participated=True),
                date(2026, 3, 3): DailyScore(points=-3, participated=False),
                date(2026, 3, 4): DailyScore(points=-3, participated=False),
                date(2026, 3, 5): DailyScore(points=-3, participated=False),
                date(2026, 3, 6): DailyScore(points=2, participated=False),  # corrected points only, no participation
                date(2026, 3, 7): DailyScore(points=3, participated=True),   # valid submission, should reactivate here
            }
        }

        lb = build_leaderboard(
            memberships=memberships,
            daily=daily,
            from_day=date(2026, 3, 1),
            to_day=date(2026, 3, 7),
            tz=BERLIN,
            include_inactive=True,
        )

        # 3/6 does NOT reactivate because participated=False, so 3/6 excluded
        # 3/7 does reactivate and count
        # => 1 + 1 - 3 - 3 - 3 + 3 = -4
        self.assertEqual(lb, [("p1", -4)])


if __name__ == "__main__":
    unittest.main()
