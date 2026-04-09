import unittest

from src.gymchallenge.id_ops import new_submission_id, new_correction_id, new_membership_event_id

class TestIdOps(unittest.TestCase):
    def test_submission_id_prefix(self):
        sid = new_submission_id()
        self.assertTrue(sid.startswith("sub_"))

    def test_submission_ids_unique(self):
        ids = {new_submission_id() for _ in range(200)}
        self.assertEqual(len(ids), 200)

    def test_correction_id_prefix(self):
        cid = new_correction_id()
        self.assertTrue(cid.startswith("corr_"))

    def test_correction_ids_unique(self):
        ids = {new_correction_id() for _ in range(200)}
        self.assertEqual(len(ids), 200)

    def test_membership_event_id_prefix(self):
        eid = new_membership_event_id()
        self.assertTrue(eid.startswith("evt_"))

    def test_membership_event_ids_unique(self):
        ids = {new_membership_event_id() for _ in range(200)}
        self.assertEqual(len(ids), 200)

if __name__ == "__main__":
    unittest.main()
