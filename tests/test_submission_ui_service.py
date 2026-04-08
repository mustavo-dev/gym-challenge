"""Tests for the admin submissions UI service."""

import unittest

from src.ui.services.submission_ui_service import filter_and_sort_submissions_for_view


class SubmissionUiServiceTests(unittest.TestCase):
    """Regression tests for submissions display and sorting."""

    def test_newest_sort_uses_submission_timestamp_field(self) -> None:
        """Newest sort should order rows by their actual raw submission timestamp."""
        submissions = [
            {
                "submission_id": "sub-001",
                "participant_id": "alpha-01",
                "display_name": "Alpha",
                "submitted_display": "2026-03-16 20:05",
                "submitted_at_raw": "2026-03-16T20:05:00+01:00",
                "points": 3,
                "source": "ui",
            },
            {
                "submission_id": "sub-002",
                "participant_id": "bravo-01",
                "display_name": "Bravo",
                "submitted_display": "2026-03-17 08:10",
                "submitted_at_raw": "2026-03-17T08:10:00+01:00",
                "points": 4,
                "source": "ui",
            },
        ]

        rows = filter_and_sort_submissions_for_view(
            submissions=submissions,
            participant_id="",
            points_value="",
            sort_value="newest",
        )

        self.assertEqual(
            [row["submission_id"] for row in rows],
            ["sub-002", "sub-001"],
        )


if __name__ == "__main__":
    unittest.main()