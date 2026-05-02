from __future__ import annotations

import sqlite3

from rm_trend_radar.db import (
    get_articles,
    get_digest_articles,
    get_public_candidate_articles,
    init_db,
    update_article_interest_flags,
    update_article_review,
    upsert_rss_items,
)
from rm_trend_radar.rss import ParsedRssItem


def test_init_db_seeds_articles(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    init_db(seed=True)

    articles = get_articles()
    assert len(articles) == 2
    assert articles[0]["published_date"] == "2026-05-01"
    assert max(article["importance"] for article in articles) == 5
    assert any("forecast" in article["tags"] for article in articles)
    assert all(article["review_status"] == "confirmed" for article in articles)
    assert all(article["reviewed_at"] is not None for article in articles)
    assert all(not article["interest_candidate"] for article in articles)
    assert all(not article["public_candidate"] for article in articles)
    assert all(article["title_priority"] == "high" for article in articles)


def test_init_db_migrates_existing_articles_table(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with sqlite3.connect("rm_trend_radar.db") as conn:
        conn.execute(
            """
            CREATE TABLE articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                published_date TEXT NOT NULL,
                title_en TEXT NOT NULL,
                title_ja TEXT NOT NULL,
                summary_ja TEXT NOT NULL,
                tags_json TEXT NOT NULL,
                importance INTEGER NOT NULL CHECK (importance BETWEEN 1 AND 5),
                rm_implication TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    init_db()

    with sqlite3.connect("rm_trend_radar.db") as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(articles)")}
    assert "review_status" in columns
    assert "reviewed_at" in columns
    assert "interest_candidate" in columns
    assert "public_candidate" in columns
    assert "title_priority" in columns
    assert "title_priority_reason" in columns


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
    assert articles[0]["review_status"] == "unreviewed"
    assert articles[0]["reviewed_at"] is None
    assert articles[0]["interest_candidate"] is False
    assert articles[0]["public_candidate"] is False
    assert articles[0]["title_priority"] == "high"
    assert "revenue" in articles[0]["title_priority_reason"]


def test_upsert_rss_items_does_not_overwrite_review_fields(tmp_path, monkeypatch):
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
    with sqlite3.connect("rm_trend_radar.db") as conn:
        conn.execute(
            """
            UPDATE articles
            SET title_ja = ?,
                summary_ja = ?,
                tags_json = ?,
                importance = ?,
                rm_implication = ?,
                note = ?,
                review_status = ?,
                reviewed_at = CURRENT_TIMESTAMP,
                interest_candidate = ?,
                public_candidate = ?
            WHERE url = ?
            """,
            (
                "手動タイトル",
                "手動要約",
                '["manual"]',
                5,
                "手動示唆",
                "手動メモ",
                "confirmed",
                1,
                1,
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
    assert articles[0]["title_priority"] == "medium"
    assert articles[0]["title_priority_reason"] == "no title rule matched, defaulted to medium"
    assert articles[0]["title_ja"] == "手動タイトル"
    assert articles[0]["summary_ja"] == "手動要約"
    assert articles[0]["tags"] == ["manual"]
    assert articles[0]["importance"] == 5
    assert articles[0]["rm_implication"] == "手動示唆"
    assert articles[0]["note"] == "手動メモ"
    assert articles[0]["review_status"] == "confirmed"
    assert articles[0]["reviewed_at"] is not None
    assert articles[0]["interest_candidate"] is True
    assert articles[0]["public_candidate"] is True


def test_update_article_review_saves_manual_review_fields(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_db()
    upsert_rss_items(
        [
            ParsedRssItem(
                source_name="IDeaS",
                url="https://example.com/review-target",
                published_date="2026-05-01",
                title_en="Review Target",
                tags=("revenue-management", "unreviewed"),
            )
        ]
    )
    article_id = get_articles()[0]["id"]

    update_article_review(
        article_id=article_id,
        title_ja="確認済みタイトル",
        summary_ja="確認済み要約",
        tags=["Revenue Management", "Pricing", "Pricing"],
        importance=4,
        rm_implication="確認済み示唆",
        note="確認済みメモ",
        review_status="confirmed",
        public_candidate=True,
        interest_candidate=True,
    )

    article = get_articles(review_status="confirmed")[0]
    assert article["id"] == article_id
    assert article["title_ja"] == "確認済みタイトル"
    assert article["summary_ja"] == "確認済み要約"
    assert article["tags"] == ["revenue-management", "pricing"]
    assert article["importance"] == 4
    assert article["rm_implication"] == "確認済み示唆"
    assert article["note"] == "確認済みメモ"
    assert article["reviewed_at"] is not None
    assert article["interest_candidate"] is True
    assert article["public_candidate"] is True


def test_update_article_interest_flags_saves_only_interest_candidate(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    init_db()
    items = [
        ParsedRssItem("IDeaS", "https://example.com/a", "2026-05-01", "A", ("tag",)),
        ParsedRssItem("IDeaS", "https://example.com/b", "2026-05-01", "B", ("tag",)),
    ]
    upsert_rss_items(items)
    articles = {article["url"]: article for article in get_articles()}

    update_article_interest_flags(
        {
            articles["https://example.com/a"]["id"]: True,
            articles["https://example.com/b"]["id"]: False,
        }
    )

    updated_articles = {article["url"]: article for article in get_articles()}
    assert updated_articles["https://example.com/a"]["interest_candidate"] is True
    assert updated_articles["https://example.com/b"]["interest_candidate"] is False
    assert updated_articles["https://example.com/a"]["review_status"] == "unreviewed"
    assert updated_articles["https://example.com/a"]["importance"] == 3


def test_get_digest_articles_includes_only_confirmed_recent_important_articles(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    init_db()
    items = [
        ParsedRssItem("IDeaS", "https://example.com/a", "2026-05-01", "A", ("tag",)),
        ParsedRssItem("IDeaS", "https://example.com/b", "2026-05-01", "B", ("tag",)),
        ParsedRssItem("IDeaS", "https://example.com/c", "2026-04-20", "C", ("tag",)),
    ]
    upsert_rss_items(items)
    articles = {article["url"]: article for article in get_articles()}
    update_article_review(
        article_id=articles["https://example.com/a"]["id"],
        title_ja="A",
        summary_ja="A summary",
        tags=["tag"],
        importance=4,
        rm_implication="A implication",
        note="",
        review_status="confirmed",
        public_candidate=True,
    )
    update_article_review(
        article_id=articles["https://example.com/b"]["id"],
        title_ja="B",
        summary_ja="B summary",
        tags=["tag"],
        importance=3,
        rm_implication="B implication",
        note="",
        review_status="confirmed",
        public_candidate=False,
    )
    update_article_review(
        article_id=articles["https://example.com/c"]["id"],
        title_ja="C",
        summary_ja="C summary",
        tags=["tag"],
        importance=5,
        rm_implication="C implication",
        note="",
        review_status="confirmed",
        public_candidate=False,
    )

    digest_articles = get_digest_articles(
        start_date="2026-04-25",
        end_date="2026-05-02",
        min_importance=4,
    )

    assert [article["url"] for article in digest_articles] == ["https://example.com/a"]


def test_get_public_candidate_articles_includes_only_confirmed_candidates(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    init_db()
    items = [
        ParsedRssItem("IDeaS", "https://example.com/a", "2026-05-01", "A", ("tag",)),
        ParsedRssItem("IDeaS", "https://example.com/b", "2026-05-01", "B", ("tag",)),
        ParsedRssItem("IDeaS", "https://example.com/c", "2026-05-01", "C", ("tag",)),
    ]
    upsert_rss_items(items)
    articles = {article["url"]: article for article in get_articles()}
    update_article_review(
        article_id=articles["https://example.com/a"]["id"],
        title_ja="A",
        summary_ja="A summary",
        tags=["tag"],
        importance=5,
        rm_implication="A implication",
        note="",
        review_status="confirmed",
        public_candidate=True,
    )
    update_article_review(
        article_id=articles["https://example.com/b"]["id"],
        title_ja="B",
        summary_ja="B summary",
        tags=["tag"],
        importance=5,
        rm_implication="B implication",
        note="",
        review_status="confirmed",
        public_candidate=False,
    )
    update_article_review(
        article_id=articles["https://example.com/c"]["id"],
        title_ja="C",
        summary_ja="C summary",
        tags=["tag"],
        importance=5,
        rm_implication="C implication",
        note="",
        review_status="unreviewed",
        public_candidate=True,
    )

    public_articles = get_public_candidate_articles()

    assert [article["url"] for article in public_articles] == ["https://example.com/a"]
