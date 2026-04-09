import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

from src.gymchallenge.models import Cycle
from src.gymchallenge.cycle_timeline import (
    cycle_window_start,
    cycle_window_end,
    cycle_status,
    cycle_overlaps_existing,
)

BERLIN = ZoneInfo("Europe/Berlin")


class TestCycleTimeline(unittest.TestCase):
    def make_cycle(self, cycle_id: str, name: str, start_day: str, end_day: str) -> Cycle:
        return Cycle(
            cycle_id=cycle_id,
            name=name,
            start_day=date.fromisoformat(start_day),
            end_day=date.fromisoformat(end_day),
            created_at=datetime.fromisoformat("2026-03-08T17:00:00+01:00"),
            active=True,  # legacy field still present for now
        )

    def test_cycle_window_start(self):
        cycle = self.make_cycle("fall26", "Fall 2026", "2026-09-01", "2026-11-30")
        self.assertEqual(
            cycle_window_start(cycle, BERLIN).isoformat(),
            "2026-09-01T20:00:00+02:00",
        )

    def test_cycle_window_end(self):
        cycle = self.make_cycle("fall26", "Fall 2026", "2026-09-01", "2026-11-30")
        self.assertEqual(
            cycle_window_end(cycle, BERLIN).isoformat(),
            "2026-12-01T12:00:00+01:00",
        )

    def test_cycle_status_planned(self):
        cycle = self.make_cycle("fall26", "Fall 2026", "2026-09-01", "2026-11-30")
        now = datetime.fromisoformat("2026-09-01T19:59:00+02:00")
        self.assertEqual(cycle_status(cycle, now, BERLIN), "planned")

    def test_cycle_status_active(self):
        cycle = self.make_cycle("fall26", "Fall 2026", "2026-09-01", "2026-11-30")
        now = datetime.fromisoformat("2026-09-01T20:00:00+02:00")
        self.assertEqual(cycle_status(cycle, now, BERLIN), "active")

    def test_cycle_status_closed(self):
        cycle = self.make_cycle("fall26", "Fall 2026", "2026-09-01", "2026-11-30")
        now = datetime.fromisoformat("2026-12-01T12:00:00+01:00")
        self.assertEqual(cycle_status(cycle, now, BERLIN), "closed")

    def test_cycle_overlap_detected(self):
        existing = [
            self.make_cycle("fall26", "Fall 2026", "2026-09-01", "2026-11-30"),
        ]
        new_cycle = self.make_cycle("winter26", "Winter 2026", "2026-11-15", "2027-02-28")
        self.assertTrue(cycle_overlaps_existing(new_cycle, existing, BERLIN))

    def test_cycle_overlap_not_detected(self):
        existing = [
            self.make_cycle("fall26", "Fall 2026", "2026-09-01", "2026-11-30"),
        ]
        new_cycle = self.make_cycle("winter26", "Winter 2026", "2026-12-01", "2027-02-28")
        self.assertFalse(cycle_overlaps_existing(new_cycle, existing, BERLIN))


if __name__ == "__main__":
    unittest.main()
