from __future__ import annotations

from rm_trend_radar.db import get_articles, init_db


def test_init_db_seeds_articles(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    init_db(seed=True)

    articles = get_articles()
    assert len(articles) == 2
    assert articles[0]["published_date"] == "2026-05-01"
    assert max(article["importance"] for article in articles) == 5
    assert any("forecast" in article["tags"] for article in articles)