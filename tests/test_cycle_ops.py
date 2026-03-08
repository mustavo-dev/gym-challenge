import unittest

from gymchallenge.cycle_ops import build_cycle_id, build_cycle_name, has_active_cycle, has_cycle_id


class TestCycleOps(unittest.TestCase):
    def test_build_cycle_id(self):
        self.assertEqual(build_cycle_id("fall", 2026), "fall26")
        self.assertEqual(build_cycle_id("Spring", 2027), "spring27")

    def test_build_cycle_name(self):
        self.assertEqual(build_cycle_name("fall", 2026), "Fall 2026")
        self.assertEqual(build_cycle_name("winter", 2027), "Winter 2027")

    def test_has_active_cycle(self):
        rows = [
            {"cycle_id": "spring26", "active": False},
            {"cycle_id": "fall26", "active": True},
        ]
        self.assertTrue(has_active_cycle(rows))
        self.assertFalse(has_active_cycle([{"cycle_id": "spring26", "active": False}]))

    def test_invalid_season_raises(self):
        with self.assertRaises(ValueError):
            build_cycle_id("monsoon", 2026)

    def test_has_cycle_id(self):
        rows = [
            {"cycle_id": "fall26", "active": True},
            {"cycle_id": "spring27", "active": False},
        ]
        self.assertTrue(has_cycle_id(rows, "fall26"))
        self.assertFalse(has_cycle_id(rows, "summer26"))

if __name__ == "__main__":
    unittest.main()
