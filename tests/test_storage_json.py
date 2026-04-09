import json
import os
import tempfile
import unittest

from src.gymchallenge.storage_json import load_list, save_list


class TestStorageJson(unittest.TestCase):
    def test_load_missing_file_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "missing.json")
            self.assertEqual(load_list(path), [])

    def test_save_then_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "rows.json")
            rows = [{"a": 1}, {"b": "x"}]

            save_list(path, rows)
            loaded = load_list(path)

            self.assertEqual(loaded, rows)

    def test_save_creates_parent_dir(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "nested", "rows.json")
            rows = [{"ok": True}]

            save_list(path, rows)
            self.assertTrue(os.path.exists(path))
            self.assertEqual(load_list(path), rows)


if __name__ == "__main__":
    unittest.main()
