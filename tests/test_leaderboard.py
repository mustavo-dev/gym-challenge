import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

from gymchallenge.models import Membership, MembershipEvent
from gymchallenge.scoring_engine import DailyScore, build_leaderboard

BERLIN = ZoneInfo("Europe/Berlin")

class TestLeaderboard(unittest.TestCase):
    def test_historical_inactive_stays_visible_but_stops_scoring(self):
        memberships = [
            Membership(
                cycle_id="c1",
                participant_id="p1",
                active_in_cycle=False,
                joined_at=datetime.fromisoformat("2026-03-01T20:00:00+01:00"),
                left_at=None,
                inactive_reason="auto",
                inactive_effective_score_day=date(2026, 3, 3),
            ),
            Membership(
                cycle_id="c1",
                participant_id="p2",
                active_in_cycle=True,
                joined_at=datetime.fromisoformat("2026-03-01T20:00:00+01:00"),
                left_at=None,
                inactive_reason=None,
                inactive_effective_score_day=None,
            ),
        ]
        membership_events = [
            MembershipEvent(
                event_id="evt1",
                cycle_id="c1",
                participant_id="p1",
                event_type="auto_inactive",
                effective_score_day=date(2026, 3, 3),
                reason="4 consecutive missed days",
                created_at=datetime.fromisoformat("2026-03-03T12:00:00+01:00"),
                actor="system",
          )
        ]

        daily = {
            "p1": {
                date(2026, 3, 1): DailyScore(points=1, participated=True),
                date(2026, 3, 2): DailyScore(points=-3, participated=False),
                date(2026, 3, 3): DailyScore(points=-3, participated=False),  # excluded (inactive effective day)
                date(2026, 3, 4): DailyScore(points=-3, participated=False),  # excluded
            },
            "p2": {
                date(2026, 3, 1): DailyScore(points=2, participated=True),
                date(2026, 3, 2): DailyScore(points=2, participated=True),
                date(2026, 3, 3): DailyScore(points=2, participated=True),
                date(2026, 3, 4): DailyScore(points=2, participated=True),
            },
        }

        lb = build_leaderboard(
            memberships=memberships,
            membership_events=membership_events,
            tz=BERLIN,
            daily=daily,
            from_day=date(2026, 3, 1),
            to_day=date(2026, 3, 4),
            include_inactive=True,
        )

        # p1 total counts only 3/1 and 3/2 => 1 + (-3) = -2
        # p2 total counts all days => 8
        self.assertEqual(lb, [("p2", 8), ("p1", -2)])

    def test_exclude_inactive_omits_them(self):
        memberships = [
            Membership(
                cycle_id="c1",
                participant_id="p1",
                active_in_cycle=False,
                joined_at=datetime.fromisoformat("2026-03-01T20:00:00+01:00"),
                left_at=None,
                inactive_reason="auto",
                inactive_effective_score_day=date(2026, 3, 3),
            ),
            Membership(
                cycle_id="c1",
                participant_id="p2",
                active_in_cycle=True,
                joined_at=datetime.fromisoformat("2026-03-01T20:00:00+01:00"),
                left_at=None,
                inactive_reason=None,
                inactive_effective_score_day=None,
            ),
        ]

        daily = {
            "p1": {
                date(2026, 3, 1): DailyScore(points=1, participated=True),
                date(2026, 3, 2): DailyScore(points=-3, participated=False),
            },
            "p2": {
                date(2026, 3, 1): DailyScore(points=2, participated=True),
                date(2026, 3, 2): DailyScore(points=2, participated=True),
            },
        }

        lb = build_leaderboard(
            memberships=memberships,
            membership_events=[],
            tz=BERLIN,
            daily=daily,
            from_day=date(2026, 3, 1),
            to_day=date(2026, 3, 2),
            include_inactive=False,
        )

        self.assertEqual(lb, [("p2", 4)])


if __name__ == "__main__":
    unittest.main()
