import unittest
from datetime import date
from zoneinfo import ZoneInfo

from src.gymchallenge.demo_data_generator import (
    generate_demo_participants,
    generate_demo_memberships,
    generate_demo_submissions,
)

BERLIN = ZoneInfo("Europe/Berlin")


class TestDemoDataGenerator(unittest.TestCase):
    def test_participants_are_deterministic(self):
        a = generate_demo_participants(count=10, seed=42)
        b = generate_demo_participants(count=10, seed=42)
        self.assertEqual(a, b)

    def test_participant_count(self):
        rows = generate_demo_participants(count=15, seed=42)
        self.assertEqual(len(rows), 15)

    def test_membership_count_matches_participants(self):
        participants = generate_demo_participants(count=12, seed=42)
        memberships = generate_demo_memberships("fall26", participants)
        self.assertEqual(len(memberships), 12)

    def test_submissions_are_deterministic(self):
        participants = generate_demo_participants(count=5, seed=42)

        a = generate_demo_submissions(
            cycle_id="fall26",
            participant_rows=participants,
            from_day=date(2026, 9, 1),
            to_day=date(2026, 9, 3),
            seed=99,
            miss_rate=0.2,
            tz=BERLIN,
        )

        b = generate_demo_submissions(
            cycle_id="fall26",
            participant_rows=participants,
            from_day=date(2026, 9, 1),
            to_day=date(2026, 9, 3),
            seed=99,
            miss_rate=0.2,
            tz=BERLIN,
        )

        self.assertEqual(a, b)

    def test_submissions_respect_cycle_id(self):
        participants = generate_demo_participants(count=3, seed=42)
        rows = generate_demo_submissions(
            cycle_id="fall26",
            participant_rows=participants,
            from_day=date(2026, 9, 1),
            to_day=date(2026, 9, 1),
            seed=99,
            miss_rate=0.0,
            tz=BERLIN,
        )

        self.assertTrue(all(r["cycle_id"] == "fall26" for r in rows))
        self.assertEqual(len(rows), 3)


if __name__ == "__main__":
    unittest.main()
