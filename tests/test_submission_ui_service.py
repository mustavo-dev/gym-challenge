"""Tests for the admin submissions UI service."""

import unittest

from src.ui.services.submission_ui_service import filter_and_sort_submissions_for_view
from src.ui.app import create_app


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

    def test_get_submissions_for_list_includes_raw_timestamp_key(self) -> None:
        """Submission list rows should expose the raw timestamp key used by sorting."""
        from datetime import datetime
        from types import SimpleNamespace
        from unittest.mock import patch

        fake_submission = SimpleNamespace(
            submission_id="sub-001",
            participant_id="alpha-01",
            submitted_at=datetime.fromisoformat("2026-03-16T20:05:00+01:00"),
            points=3,
            source="ui",
        )

        app = create_app()
        app.config["TESTING"] = True
        app.config["GYM_TIMEZONE"] = "Europe/Berlin"

        with app.app_context():
            with patch(
                "src.ui.services.submission_ui_service.load_list",
                side_effect=[[], []],
            ), patch(
                "src.ui.services.submission_ui_service.load_submissions",
                return_value=[fake_submission],
            ), patch(
                "src.ui.services.submission_ui_service.build_display_name_map",
                return_value={"alpha-01": "Alpha"},
            ):
                from src.ui.services.submission_ui_service import get_submissions_for_list

                rows = get_submissions_for_list()

        self.assertEqual(len(rows), 1)
        self.assertIn("submitted_at_raw", rows[0])
        self.assertEqual(rows[0]["submitted_at_raw"], "2026-03-16T20:05:00+01:00")

    def test_get_submissions_for_list_includes_score_day(self) -> None:
        """Submission rows should expose the derived score day for admin auditability."""
        from datetime import datetime
        from types import SimpleNamespace
        from unittest.mock import patch

        fake_submission = SimpleNamespace(
            submission_id="sub-001",
            participant_id="alpha-01",
            submitted_at=datetime.fromisoformat("2026-03-16T08:05:00+01:00"),
            points=3,
            source="ui",
        )

        app = create_app()
        app.config["TESTING"] = True
        app.config["GYM_TIMEZONE"] = "Europe/Berlin"

        with app.app_context():
            with patch(
                "src.ui.services.submission_ui_service.load_list",
                side_effect=[[], []],
            ), patch(
                "src.ui.services.submission_ui_service.load_submissions",
                return_value=[fake_submission],
            ), patch(
                "src.ui.services.submission_ui_service.build_display_name_map",
                return_value={"alpha-01": "Alpha"},
            ):
                from src.ui.services.submission_ui_service import get_submissions_for_list

                rows = get_submissions_for_list()

        self.assertEqual(len(rows), 1)
        self.assertIn("score_day", rows[0])
        self.assertEqual(rows[0]["score_day"], "2026-03-15")


if __name__ == "__main__":
    unittest.main()