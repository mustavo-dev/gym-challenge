"""Tests for UI app configuration behavior."""

import unittest

from src.ui.app import create_app


class UiAppConfigTests(unittest.TestCase):
    """Small config-groundwork tests for the Flask UI app."""

    def test_home_uses_configured_challenge_name_in_base_template(self) -> None:
        app = create_app()
        app.config["TESTING"] = True
        app.config["CHALLENGE_NAME"] = "Test Challenge"

        client = app.test_client()
        response = client.get("/")

        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("<h1>Test Challenge</h1>", html)

    def test_home_title_uses_configured_challenge_name(self) -> None:
        app = create_app()
        app.config["TESTING"] = True
        app.config["CHALLENGE_NAME"] = "Test Challenge"

        client = app.test_client()
        response = client.get("/")

        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("<title>Test Challenge UI</title>", html)


if __name__ == "__main__":
    unittest.main()