import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

from gymchallenge.models import Membership, MembershipEvent
from gymchallenge.membership_timeline import build_active_day_map

BERLIN = ZoneInfo("Europe/Berlin")


class TestMembershipTimeline(unittest.TestCase):
    def test_manual_inactive_then_manual_reactivate(self):
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
        ]

        active_map = build_active_day_map(
            membership=membership,
            events=events,
            from_day=date(2026, 3, 1),
            to_day=date(2026, 3, 6),
            tz=BERLIN,
        )

        self.assertEqual(
            active_map,
            {
                date(2026, 3, 1): True,
                date(2026, 3, 2): True,
                date(2026, 3, 3): False,
                date(2026, 3, 4): False,
                date(2026, 3, 5): True,
                date(2026, 3, 6): True,
            },
        )

    def test_auto_inactive_then_auto_reactivate_submission(self):
        membership = Membership(
            cycle_id="c1",
            participant_id="p1",
            active_in_cycle=False,
            joined_at=datetime.fromisoformat("2026-03-01T20:00:00+01:00"),
            left_at=None,
            inactive_reason="auto",
            inactive_effective_score_day=date(2026, 3, 4),
        )

        events = [
            MembershipEvent(
                event_id="evt1",
                cycle_id="c1",
                participant_id="p1",
                event_type="auto_inactive",
                effective_score_day=date(2026, 3, 4),
                reason="4 consecutive missed days",
                created_at=datetime.fromisoformat("2026-03-04T12:00:00+01:00"),
                actor="system",
            ),
            MembershipEvent(
                event_id="evt2",
                cycle_id="c1",
                participant_id="p1",
                event_type="auto_reactivate_submission",
                effective_score_day=date(2026, 3, 6),
                reason="valid submission",
                created_at=datetime.fromisoformat("2026-03-06T20:05:00+01:00"),
                actor="system",
            ),
        ]

        active_map = build_active_day_map(
            membership=membership,
            events=events,
            from_day=date(2026, 3, 1),
            to_day=date(2026, 3, 7),
            tz=BERLIN,
        )

        self.assertEqual(active_map[date(2026, 3, 3)], True)
        self.assertEqual(active_map[date(2026, 3, 4)], False)
        self.assertEqual(active_map[date(2026, 3, 5)], False)
        self.assertEqual(active_map[date(2026, 3, 6)], True)
        self.assertEqual(active_map[date(2026, 3, 7)], True)

    def test_left_at_ends_activity(self):
        membership = Membership(
            cycle_id="c1",
            participant_id="p1",
            active_in_cycle=True,
            joined_at=datetime.fromisoformat("2026-03-01T20:00:00+01:00"),
            left_at=datetime.fromisoformat("2026-03-05T20:00:00+01:00"),
            inactive_reason=None,
            inactive_effective_score_day=None,
        )

        events = []

        active_map = build_active_day_map(
            membership=membership,
            events=events,
            from_day=date(2026, 3, 1),
            to_day=date(2026, 3, 6),
            tz=BERLIN,
        )

        self.assertEqual(active_map[date(2026, 3, 4)], True)
        self.assertEqual(active_map[date(2026, 3, 5)], False)
        self.assertEqual(active_map[date(2026, 3, 6)], False)


if __name__ == "__main__":
    unittest.main()
