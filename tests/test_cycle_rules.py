import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

from src.gymchallenge.cycle_rules import score_day_in_cycle, cycle_accepts_timestamp

BERLIN = ZoneInfo("Europe/Berlin")


class TestCycleRules(unittest.TestCase):
    def test_score_day_in_cycle_inclusive(self):
        start = date(2026, 3, 1)
        end = date(2026, 3, 2)

        self.assertTrue(score_day_in_cycle(date(2026, 3, 1), start, end))
        self.assertTrue(score_day_in_cycle(date(2026, 3, 2), start, end))
        self.assertFalse(score_day_in_cycle(date(2026, 2, 28), start, end))
        self.assertFalse(score_day_in_cycle(date(2026, 3, 3), start, end))

    def test_cycle_accepts_timestamp_rejects_invalid_window(self):
        start = date(2026, 3, 1)
        end = date(2026, 3, 2)

        # 12:00 is invalid window time
        dt = datetime.fromisoformat("2026-03-02T12:00:00+01:00")
        ok, sd = cycle_accepts_timestamp(dt, BERLIN, start, end)
        self.assertFalse(ok)
        self.assertIsNone(sd)

    def test_cycle_accepts_timestamp_accepts_end_score_day_until_next_noon(self):
        start = date(2026, 3, 1)
        end = date(2026, 3, 2)

        # Cycle ends on 2026-03-02 (score day). Submissions are allowed until 12:00 on 2026-03-03.
        dt = datetime.fromisoformat("2026-03-03T11:59:00+01:00")  # maps to score_day 2026-03-02
        ok, sd = cycle_accepts_timestamp(dt, BERLIN, start, end)
        self.assertTrue(ok)
        self.assertEqual(sd, date(2026, 3, 2))

        dt = datetime.fromisoformat("2026-03-03T12:00:00+01:00")  # invalid window
        ok, sd = cycle_accepts_timestamp(dt, BERLIN, start, end)
        self.assertFalse(ok)
        self.assertIsNone(sd)

    def test_cycle_accepts_timestamp_rejects_score_day_outside_cycle(self):
        start = date(2026, 3, 1)
        end = date(2026, 3, 2)

        # 2026-03-03 20:00 maps to score_day 2026-03-03, which is outside the cycle
        dt = datetime.fromisoformat("2026-03-03T20:00:00+01:00")
        ok, sd = cycle_accepts_timestamp(dt, BERLIN, start, end)
        self.assertFalse(ok)
        self.assertEqual(sd, date(2026, 3, 3))  # score day is known, but rejected due to cycle bounds


if __name__ == "__main__":
    unittest.main()
