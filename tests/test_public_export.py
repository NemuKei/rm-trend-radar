from __future__ import annotations

import json

from rm_trend_radar.public_export import (
    build_public_candidate_records,
    generate_public_candidate_json,
    generate_public_candidate_markdown,
)


ARTICLE = {
    "source_name": "IDeaS",
    "url": "https://example.com/public",
    "published_date": "2026-05-01",
    "title_ja": "公開候補記事",
    "title_en": "Public Candidate",
    "summary_ja": "短い紹介",
    "tags": ["pricing", "forecast"],
    "importance": 5,
    "rm_implication": "業務上の示唆",
    "note": "内部メモ",
    "review_status": "confirmed",
    "public_candidate": True,
}


def test_build_public_candidate_records_excludes_internal_note():
    records = build_public_candidate_records([ARTICLE])

    assert records == [
        {
            "source_name": "IDeaS",
            "url": "https://example.com/public",
            "published_date": "2026-05-01",
            "title_ja": "公開候補記事",
            "title_en": "Public Candidate",
            "summary_ja": "短い紹介",
            "tags": ["pricing", "forecast"],
            "importance": 5,
            "rm_implication": "業務上の示唆",
        }
    ]


def test_generate_public_candidate_json_is_machine_readable():
    data = json.loads(generate_public_candidate_json([ARTICLE]))

    assert data[0]["title_ja"] == "公開候補記事"
    assert "note" not in data[0]


def test_generate_public_candidate_markdown_uses_public_fields_only():
    markdown = generate_public_candidate_markdown([ARTICLE])

    assert "# 公開候補記事" in markdown
    assert "## 公開候補記事" in markdown
    assert "短い紹介" in markdown
    assert "業務上の示唆" in markdown
    assert "内部メモ" not in markdown


def test_generate_public_candidate_markdown_reports_empty_result():
    markdown = generate_public_candidate_markdown([])

    assert "該当記事はありません。" in markdown
