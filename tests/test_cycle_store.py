import unittest

from src.gymchallenge.cycle_store import find_cycle_row


class TestCycleStore(unittest.TestCase):
    def test_find_cycle_row(self):
        rows = [
            {"cycle_id": "fall26", "name": "Fall 2026"},
            {"cycle_id": "winter26", "name": "Winter 2026"},
        ]

        row = find_cycle_row(rows, "winter26")
        self.assertIsNotNone(row)
        self.assertEqual(row["name"], "Winter 2026")

        self.assertIsNone(find_cycle_row(rows, "spring27"))


if __name__ == "__main__":
    unittest.main()
