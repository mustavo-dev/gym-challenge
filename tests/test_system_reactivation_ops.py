import os
import tempfile
import unittest
from datetime import date, datetime

from gymchallenge.storage_json import load_list
from gymchallenge.system_event_ops import append_missing_auto_reactivate_events


class TestSystemReactivationOps(unittest.TestCase):
    def test_appends_only_missing_auto_reactivate_events(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "membership_events.json")

            existing = [
                {
                    "event_id": "evt_existing",
                    "cycle_id": "c1",
                    "participant_id": "p1",
                    "event_type": "auto_reactivate_submission",
                    "effective_score_day": "2026-03-06",
                    "reason": "Valid participant submission reactivated member",
                    "created_at": "2026-03-06T12:00:00+01:00",
                    "actor": "system",
                }
            ]

            updates = {
                "p1": date(2026, 3, 6),  # duplicate
                "p2": date(2026, 3, 7),  # new
            }

            written = append_missing_auto_reactivate_events(
                path=path,
                existing_rows=existing,
                cycle_id="c1",
                updates=updates,
                created_at=datetime.fromisoformat("2026-03-08T12:00:00+01:00"),
            )

            rows = load_list(path)

            self.assertEqual(len(written), 1)
            self.assertEqual(written[0]["participant_id"], "p2")
            self.assertEqual(written[0]["event_type"], "auto_reactivate_submission")
            self.assertEqual(written[0]["effective_score_day"], "2026-03-07")
            self.assertEqual(rows[0]["participant_id"], "p2")


if __name__ == "__main__":
    unittest.main()
