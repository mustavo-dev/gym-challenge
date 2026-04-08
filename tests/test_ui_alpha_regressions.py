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

    def test_correction_rejects_non_member_for_matching_cycle(self) -> None:
        """A correction must not be written for a participant outside the cycle."""
        with patch(
            "src.ui.routes.admin_routes.find_cycle_id_for_score_day",
            return_value="spring26",
        ), patch(
            "src.gymchallenge.data_paths.data_path",
            return_value="/tmp/mock.json",
        ), patch(
            "src.gymchallenge.storage_json.load_list",
            return_value=[],
        ), patch(
            "src.gymchallenge.id_ops.new_correction_id",
            return_value="cor-001",
        ) as mock_new_correction_id, patch(
            "src.gymchallenge.storage_ops.append_row",
        ) as mock_append_row:
            response = self.client.post(
                "/admin/corrections",
                data={
                    "participant_id": "frank-test-01",
                    "score_day": "2026-03-17",
                    "new_points": "2",
                    "reason": "alpha regression",
                },
            )

        self.assertEqual(response.status_code, 302)
        mock_new_correction_id.assert_not_called()
        mock_append_row.assert_not_called()

    def test_leaderboard_report_exports_display_name_only(self) -> None:
        """Leaderboard CSV should exclude participant_id and show display name only."""
        from datetime import date

        selected_cycle = SimpleNamespace(
            cycle_id="spring26",
            start_day=date(2026, 3, 10),
            end_day=date(2026, 3, 30),
        )
        membership = SimpleNamespace(
            cycle_id="spring26",
            participant_id="walker-luke-01",
        )

        with patch(
            "src.gymchallenge.data_paths.data_path",
            return_value="/tmp/mock.json",
        ), patch(
            "src.gymchallenge.storage_json.load_list",
            return_value=[],
        ), patch(
            "src.gymchallenge.loaders.load_cycles",
            return_value=[selected_cycle],
        ), patch(
            "src.gymchallenge.loaders.load_memberships",
            return_value=[membership],
        ), patch(
            "src.gymchallenge.loaders.load_membership_events",
            return_value=[],
        ), patch(
            "src.gymchallenge.loaders.load_submissions",
            return_value=[],
        ), patch(
            "src.gymchallenge.loaders.load_corrections",
            return_value=[],
        ), patch(
            "src.gymchallenge.display_names.build_display_name_map",
            return_value={"walker-luke-01": "Luke Walker"},
        ), patch(
            "src.gymchallenge.scoring_engine.compute_daily_scores",
            return_value={},
        ), patch(
            "src.gymchallenge.scoring_engine.build_leaderboard",
            return_value=[("walker-luke-01", 9)],
        ):
            response = self.client.post(
                "/admin/reports",
                data={
                    "cycle_id": "spring26",
                    "report_type": "leaderboard",
                },
            )

        self.assertEqual(response.status_code, 200)
        csv_text = response.data.decode("utf-8")
        header = csv_text.splitlines()[0]
        self.assertEqual(header, "rank,display_name,total_points")
        self.assertNotIn("walker-luke-01", csv_text)

    def test_leaderboard_report_excludes_archived_participants(self) -> None:
        """Leaderboard CSV should exclude archived participants."""
        from datetime import date

        selected_cycle = SimpleNamespace(
            cycle_id="spring26",
            start_day=date(2026, 3, 10),
            end_day=date(2026, 3, 30),
        )
        membership = SimpleNamespace(
            cycle_id="spring26",
            participant_id="walker-luke-01",
        )

        with patch(
            "src.gymchallenge.data_paths.data_path",
            return_value="/tmp/mock.json",
        ), patch(
            "src.gymchallenge.storage_json.load_list",
            side_effect=[
                [],  # cycles.json
                [],  # memberships.json
                [],  # membership_events.json
                [],  # submissions.json
                [],  # corrections.json
                [
                    {
                        "participant_id": "walker-luke-01",
                        "first_name": "Luke",
                        "last_name": "Walker",
                        "archived": True,
                    }
                ],  # participants.json
            ],
        ), patch(
            "src.gymchallenge.loaders.load_cycles",
            return_value=[selected_cycle],
        ), patch(
            "src.gymchallenge.loaders.load_memberships",
            return_value=[membership],
        ), patch(
            "src.gymchallenge.loaders.load_membership_events",
            return_value=[],
        ), patch(
            "src.gymchallenge.loaders.load_submissions",
            return_value=[],
        ), patch(
            "src.gymchallenge.loaders.load_corrections",
            return_value=[],
        ), patch(
            "src.gymchallenge.display_names.build_display_name_map",
            return_value={"walker-luke-01": "Luke Walker"},
        ), patch(
            "src.gymchallenge.scoring_engine.compute_daily_scores",
            return_value={},
        ), patch(
            "src.gymchallenge.scoring_engine.build_leaderboard",
            return_value=[("walker-luke-01", 9)],
        ):
            response = self.client.post(
                "/admin/reports",
                data={
                    "cycle_id": "spring26",
                    "report_type": "leaderboard",
                },
            )

        self.assertEqual(response.status_code, 200)
        csv_text = response.data.decode("utf-8")
        self.assertEqual(csv_text.splitlines(), ["rank,display_name,total_points"])

    def test_active_cycle_report_uses_elapsed_days_only(self) -> None:
        """Active-cycle leaderboard reports should stop at the current score day."""
        from datetime import date, datetime
        from zoneinfo import ZoneInfo

        selected_cycle = SimpleNamespace(
            cycle_id="spring26",
            start_day=date(2026, 3, 10),
            end_day=date(2026, 3, 30),
        )
        membership = SimpleNamespace(
            cycle_id="spring26",
            participant_id="walker-luke-01",
        )

        fake_now = datetime(2026, 3, 16, 21, 0, tzinfo=ZoneInfo("Europe/Berlin"))

        class FixedDateTime:
            @classmethod
            def now(cls, tz=None):
                return fake_now if tz is not None else fake_now.replace(tzinfo=None)

        with patch(
            "datetime.datetime",
            FixedDateTime,
        ), patch(
            "src.gymchallenge.data_paths.data_path",
            return_value="/tmp/mock.json",
        ), patch(
            "src.gymchallenge.storage_json.load_list",
            return_value=[],
        ), patch(
            "src.gymchallenge.loaders.load_cycles",
            return_value=[selected_cycle],
        ), patch(
            "src.gymchallenge.loaders.load_memberships",
            return_value=[membership],
        ), patch(
            "src.gymchallenge.loaders.load_membership_events",
            return_value=[],
        ), patch(
            "src.gymchallenge.loaders.load_submissions",
            return_value=[],
        ), patch(
            "src.gymchallenge.loaders.load_corrections",
            return_value=[],
        ), patch(
            "src.gymchallenge.display_names.build_display_name_map",
            return_value={"walker-luke-01": "Luke Walker"},
        ), patch(
            "src.gymchallenge.scoring_engine.compute_daily_scores",
            return_value={},
        ) as mock_compute_daily_scores, patch(
            "src.gymchallenge.scoring_engine.build_leaderboard",
            return_value=[("walker-luke-01", 9)],
        ) as mock_build_leaderboard:
            response = self.client.post(
                "/admin/reports",
                data={
                    "cycle_id": "spring26",
                    "report_type": "leaderboard",
                },
            )

        self.assertEqual(response.status_code, 200)

        expected_to_day = date(2026, 3, 16)

        self.assertEqual(
            mock_compute_daily_scores.call_args.kwargs["cycle_end"],
            expected_to_day,
        )
        self.assertEqual(
            mock_build_leaderboard.call_args.kwargs["to_day"],
            expected_to_day,
        )

    def test_admin_submissions_page_displays_score_day(self) -> None:
        """Admin submissions page should render the derived score day."""
        with patch(
            "src.ui.routes.admin_routes.get_submissions_for_list",
            return_value=[
                {
                    "submission_id": "sub-001",
                    "participant_id": "alpha-01",
                    "display_name": "Alpha",
                    "show_participant_id": False,
                    "submitted_display": "2026-03-16 08:05+01:00",
                    "submitted_at_raw": "2026-03-16T08:05:00+01:00",
                    "score_day": "2026-03-15",
                    "points": 3,
                    "source": "ui",
                }
            ],
        ), patch(
            "src.ui.routes.admin_routes.filter_and_sort_submissions_for_view",
            side_effect=lambda submissions, participant_id, points_value, sort_value: submissions,
        ), patch(
            "src.ui.routes.admin_routes.get_participant_choices",
            return_value=[],
        ):
            response = self.client.get("/admin/submissions")

        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("2026-03-15", html)

    def test_submit_success_page_shows_human_readable_recorded_timestamp(self) -> None:
        """Successful submit flow should show the recorded timestamp in human-readable form."""
        from datetime import date, datetime
        from zoneinfo import ZoneInfo

        context = {
            "submit_enabled": True,
            "active_cycle": SimpleNamespace(cycle_id="spring26", name="Spring 2026"),
            "participant_choices": [
                {"participant_id": "walker-luke-01", "display_name": "Luke Walker"},
            ],
            "submit_message": "",
        }

        fake_now = datetime(2026, 3, 16, 8, 5, tzinfo=ZoneInfo("Europe/Berlin"))

        from datetime import datetime as RealDateTime

        class FixedDateTime(RealDateTime):
            @classmethod
            def now(cls, tz=None):
                return fake_now if tz is not None else fake_now.replace(tzinfo=None)

        with patch(
            "datetime.datetime",
            FixedDateTime,
        ), patch(
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
            return_value=date(2026, 3, 15),
        ), patch(
            "src.gymchallenge.id_ops.new_submission_id",
            return_value="sub-001",
        ), patch(
            "src.gymchallenge.storage_ops.append_row",
        ):
            response = self.client.post(
                "/submit",
                data={
                    "participant_id": "walker-luke-01",
                    "points": "3",
                },
                follow_redirects=True,
            )

        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("Recorded at: 2026-03-16 08:05 CET", html)

    def test_corrections_page_filters_participant_choices_by_score_day_cycle(self) -> None:
        """Corrections page should only offer members of the score day's cycle."""
        with patch(
            "src.ui.routes.admin_routes.get_corrections_for_list",
            return_value=[],
        ), patch(
            "src.ui.routes.admin_routes.find_cycle_id_for_score_day",
            return_value="spring26",
        ), patch(
            "src.ui.routes.admin_routes.get_participant_choices",
            return_value=[
                {"participant_id": "member-01", "display_name": "Member One"},
                {"participant_id": "outsider-01", "display_name": "Outsider One"},
            ],
        ), patch(
            "src.gymchallenge.data_paths.data_path",
            return_value="/tmp/mock.json",
        ), patch(
            "src.gymchallenge.storage_json.load_list",
            side_effect=[
                [
                    {"cycle_id": "spring26", "participant_id": "member-01"},
                    {"cycle_id": "other26", "participant_id": "outsider-01"},
                ],
            ],
        ):
            response = self.client.get("/admin/corrections?score_day=2026-03-17")

        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("Member One", html)
        self.assertNotIn("Outsider One", html)

    def test_corrections_page_preserves_score_day_and_shows_filter_form(self) -> None:
        """Corrections page should preserve score_day and provide a GET filter path."""
        with patch(
            "src.ui.routes.admin_routes.get_corrections_for_list",
            return_value=[],
        ), patch(
            "src.ui.routes.admin_routes.get_participant_choices",
            return_value=[],
        ):
            response = self.client.get("/admin/corrections?score_day=2026-03-17")

        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn('method="get"', html)
        self.assertIn('value="2026-03-17"', html)
        self.assertIn("Load Eligible Participants", html)

    def test_submit_success_uses_configured_gym_timezone(self) -> None:
        """Submit success message should use the configured gym timezone."""
        from datetime import date, datetime as RealDateTime

        self.app.config["GYM_TIMEZONE"] = "America/New_York"

        context = {
            "submit_enabled": True,
            "active_cycle": SimpleNamespace(cycle_id="spring26", name="Spring 2026"),
            "participant_choices": [
                {"participant_id": "walker-luke-01", "display_name": "Luke Walker"},
            ],
            "submit_message": "",
        }

        class FixedDateTime(RealDateTime):
            @classmethod
            def now(cls, tz=None):
                if tz is None:
                    return cls(2026, 3, 16, 8, 5)
                return cls(2026, 3, 16, 8, 5, tzinfo=tz)

        with patch(
            "datetime.datetime",
            FixedDateTime,
        ), patch(
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
            return_value=date(2026, 3, 15),
        ), patch(
            "src.gymchallenge.id_ops.new_submission_id",
            return_value="sub-001",
        ), patch(
            "src.gymchallenge.storage_ops.append_row",
        ):
            response = self.client.post(
                "/submit",
                data={
                    "participant_id": "walker-luke-01",
                    "points": "3",
                },
                follow_redirects=True,
            )

        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("Recorded at: 2026-03-16 08:05 EDT", html)

    def test_active_cycle_report_uses_configured_gym_timezone(self) -> None:
        """Active-cycle report cutoff should use configured gym timezone."""
        from datetime import date, datetime as RealDateTime

        self.app.config["GYM_TIMEZONE"] = "America/New_York"

        selected_cycle = SimpleNamespace(
            cycle_id="spring26",
            start_day=date(2026, 3, 10),
            end_day=date(2026, 3, 30),
        )
        membership = SimpleNamespace(
            cycle_id="spring26",
            participant_id="walker-luke-01",
        )

        class FixedDateTime(RealDateTime):
            @classmethod
            def now(cls, tz=None):
                if tz is None:
                    return cls(2026, 3, 16, 21, 0)
                return cls(2026, 3, 16, 21, 0, tzinfo=tz)

        with patch(
            "datetime.datetime",
            FixedDateTime,
        ), patch(
            "src.gymchallenge.data_paths.data_path",
            return_value="/tmp/mock.json",
        ), patch(
            "src.gymchallenge.storage_json.load_list",
            return_value=[],
        ), patch(
            "src.gymchallenge.loaders.load_cycles",
            return_value=[selected_cycle],
        ), patch(
            "src.gymchallenge.loaders.load_memberships",
            return_value=[membership],
        ), patch(
            "src.gymchallenge.loaders.load_membership_events",
            return_value=[],
        ), patch(
            "src.gymchallenge.loaders.load_submissions",
            return_value=[],
        ), patch(
            "src.gymchallenge.loaders.load_corrections",
            return_value=[],
        ), patch(
            "src.gymchallenge.display_names.build_display_name_map",
            return_value={"walker-luke-01": "Luke Walker"},
        ), patch(
            "src.gymchallenge.scoring_engine.compute_daily_scores",
            return_value={},
        ) as mock_compute_daily_scores, patch(
            "src.gymchallenge.scoring_engine.build_leaderboard",
            return_value=[("walker-luke-01", 9)],
        ):
            response = self.client.post(
                "/admin/reports",
                data={
                    "cycle_id": "spring26",
                    "report_type": "leaderboard",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            mock_compute_daily_scores.call_args.kwargs["tz"].key,
            "America/New_York",
        )

if __name__ == "__main__":
    unittest.main()