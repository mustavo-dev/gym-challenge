"""Tests for UI config helper functions."""

import unittest

from src.ui.app import create_app


class UiConfigHelperTests(unittest.TestCase):
    """Small tests for config-driven UI helpers."""

    def test_get_ui_timezone_uses_configured_gym_timezone(self) -> None:
        app = create_app()
        app.config["TESTING"] = True
        app.config["GYM_TIMEZONE"] = "America/New_York"

        with app.app_context():
            from src.ui.config import get_ui_timezone

            tz = get_ui_timezone()

        self.assertEqual(str(tz), "America/New_York")

    def test_get_admin_actor_name_uses_configured_admin_name(self) -> None:
        app = create_app()
        app.config["TESTING"] = True
        app.config["ADMIN_NAME"] = "Jayme"

        with app.app_context():
            from src.ui.config import get_admin_actor_name

            actor = get_admin_actor_name()

        self.assertEqual(actor, "Jayme")

if __name__ == "__main__":
    unittest.main()