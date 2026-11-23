import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

from src.gymchallenge.scoring_engine import DailyScore, detect_auto_inactive


class TestAutoInactive(unittest.TestCase):
    def test_triggers_after_four_consecutive_misses(self):
        cycle_start = date(2026, 3, 1)
        cycle_end = date(2026, 3, 6)
        tz = ZoneInfo("Europe/Berlin")
        as_of = datetime(2026, 3, 5, 12, 0, tzinfo=tz)

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

        updates = detect_auto_inactive(
            daily,
            cycle_start,
            cycle_end,
            as_of=as_of,
            tz=tz,
            streak_required=4,
        )
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

        updates = detect_auto_inactive(
            daily,
            cycle_start,
            cycle_end,
            as_of=as_of,
            tz=tz,
            streak_required=4,
        )
        self.assertEqual(updates, {})

    def test_fourth_miss_only_triggers_after_window_closes(self):
        cycle_start = date(2026, 3, 1)
        cycle_end = date(2026, 3, 7)
        tz = ZoneInfo("Europe/Berlin")
        as_of_before_close = datetime(2026, 3, 5, 11, 59, tzinfo=tz)
        as_of_at_close = datetime(2026, 3, 5, 12, 0, tzinfo=tz)

        daily = {
            "p1": {
                date(2026, 3, 1): DailyScore(points=-3, participated=False),
                date(2026, 3, 2): DailyScore(points=-3, participated=False),
                date(2026, 3, 3): DailyScore(points=-3, participated=False),
                date(2026, 3, 4): DailyScore(points=-3, participated=False),
                date(2026, 3, 5): DailyScore(points=-3, participated=False),
                date(2026, 3, 6): DailyScore(points=-3, participated=False),
                date(2026, 3, 7): DailyScore(points=-3, participated=False),
            }
        }

        updates_before_close = detect_auto_inactive(
            daily,
            cycle_start,
            cycle_end,
            as_of=as_of_before_close,
            tz=tz,
            streak_required=4,
        )
        self.assertEqual(updates_before_close, {})

        updates_at_close = detect_auto_inactive(
            daily,
            cycle_start,
            cycle_end,
            as_of=as_of_at_close,
            tz=tz,
            streak_required=4,
        )
        self.assertEqual(updates_at_close, {"p1": date(2026, 3, 5)})

    def test_streak_resets_on_participation(self):
        cycle_start = date(2026, 3, 1)
        cycle_end = date(2026, 3, 7)
        tz = ZoneInfo("Europe/Berlin")
        as_of = datetime(2026, 3, 8, 12, 0, tzinfo=tz)

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

        updates = detect_auto_inactive(
            daily,
            cycle_start,
            cycle_end,
            as_of=as_of,
            tz=tz,
            streak_required=4,
        )
        self.assertNotIn("p1", updates)

    def test_no_inactivity_transition_outside_cycle(self):
        cycle_start = date(2026, 3, 1)
        cycle_end = date(2026, 3, 4)
        tz = ZoneInfo("Europe/Berlin")
        as_of = datetime(2026, 3, 5, 12, 0, tzinfo=tz)

        daily = {
            "p1": {
                date(2026, 3, 1): DailyScore(points=-3, participated=False),
                date(2026, 3, 2): DailyScore(points=-3, participated=False),
                date(2026, 3, 3): DailyScore(points=-3, participated=False),
                date(2026, 3, 4): DailyScore(points=-3, participated=False),
            }
        }

        updates = detect_auto_inactive(
            daily,
            cycle_start,
            cycle_end,
            as_of=as_of,
            tz=tz,
            streak_required=4,
        )
        self.assertEqual(updates, {})


if __name__ == "__main__":
    unittest.main()
