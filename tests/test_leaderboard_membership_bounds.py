import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

from src.gymchallenge.models import Membership
from src.gymchallenge.scoring_engine import DailyScore, build_leaderboard

BERLIN = ZoneInfo("Europe/Berlin")


class TestLeaderboardMembershipBounds(unittest.TestCase):
    def test_joined_at_limits_start_day(self):
        memberships = [
            Membership(
                cycle_id="c1",
                participant_id="p1",
                active_in_cycle=True,
                joined_at=datetime.fromisoformat("2026-03-03T20:00:00+01:00"),
                left_at=None,
                inactive_reason=None,
                inactive_effective_score_day=None,
            )
        ]

        daily = {
            "p1": {
                date(2026, 3, 1): DailyScore(points=10, participated=True),
                date(2026, 3, 2): DailyScore(points=10, participated=True),
                date(2026, 3, 3): DailyScore(points=1, participated=True),
                date(2026, 3, 4): DailyScore(points=1, participated=True),
            }
        }

        lb = build_leaderboard(
            memberships=memberships,
            membership_events=[],
            daily=daily,
            from_day=date(2026, 3, 1),
            to_day=date(2026, 3, 4),
            tz=BERLIN,
            include_inactive=True,
        )

        # joined_at is 2026-03-03T20:00 -> score day 2026-03-03
        # so only count 3/3 and 3/4 => 1 + 1 = 2
        self.assertEqual(lb, [("p1", 2)])

    def test_left_at_limits_end_day(self):
        memberships = [
            Membership(
                cycle_id="c1",
                participant_id="p1",
                active_in_cycle=True,
                joined_at=datetime.fromisoformat("2026-03-01T20:00:00+01:00"),
                left_at=datetime.fromisoformat("2026-03-05T20:00:00+01:00"),
                inactive_reason=None,
                inactive_effective_score_day=None,
            )
        ]

        daily = {
            "p1": {
                date(2026, 3, 1): DailyScore(points=1, participated=True),
                date(2026, 3, 2): DailyScore(points=1, participated=True),
                date(2026, 3, 3): DailyScore(points=1, participated=True),
                date(2026, 3, 4): DailyScore(points=1, participated=True),
                date(2026, 3, 5): DailyScore(points=100, participated=True),
            }
        }

        lb = build_leaderboard(
            memberships=memberships,
            membership_events=[],
            daily=daily,
            from_day=date(2026, 3, 1),
            to_day=date(2026, 3, 5),
            tz=BERLIN,
            include_inactive=True,
        )

        # left_at is 2026-03-05T20:00 -> score day 2026-03-05
        # exclude 3/5 and later, so count 3/1..3/4 => 4
        self.assertEqual(lb, [("p1", 4)])


if __name__ == "__main__":
    unittest.main()
