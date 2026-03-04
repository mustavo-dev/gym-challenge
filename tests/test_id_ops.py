import unittest

from gymchallenge.id_ops import new_submission_id


class TestIdOps(unittest.TestCase):
    def test_submission_id_prefix(self):
        sid = new_submission_id()
        self.assertTrue(sid.startswith("sub_"))

    def test_submission_ids_unique(self):
        ids = {new_submission_id() for _ in range(200)}
        self.assertEqual(len(ids), 200)


if __name__ == "__main__":
    unittest.main()
