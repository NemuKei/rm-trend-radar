from __future__ import annotations

from rm_trend_radar.db import get_articles, init_db, upsert_rss_items
from rm_trend_radar.rss import ParsedRssItem


def test_init_db_seeds_articles(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    init_db(seed=True)

    articles = get_articles()
    assert len(articles) == 2
    assert articles[0]["published_date"] == "2026-05-01"
    assert max(article["importance"] for article in articles) == 5
    assert any("forecast" in article["tags"] for article in articles)


def test_upsert_rss_items_adds_fetched_article_with_placeholders(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_db()

    result = upsert_rss_items(
        [
            ParsedRssItem(
                source_name="IDeaS",
                url="https://example.com/new-article",
                published_date="2026-05-01",
                title_en="New Revenue Article",
                tags=("revenue-management", "unreviewed"),
            )
        ]
    )

    articles = get_articles()
    assert result == {"added": 1, "updated": 0, "unchanged": 0}
    assert len(articles) == 1
    assert articles[0]["title_ja"] == "New Revenue Article"
    assert articles[0]["summary_ja"] == "未要約。原文リンクを確認してください。"
    assert articles[0]["importance"] == 3
    assert articles[0]["rm_implication"] == "未記入。原文確認後に追記してください。"
    assert articles[0]["note"] == "RSS取得直後。要約、重要度、示唆は未確認。"
    assert articles[0]["tags"] == ["revenue-management", "unreviewed"]


def test_upsert_rss_items_does_not_overwrite_manual_fields(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_db()
    item = ParsedRssItem(
        source_name="IDeaS",
        url="https://example.com/manual-article",
        published_date="2026-05-01",
        title_en="Original English Title",
        tags=("pricing", "unreviewed"),
    )
    upsert_rss_items([item])

    import sqlite3

    with sqlite3.connect("rm_trend_radar.db") as conn:
        conn.execute(
            """
            UPDATE articles
            SET title_ja = ?,
                summary_ja = ?,
                tags_json = ?,
                importance = ?,
                rm_implication = ?,
                note = ?
            WHERE url = ?
            """,
            (
                "手動タイトル",
                "手動要約",
                '["manual"]',
                5,
                "手動示唆",
                "手動メモ",
                item.url,
            ),
        )

    result = upsert_rss_items(
        [
            ParsedRssItem(
                source_name="SiteMinder",
                url=item.url,
                published_date="2026-05-02",
                title_en="Updated English Title",
                tags=("updated", "unreviewed"),
            )
        ]
    )

    articles = get_articles()
    assert result == {"added": 0, "updated": 1, "unchanged": 0}
    assert len(articles) == 1
    assert articles[0]["source_name"] == "SiteMinder"
    assert articles[0]["published_date"] == "2026-05-02"
    assert articles[0]["title_en"] == "Updated English Title"
    assert articles[0]["title_ja"] == "手動タイトル"
    assert articles[0]["summary_ja"] == "手動要約"
    assert articles[0]["tags"] == ["manual"]
    assert articles[0]["importance"] == 5
    assert articles[0]["rm_implication"] == "手動示唆"
    assert articles[0]["note"] == "手動メモ"
