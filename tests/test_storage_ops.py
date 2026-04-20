import os
import tempfile
import unittest

from src.gymchallenge.storage_ops import append_row
from src.gymchallenge.storage_json import load_list


class TestStorageOps(unittest.TestCase):
    def test_append_row_creates_file_and_appends(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "items.json")
            append_row(path, {"x": 1})
            append_row(path, {"x": 2})

            self.assertEqual(load_list(path), [{"x": 1}, {"x": 2}])


if __name__ == "__main__":
    unittest.main()
