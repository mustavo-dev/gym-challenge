import unittest
from datetime import date, datetime

from gymchallenge.models import MembershipEvent


class TestMembershipEventModel(unittest.TestCase):
    def test_membership_event_creation(self):
        event = MembershipEvent(
            event_id="evt_1234abcd",
            cycle_id="c1",
            participant_id="p1",
            event_type="auto_inactive",
            effective_score_day=date(2026, 3, 6),
            reason="4 consecutive missed days",
            created_at=datetime.fromisoformat("2026-03-06T12:00:00+01:00"),
            actor="system",
        )

        self.assertEqual(event.event_id, "evt_1234abcd")
        self.assertEqual(event.event_type, "auto_inactive")
        self.assertEqual(event.actor, "system")


if __name__ == "__main__":
    unittest.main()
