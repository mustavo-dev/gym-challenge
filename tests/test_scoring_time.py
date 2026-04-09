import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from src.gymchallenge.scoring_time import is_within_checkin_window, score_day_for_timestamp


BERLIN = ZoneInfo("Europe/Berlin")


class TestScoringTime(unittest.TestCase):
    def test_window_boundaries(self):
        # 19:59 is invalid
        dt = datetime.fromisoformat("2026-03-02T19:59:00+01:00")
        self.assertFalse(is_within_checkin_window(dt, BERLIN))
        self.assertIsNone(score_day_for_timestamp(dt, BERLIN))

        # 20:00 is valid and maps to same day
        dt = datetime.fromisoformat("2026-03-02T20:00:00+01:00")
        self.assertTrue(is_within_checkin_window(dt, BERLIN))
        self.assertEqual(score_day_for_timestamp(dt, BERLIN).isoformat(), "2026-03-02")

        # 11:59 is valid and maps to previous day
        dt = datetime.fromisoformat("2026-03-03T11:59:00+01:00")
        self.assertTrue(is_within_checkin_window(dt, BERLIN))
        self.assertEqual(score_day_for_timestamp(dt, BERLIN).isoformat(), "2026-03-02")

        # 12:00 is invalid
        dt = datetime.fromisoformat("2026-03-03T12:00:00+01:00")
        self.assertFalse(is_within_checkin_window(dt, BERLIN))
        self.assertIsNone(score_day_for_timestamp(dt, BERLIN))

    def test_requires_timezone_aware(self):
        dt = datetime(2026, 3, 2, 20, 0, 0)  # naive
        with self.assertRaises(ValueError):
            is_within_checkin_window(dt, BERLIN)

    def test_time_zone_conversion(self):
        # This timestamp is 19:00 UTC which is 20:00 Berlin (CET) on this date.
        dt = datetime.fromisoformat("2026-03-02T19:00:00+00:00")
        self.assertTrue(is_within_checkin_window(dt, BERLIN))
        self.assertEqual(score_day_for_timestamp(dt, BERLIN).isoformat(), "2026-03-02")


if __name__ == "__main__":
    unittest.main()
