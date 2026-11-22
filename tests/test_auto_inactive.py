import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

from src.gymchallenge.scoring_engine import DailyScore, detect_auto_inactive


class TestAutoInactive(unittest.TestCase):
    def test_triggers_after_four_consecutive_misses(self):
        cycle_start = date(2026, 3, 1)
        cycle_end = date(2026, 3, 6)

        # p1 misses 3/1,3/2,3/3,3/4 => becomes inactive effective 3/5
        daily = {
            "p1": {
                date(2026, 3, 1): DailyScore(points=-3, participated=False),
                date(2026, 3, 2): DailyScore(points=-3, participated=False),
                date(2026, 3, 3): DailyScore(points=-3, participated=False),
                date(2026, 3, 4): DailyScore(points=-3, participated=False),
                date(2026, 3, 5): DailyScore(points=2, participated=True),
                date(2026, 3, 6): DailyScore(points=2, participated=True),
            }
        }

        updates = detect_auto_inactive(daily, cycle_start, cycle_end, streak_required=4)
        self.assertEqual(updates["p1"], date(2026, 3, 5))

    def test_future_days_do_not_trigger_inactivity(self):
        cycle_start = date(2026, 3, 1)
        cycle_end = date(2026, 3, 7)
        tz = ZoneInfo("Europe/Berlin")
        as_of = datetime(2026, 3, 1, 21, 0, tzinfo=tz)

        daily = {
            "p1": {
                date(2026, 3, 1): DailyScore(points=4, participated=True),
                date(2026, 3, 2): DailyScore(points=-3, participated=False),
                date(2026, 3, 3): DailyScore(points=-3, participated=False),
                date(2026, 3, 4): DailyScore(points=-3, participated=False),
                date(2026, 3, 5): DailyScore(points=-3, participated=False),
                date(2026, 3, 6): DailyScore(points=-3, participated=False),
                date(2026, 3, 7): DailyScore(points=-3, participated=False),
            }
        }

        updates = detect_auto_inactive(daily, cycle_start, cycle_end, as_of=as_of, tz=tz, streak_required=4)
        self.assertEqual(updates, {})

    def test_streak_resets_on_participation(self):
        cycle_start = date(2026, 3, 1)
        cycle_end = date(2026, 3, 7)

        # misses 3 days, participates, then misses 4 => triggers on second streak
        daily = {
            "p1": {
                date(2026, 3, 1): DailyScore(points=-3, participated=False),
                date(2026, 3, 2): DailyScore(points=-3, participated=False),
                date(2026, 3, 3): DailyScore(points=-3, participated=False),
                date(2026, 3, 4): DailyScore(points=1, participated=True),
                date(2026, 3, 5): DailyScore(points=-3, participated=False),
                date(2026, 3, 6): DailyScore(points=-3, participated=False),
                date(2026, 3, 7): DailyScore(points=-3, participated=False),
            }
        }

        updates = detect_auto_inactive(daily, cycle_start, cycle_end, streak_required=4)
        self.assertNotIn("p1", updates)

    def test_effective_day_is_next_day_even_if_outside_cycle(self):
        cycle_start = date(2026, 3, 1)
        cycle_end = date(2026, 3, 4)

        # 4th miss on cycle_end => effective next day (outside cycle)
        daily = {
            "p1": {
                date(2026, 3, 1): DailyScore(points=-3, participated=False),
                date(2026, 3, 2): DailyScore(points=-3, participated=False),
                date(2026, 3, 3): DailyScore(points=-3, participated=False),
                date(2026, 3, 4): DailyScore(points=-3, participated=False),
            }
        }

        updates = detect_auto_inactive(daily, cycle_start, cycle_end, streak_required=4)
        self.assertEqual(updates["p1"], date(2026, 3, 5))


if __name__ == "__main__":
    unittest.main()
