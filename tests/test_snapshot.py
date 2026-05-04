from __future__ import annotations

from rm_trend_radar.snapshot import (
    build_snapshot,
    snapshot_has_failures,
    snapshot_has_successes,
)


RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Snapshot Article</title>
      <link>https://example.com/snapshot?utm_source=test</link>
      <pubDate>Fri, 01 May 2026 09:12:34 +0000</pubDate>
      <category>Revenue Management</category>
      <description>This description must not be exported.</description>
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


def test_build_snapshot_exports_metadata_only():
    snapshot = build_snapshot(source_names=["IDeaS"], opener=fake_opener)

    assert snapshot["contract"] == "rss-metadata-only-v1"
    assert snapshot["lp_ready"] is False
    assert snapshot["publish_decision"] == "manual_review_required"
    assert snapshot["sources"][0]["source"] == "IDeaS"
    assert snapshot["sources"][0]["fetched"] == 1

    article = snapshot["articles"][0]
    assert article == {
        "source_name": "IDeaS",
        "url": "https://example.com/snapshot",
        "published_date": "2026-05-01",
        "title_en": "Snapshot Article",
        "tags": ["revenue-management", "unreviewed"],
        "review_status": "unreviewed",
        "public_candidate": False,
    }
    assert "description" not in article
    assert "summary_ja" not in article


def test_snapshot_failure_helpers_distinguish_partial_success():
    snapshot = {
        "sources": [
            {"source": "OK", "fetched": 1, "failed": 0, "error": None},
            {"source": "Broken", "fetched": 0, "failed": 1, "error": "failed"},
        ]
    }

    assert snapshot_has_failures(snapshot) is True
    assert snapshot_has_successes(snapshot) is True
