"""Tests for non-Flask runtime config helpers."""

import os
import tempfile
import unittest


class RuntimeConfigTests(unittest.TestCase):
    """Small tests for shared runtime config loading."""

    def test_get_runtime_timezone_uses_instance_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            instance_dir = os.path.join(tmpdir, "instance")
            os.makedirs(instance_dir, exist_ok=True)

            config_path = os.path.join(instance_dir, "config.py")
            with open(config_path, "w", encoding="utf-8") as handle:
                handle.write('GYM_TIMEZONE = "America/New_York"\n')

            from src.gymchallenge.runtime_config import get_runtime_timezone

            tz = get_runtime_timezone(instance_dir)

        self.assertEqual(str(tz), "America/New_York")


if __name__ == "__main__":
    unittest.main()