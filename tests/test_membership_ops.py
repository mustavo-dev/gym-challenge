import unittest

from gymchallenge.membership_ops import has_membership


class TestMembershipOps(unittest.TestCase):
    def test_has_membership(self):
        rows = [
            {"cycle_id": "c1", "participant_id": "p1"},
            {"cycle_id": "c2", "participant_id": "p1"},
        ]
        self.assertTrue(has_membership(rows, "c1", "p1"))
        self.assertFalse(has_membership(rows, "c1", "p2"))


if __name__ == "__main__":
    unittest.main()
