from __future__ import annotations

from rm_trend_radar.db import get_articles, init_db
from rm_trend_radar.fetch import (
    exit_code_for_results,
    fetch_sources,
    unknown_source_names,
)


RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Fetched Article</title>
      <link>https://example.com/fetched?utm_source=test</link>
      <pubDate>Fri, 01 May 2026 09:12:34 +0000</pubDate>
      <category>Revenue Management</category>
      <description>This description is not stored.</description>
    </item>
  </channel>
</rss>
"""


class FakeHeaders:
    def get_content_charset(self):
        return "utf-8"


class FakeResponse:
    headers = FakeHeaders()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return RSS_XML.encode("utf-8")


def fake_opener(url, timeout):
    assert url
    assert timeout == 20
    return FakeResponse()


def test_fetch_sources_dry_run_does_not_write_to_database(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_db()

    results = fetch_sources(
        source_names=["IDeaS"],
        dry_run=True,
        opener=fake_opener,
    )

    assert [result.to_dict() for result in results] == [
        {
            "source": "IDeaS",
            "fetched": 1,
            "added": 0,
            "updated": 0,
            "unchanged": 0,
            "failed": 0,
            "error": None,
        }
    ]
    assert get_articles() == []


def test_fetch_sources_writes_parsed_items_to_database(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_db()

    results = fetch_sources(source_names=["IDeaS"], opener=fake_opener)

    articles = get_articles()
    assert results[0].added == 1
    assert articles[0]["source_name"] == "IDeaS"
    assert articles[0]["url"] == "https://example.com/fetched"


def test_unknown_source_names_are_case_insensitive():
    assert unknown_source_names(["ideas", "unknown"]) == ["unknown"]


def test_exit_code_for_results_reports_success_and_partial_failure():
    success = fetch_sources(source_names=["IDeaS"], dry_run=True, opener=fake_opener)
    assert exit_code_for_results(success) == 0

    failed = success[0].__class__(
        source="Broken",
        fetched=0,
        added=0,
        updated=0,
        unchanged=0,
        failed=1,
        error="failed",
    )
    assert exit_code_for_results([success[0], failed]) == 3
    assert exit_code_for_results([failed]) == 2
