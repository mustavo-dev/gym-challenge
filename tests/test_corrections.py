import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

from src.gymchallenge.models import Submission, Correction
from src.gymchallenge.scoring_engine import compute_daily_scores


BERLIN = ZoneInfo("Europe/Berlin")


class TestCorrections(unittest.TestCase):
    def test_correction_overrides_points_only(self):
        cycle_start = date(2026, 3, 1)
        cycle_end = date(2026, 3, 1)

        submissions = []  # no submission (miss)

        corrections = [
            Correction(
                correction_id="c1",
                cycle_id="cy1",
                participant_id="p1",
                score_day=date(2026, 3, 1),
                new_points=2,
                reason="Admin fix",
                created_at=datetime.fromisoformat("2026-03-02T10:00:00+01:00"),
                admin="jayme",
            )
        ]

        result = compute_daily_scores(
            participant_ids=["p1"],
            submissions=submissions,
            tz=BERLIN,
            cycle_start=cycle_start,
            cycle_end=cycle_end,
            missing_points=-3,
            corrections=corrections,
        )

        self.assertEqual(result["p1"][date(2026, 3, 1)].points, 2)
        self.assertFalse(result["p1"][date(2026, 3, 1)].participated)

    def test_latest_correction_wins(self):
        cycle_start = date(2026, 3, 1)
        cycle_end = date(2026, 3, 1)

        corrections = [
            Correction(
                correction_id="c1",
                cycle_id="cy1",
                participant_id="p1",
                score_day=date(2026, 3, 1),
                new_points=1,
                reason="First",
                created_at=datetime.fromisoformat("2026-03-02T09:00:00+01:00"),
                admin="jayme",
            ),
            Correction(
                correction_id="c2",
                cycle_id="cy1",
                participant_id="p1",
                score_day=date(2026, 3, 1),
                new_points=3,
                reason="Second",
                created_at=datetime.fromisoformat("2026-03-02T10:00:00+01:00"),
                admin="jayme",
            ),
        ]

        result = compute_daily_scores(
            participant_ids=["p1"],
            submissions=[],
            tz=BERLIN,
            cycle_start=cycle_start,
            cycle_end=cycle_end,
            missing_points=-3,
            corrections=corrections,
        )

        self.assertEqual(result["p1"][date(2026, 3, 1)].points, 3)


if __name__ == "__main__":
    unittest.main()
