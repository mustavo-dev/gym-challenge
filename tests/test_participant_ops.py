import unittest

from src.gymchallenge.participant_ops import generate_participant_id


class TestParticipantOps(unittest.TestCase):

    def test_first_id(self):
        rows = []
        pid = generate_participant_id("John", "Smith", rows)
        self.assertEqual(pid, "smith-john-01")

    def test_collision(self):
        rows = [
            {"participant_id": "smith-john-01"},
            {"participant_id": "smith-john-02"},
        ]

        pid = generate_participant_id("John", "Smith", rows)
        self.assertEqual(pid, "smith-john-03")


if __name__ == "__main__":
    unittest.main()
