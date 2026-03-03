import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

from gymchallenge.models import Submission
from gymchallenge.scoring_engine import compute_daily_scores


BERLIN = ZoneInfo("Europe/Berlin")


class TestScoringEngine(unittest.TestCase):

    def test_missing_submission_gets_penalty(self):
        cycle_start = date(2026, 3, 1)
        cycle_end = date(2026, 3, 3)

        submissions = []  # no one submitted

        result = compute_daily_scores(
            participant_ids=["p1"],
            submissions=submissions,
            tz=BERLIN,
            cycle_start=cycle_start,
            cycle_end=cycle_end,
            missing_points=-3,
        )

        # 3 score days, each should be -3
        self.assertEqual(result["p1"][date(2026, 3, 1)].points, -3)
        self.assertFalse(result["p1"][date(2026, 3, 1)].participated)

        self.assertEqual(result["p1"][date(2026, 3, 2)].points, -3)
        self.assertFalse(result["p1"][date(2026, 3, 2)].participated)

        self.assertEqual(result["p1"][date(2026, 3, 3)].points, -3)
        self.assertFalse(result["p1"][date(2026, 3, 3)].participated)

    def test_valid_submission_overrides_missing(self):
        cycle_start = date(2026, 3, 1)
        cycle_end = date(2026, 3, 1)

        submissions = [
            Submission(
                submission_id="s1",
                cycle_id="c1",
                participant_id="p1",
                submitted_at=datetime.fromisoformat("2026-03-01T20:00:00+01:00"),
                points=5,
                source="manual",
            )
        ]

        result = compute_daily_scores(
            participant_ids=["p1"],
            submissions=submissions,
            tz=BERLIN,
            cycle_start=cycle_start,
            cycle_end=cycle_end,
            missing_points=-3,
        )

        self.assertEqual(result["p1"][date(2026, 3, 1)].points, 5)
        self.assertTrue(result["p1"][date(2026, 3, 1)].participated)

    def test_duplicate_submissions_keep_earliest_valid(self):
        cycle_start = date(2026, 3, 1)
        cycle_end = date(2026, 3, 1)

        submissions = [
            Submission(
                submission_id="s_early",
                cycle_id="c1",
                participant_id="p1",
                submitted_at=datetime.fromisoformat("2026-03-01T20:01:00+01:00"),
                points=2,
                source="manual",
            ),
            Submission(
                submission_id="s_late",
                cycle_id="c1",
                participant_id="p1",
                submitted_at=datetime.fromisoformat("2026-03-01T20:05:00+01:00"),
                points=5,
                source="manual",
            ),
        ]

        result = compute_daily_scores(
            participant_ids=["p1"],
            submissions=submissions,
            tz=BERLIN,
            cycle_start=cycle_start,
            cycle_end=cycle_end,
            missing_points=-3,
        )

        # Earliest wins => 2
        self.assertEqual(result["p1"][date(2026, 3, 1)].points, 2)
        self.assertTrue(result["p1"][date(2026, 3, 1)].participated)

if __name__ == "__main__":
    unittest.main()
