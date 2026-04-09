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

    def test_create_app_loads_additional_instance_config_values(self) -> None:
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            instance_dir = os.path.join(tmpdir, "instance")
            os.makedirs(instance_dir, exist_ok=True)

            config_path = os.path.join(instance_dir, "config.py")
            with open(config_path, "w", encoding="utf-8") as handle:
                handle.write('CHALLENGE_NAME = "Instance Challenge"\n')
                handle.write('GYM_NAME = "Test Gym"\n')
                handle.write('ADMIN_NAME = "Jayme"\n')
                handle.write('GYM_TIMEZONE = "Europe/Berlin"\n')

            app = create_app(instance_path=instance_dir)
            app.config["TESTING"] = True

            self.assertEqual(app.config["CHALLENGE_NAME"], "Instance Challenge")
            self.assertEqual(app.config["GYM_NAME"], "Test Gym")
            self.assertEqual(app.config["ADMIN_NAME"], "Jayme")
            self.assertEqual(app.config["GYM_TIMEZONE"], "Europe/Berlin")

    def test_create_app_sets_default_additional_config_values(self) -> None:
        app = create_app()
        app.config["TESTING"] = True

        self.assertEqual(app.config["GYM_NAME"], "Default Gym")
        self.assertEqual(app.config["ADMIN_NAME"], "Admin")
        self.assertEqual(app.config["GYM_TIMEZONE"], "UTC")

    def test_admin_dashboard_shows_configured_gym_name(self) -> None:
        app = create_app()
        app.config["TESTING"] = True
        app.config["GYM_NAME"] = "Test Gym"

        client = app.test_client()
        response = client.get("/admin")

        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("Gym: Test Gym", html)

    def test_admin_dashboard_shows_configured_admin_name(self) -> None:
        app = create_app()
        app.config["TESTING"] = True
        app.config["ADMIN_NAME"] = "Jayme"

        client = app.test_client()
        response = client.get("/admin")

        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("Admin: Jayme", html)

    def test_reports_page_shows_configured_admin_name(self) -> None:
        app = create_app()
        app.config["TESTING"] = True
        app.config["ADMIN_NAME"] = "Jayme"

        client = app.test_client()
        response = client.get("/admin/reports")

        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("Generate downloadable challenge reports for Jayme.", html)

    def test_create_app_loads_secret_key_from_instance_config(self) -> None:
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            instance_dir = os.path.join(tmpdir, "instance")
            os.makedirs(instance_dir, exist_ok=True)

            config_path = os.path.join(instance_dir, "config.py")
            with open(config_path, "w", encoding="utf-8") as handle:
                handle.write('SECRET_KEY = "instance-secret-key"\n')

            app = create_app(instance_path=instance_dir)
            app.config["TESTING"] = True

            self.assertEqual(app.secret_key, "instance-secret-key")

    def test_create_app_prefers_secret_key_from_environment(self) -> None:
        import os
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmpdir:
            instance_dir = os.path.join(tmpdir, "instance")
            os.makedirs(instance_dir, exist_ok=True)

            config_path = os.path.join(instance_dir, "config.py")
            with open(config_path, "w", encoding="utf-8") as handle:
                handle.write('SECRET_KEY = "instance-secret-key"\n')

            with patch.dict(os.environ, {"SECRET_KEY": "env-secret-key"}, clear=False):
                app = create_app(instance_path=instance_dir)
                app.config["TESTING"] = True

            self.assertEqual(app.secret_key, "env-secret-key")

if __name__ == "__main__":
    unittest.main()