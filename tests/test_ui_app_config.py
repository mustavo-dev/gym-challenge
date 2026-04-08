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

    def test_create_app_loads_challenge_name_from_instance_config(self) -> None:
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            instance_dir = os.path.join(tmpdir, "instance")
            os.makedirs(instance_dir, exist_ok=True)

            config_path = os.path.join(instance_dir, "config.py")
            with open(config_path, "w", encoding="utf-8") as handle:
                handle.write('CHALLENGE_NAME = "Instance Challenge"\n')

            app = create_app(instance_path=instance_dir)
            app.config["TESTING"] = True

            client = app.test_client()
            response = client.get("/")

            self.assertEqual(response.status_code, 200)
            html = response.data.decode("utf-8")
            self.assertIn("<h1>Instance Challenge</h1>", html)


if __name__ == "__main__":
    unittest.main()