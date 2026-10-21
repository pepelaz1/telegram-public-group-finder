import csv
import unittest
from pathlib import Path
from types import SimpleNamespace

from finder import collect_groups, write_csv, write_report


class FinderTests(unittest.TestCase):
    def test_filters_and_merges_queries(self):
        group = SimpleNamespace(id=7, title="Ads group", username="ads_group", megagroup=True)
        channel = SimpleNamespace(id=8, title="Ads channel", username="ads_channel", megagroup=False)
        private = SimpleNamespace(id=9, title="Private", username=None, megagroup=True)
        result = collect_groups([("Google Ads", [group, channel, private]), ("CPA", [group])])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].matched_queries, ("Google Ads", "CPA"))
        self.assertEqual(result[0].url, "https://t.me/ads_group")

    def test_csv_and_report_escape_untrusted_title(self):
        group = SimpleNamespace(id=3, title="<script>alert(1)</script>", username="safe_group", megagroup=True)
        results = collect_groups([("ads", [group])])
        output = Path(__file__).resolve().parents[1] / "output" / "tests"
        csv_file, html_file = output / "groups.csv", output / "report.html"
        write_csv(results, csv_file)
        write_report(results, html_file, demo=False)
        with csv_file.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(rows[0]["title"], "<script>alert(1)</script>")
        report = html_file.read_text(encoding="utf-8")
        self.assertIn("&lt;script&gt;", report)
        self.assertNotIn("<script>alert", report)


if __name__ == "__main__":
    unittest.main()
