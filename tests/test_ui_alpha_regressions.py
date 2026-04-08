"""UI regression tests for alpha-discovered failures."""

import unittest

from src.ui.app import create_app


class UiAlphaRegressionTests(unittest.TestCase):
    """Regression coverage for Flask request paths exposed by alpha."""

    def setUp(self) -> None:
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()


if __name__ == "__main__":
    unittest.main()