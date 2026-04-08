"""UI regression tests for alpha-discovered failures."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.ui.app import create_app


class UiAlphaRegressionTests(unittest.TestCase):
    """Regression coverage for Flask request paths exposed by alpha."""

    def setUp(self) -> None:
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_submit_rejects_invalid_window_when_score_day_is_none(self) -> None:
        """An invalid scoring-window submission must not be written to storage."""
        context = {
            "submit_enabled": True,
            "active_cycle": SimpleNamespace(cycle_id="spring26"),
            "participant_choices": [
                {"participant_id": "walker-luke-01"},
            ],
            "submit_message": "",
        }

        with patch(
            "src.ui.routes.participant_routes.get_submit_page_context",
            return_value=context,
        ), patch(
            "src.gymchallenge.data_paths.data_path",
            return_value="/tmp/submissions.json",
        ), patch(
            "src.gymchallenge.storage_json.load_list",
            return_value=[],
        ), patch(
            "src.gymchallenge.loaders.load_submissions",
            return_value=[],
        ), patch(
            "src.gymchallenge.scoring_time.score_day_for_timestamp",
            return_value=None,
        ), patch(
            "src.gymchallenge.id_ops.new_submission_id",
            return_value="sub-001",
        ) as mock_new_submission_id, patch(
            "src.gymchallenge.storage_ops.append_row",
        ) as mock_append_row:
            response = self.client.post(
                "/submit",
                data={
                    "participant_id": "walker-luke-01",
                    "points": "3",
                },
            )

        self.assertEqual(response.status_code, 302)
        mock_new_submission_id.assert_not_called()
        mock_append_row.assert_not_called()


if __name__ == "__main__":
    unittest.main()