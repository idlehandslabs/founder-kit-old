import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import metrics


class StatsTable(unittest.TestCase):
    def test_totals_and_missing_keys(self):
        st = {"days": [{"day": "2026-10-21", "visits": 3}, {"day": "2026-10-22", "visits": 4, "signups": 1}]}
        rows = metrics.stats_table(st, ["visits", "signups"])
        self.assertEqual(rows[-1], "| **total** | **7** | **1** |")
        self.assertIn("| 2026-10-21 | 3 | 0 |", rows)

    def test_empty(self):
        self.assertEqual(metrics.stats_table({}, ["a"])[-1], "| **total** | **0** |")


if __name__ == "__main__":
    unittest.main()
