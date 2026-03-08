import os
import tempfile
import unittest
from datetime import date, datetime

from gymchallenge.membership_event_ops import append_membership_event
from gymchallenge.storage_json import load_list


class TestMembershipEventOps(unittest.TestCase):
    def test_append_membership_event(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "membership_events.json")

            row = append_membership_event(
                path=path,
                cycle_id="c1",
                participant_id="p1",
                event_type="manual_inactive",
                effective_score_day=date(2026, 3, 6),
                reason="Stopped participating",
                created_at=datetime.fromisoformat("2026-03-06T12:00:00+01:00"),
                actor="jayme",
            )

            rows = load_list(path)

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["cycle_id"], "c1")
            self.assertEqual(rows[0]["participant_id"], "p1")
            self.assertEqual(rows[0]["event_type"], "manual_inactive")
            self.assertEqual(rows[0]["effective_score_day"], "2026-03-06")
            self.assertEqual(rows[0]["reason"], "Stopped participating")
            self.assertEqual(rows[0]["actor"], "jayme")
            self.assertTrue(row["event_id"].startswith("evt_"))


if __name__ == "__main__":
    unittest.main()
