from __future__ import annotations

from rm_trend_radar.digest import generate_weekly_digest_markdown


def test_generate_weekly_digest_markdown_uses_confirmed_article_fields():
    markdown = generate_weekly_digest_markdown(
        [
            {
                "title_ja": "確認済み記事",
                "source_name": "IDeaS",
                "published_date": "2026-05-01",
                "importance": 4,
                "url": "https://example.com/article",
                "summary_ja": "確認済み要約",
                "rm_implication": "確認済み示唆",
            }
        ],
        start_date="2026-04-26",
        end_date="2026-05-02",
        min_importance=4,
    )

    assert "# RM Trend Radar 週次ダイジェスト" in markdown
    assert "- 生成方法: 保存済みの確認済み記事データから機械的に整形。AI による新規文章生成は行わない。" in markdown
    assert "## 確認済み記事" in markdown
    assert "- 原文 URL: https://example.com/article" in markdown
    assert "確認済み要約" in markdown
    assert "確認済み示唆" in markdown


def test_generate_weekly_digest_markdown_reports_empty_result():
    markdown = generate_weekly_digest_markdown(
        [],
        start_date="2026-04-26",
        end_date="2026-05-02",
    )

    assert "該当記事はありません。" in markdown
