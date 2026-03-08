import unittest

from gymchallenge.display_names import build_display_name_map


class TestDisplayNames(unittest.TestCase):
    def test_unique_names_use_last_first(self):
        rows = [
            {
                "participant_id": "smith-john-01",
                "first_name": "John",
                "last_name": "Smith",
            },
            {
                "participant_id": "doe-jane-01",
                "first_name": "Jane",
                "last_name": "Doe",
            },
        ]

        result = build_display_name_map(rows)

        self.assertEqual(result["smith-john-01"], "Smith, John")
        self.assertEqual(result["doe-jane-01"], "Doe, Jane")

    def test_duplicate_names_get_suffix(self):
        rows = [
            {
                "participant_id": "smith-john-01",
                "first_name": "John",
                "last_name": "Smith",
            },
            {
                "participant_id": "smith-john-02",
                "first_name": "John",
                "last_name": "Smith",
            },
        ]

        result = build_display_name_map(rows)

        self.assertEqual(result["smith-john-01"], "Smith, John (01)")
        self.assertEqual(result["smith-john-02"], "Smith, John (02)")


if __name__ == "__main__":
    unittest.main()
