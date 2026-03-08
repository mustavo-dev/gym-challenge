import unittest

from gymchallenge.membership_event_store import has_matching_event


class TestMembershipEventStore(unittest.TestCase):
    def test_has_matching_event(self):
        rows = [
            {
                "cycle_id": "c1",
                "participant_id": "p1",
                "event_type": "auto_inactive",
                "effective_score_day": "2026-03-06",
            }
        ]

        self.assertTrue(
            has_matching_event(
                rows,
                cycle_id="c1",
                participant_id="p1",
                event_type="auto_inactive",
                effective_score_day="2026-03-06",
            )
        )

        self.assertFalse(
            has_matching_event(
                rows,
                cycle_id="c1",
                participant_id="p1",
                event_type="auto_inactive",
                effective_score_day="2026-03-07",
            )
        )


if __name__ == "__main__":
    unittest.main()
