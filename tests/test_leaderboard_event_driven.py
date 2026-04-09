import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

from src.gymchallenge.models import Membership, MembershipEvent
from src.gymchallenge.scoring_engine import DailyScore, build_leaderboard

BERLIN = ZoneInfo("Europe/Berlin")


class TestLeaderboardEventDriven(unittest.TestCase):
    def test_multiple_active_inactive_periods_are_scored_from_events(self):
        membership = Membership(
            cycle_id="c1",
            participant_id="p1",
            active_in_cycle=True,
            joined_at=datetime.fromisoformat("2026-03-01T20:00:00+01:00"),
            left_at=None,
            inactive_reason=None,
            inactive_effective_score_day=None,
        )

        events = [
            MembershipEvent(
                event_id="evt1",
                cycle_id="c1",
                participant_id="p1",
                event_type="manual_inactive",
                effective_score_day=date(2026, 3, 3),
                reason="pause",
                created_at=datetime.fromisoformat("2026-03-03T10:00:00+01:00"),
                actor="jayme",
            ),
            MembershipEvent(
                event_id="evt2",
                cycle_id="c1",
                participant_id="p1",
                event_type="manual_reactivate",
                effective_score_day=date(2026, 3, 5),
                reason="resume",
                created_at=datetime.fromisoformat("2026-03-05T10:00:00+01:00"),
                actor="jayme",
            ),
            MembershipEvent(
                event_id="evt3",
                cycle_id="c1",
                participant_id="p1",
                event_type="auto_inactive",
                effective_score_day=date(2026, 3, 6),
                reason="4 misses",
                created_at=datetime.fromisoformat("2026-03-06T12:00:00+01:00"),
                actor="system",
            ),
            MembershipEvent(
                event_id="evt4",
                cycle_id="c1",
                participant_id="p1",
                event_type="auto_reactivate_submission",
                effective_score_day=date(2026, 3, 7),
                reason="submission",
                created_at=datetime.fromisoformat("2026-03-07T20:05:00+01:00"),
                actor="system",
            ),
        ]

        daily = {
            "p1": {
                date(2026, 3, 1): DailyScore(points=1, participated=True),
                date(2026, 3, 2): DailyScore(points=1, participated=True),
                date(2026, 3, 3): DailyScore(points=10, participated=True),  # excluded by inactive
                date(2026, 3, 4): DailyScore(points=10, participated=True),  # excluded by inactive
                date(2026, 3, 5): DailyScore(points=2, participated=True),
                date(2026, 3, 6): DailyScore(points=10, participated=True),  # excluded by inactive
                date(2026, 3, 7): DailyScore(points=3, participated=True),
            }
        }

        lb = build_leaderboard(
            memberships=[membership],
            membership_events=events,
            daily=daily,
            from_day=date(2026, 3, 1),
            to_day=date(2026, 3, 7),
            tz=BERLIN,
            include_inactive=True,
        )

        # active on 3/1, 3/2, 3/5, 3/7 only => 1 + 1 + 2 + 3 = 7
        self.assertEqual(lb, [("p1", 7)])


if __name__ == "__main__":
    unittest.main()
