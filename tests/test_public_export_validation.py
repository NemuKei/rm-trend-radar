import unittest
from datetime import datetime, timezone

from rm_trend_radar.public_export_validation import validate_public_export


def article(**kw):
    row = {"public_category": "pricing_optimization", "public_category_label": "料金設定・価格最適化",
           "title_ja": "直前料金を下げずに競争力を保つ", "summary_ja": "短い紹介文。",
           "source_name": "IDeaS", "published_date": "2026-09-01", "url": "https://ideas.com/a"}
    row.update(kw)
    return row


def payload(*articles, run_at="2026-09-24T06:10:00Z"):
    return {"schema_version": 1, "run_at_utc": run_at, "automation_id": "rm-trend-radar-lp-reflection",
            "source_repo": "rm-trend-radar", "articles": list(articles)}


class PublicExportValidationTest(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate_public_export(payload(article())), [])

    def test_extra_field_rejected(self):
        self.assertTrue(validate_public_export(payload(article(personal_summary="x"))))

    def test_missing_or_empty_field_rejected(self):
        a = article(); del a["source_name"]
        self.assertTrue(validate_public_export(payload(a)))
        self.assertTrue(validate_public_export(payload(article(title_ja=" "))))

    def test_length_limits(self):
        self.assertTrue(validate_public_export(payload(article(title_ja="あ" * 81))))
        self.assertTrue(validate_public_export(payload(article(summary_ja="あ" * 161))))
        self.assertEqual(validate_public_export(payload(article(title_ja="あ" * 80, summary_ja="あ" * 160))), [])

    def test_category_label_date_url(self):
        self.assertTrue(validate_public_export(payload(article(public_category="unknown"))))
        self.assertTrue(validate_public_export(payload(article(public_category_label="別ラベル"))))
        self.assertTrue(validate_public_export(payload(article(published_date="2026/09/01"))))
        self.assertTrue(validate_public_export(payload(article(url="http://ideas.com/a"))))

    def test_duplicate_url(self):
        self.assertTrue(validate_public_export(payload(article(), article(title_ja="別"))))

    def test_freshness(self):
        now = datetime(2026, 10, 2, tzinfo=timezone.utc)
        self.assertTrue(validate_public_export(payload(article()), now=now, max_age_days=7))
        self.assertEqual(validate_public_export(payload(article()), now=now, max_age_days=8), [])

    def test_header(self):
        self.assertTrue(validate_public_export({"schema_version": 2, "articles": []}))


if __name__ == "__main__":
    unittest.main()
