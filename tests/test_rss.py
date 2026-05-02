from __future__ import annotations

from rm_trend_radar.rss import normalize_article_url, normalize_tag, parse_rss_items
from rm_trend_radar.sources import get_initial_feed_sources


def test_initial_feed_sources_include_only_selected_mvp_sources():
    sources = get_initial_feed_sources()

    assert [source.source_name for source in sources] == [
        "IDeaS",
        "SiteMinder",
        "RoomPriceGenie",
        "Revfine",
        "Hotel Speak",
    ]
    assert all(source.feed_url for source in sources)


def test_parse_rss_items_extracts_contract_fields_only():
    source = get_initial_feed_sources()[0]
    xml_text = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
      <channel>
        <item>
          <title>Revenue &amp; Pricing Update</title>
          <link>https://example.com/article?utm_source=newsletter&amp;keep=1#section</link>
          <pubDate>Fri, 01 May 2026 09:12:34 +0000</pubDate>
          <category>Revenue Management</category>
          <category>AI</category>
          <description>This excerpt is not part of ParsedRssItem.</description>
          <content:encoded><![CDATA[<p>Full article body must not be returned.</p>]]></content:encoded>
        </item>
      </channel>
    </rss>
    """

    items = parse_rss_items(xml_text, source)

    assert len(items) == 1
    assert items[0].source_name == "IDeaS"
    assert items[0].url == "https://example.com/article?keep=1"
    assert items[0].published_date == "2026-05-01"
    assert items[0].title_en == "Revenue & Pricing Update"
    assert items[0].tags == ("revenue-management", "ai", "unreviewed")
    assert not hasattr(items[0], "description")
    assert not hasattr(items[0], "content")


def test_parse_rss_items_skips_items_without_required_fields():
    source = get_initial_feed_sources()[0]
    xml_text = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <item>
          <title>Missing link</title>
          <pubDate>Fri, 01 May 2026 09:12:34 +0000</pubDate>
        </item>
        <item>
          <title>Invalid date</title>
          <link>https://example.com/invalid-date</link>
          <pubDate>not a date</pubDate>
        </item>
      </channel>
    </rss>
    """

    assert parse_rss_items(xml_text, source) == []


def test_normalize_article_url_removes_tracking_query_and_fragment():
    assert (
        normalize_article_url(
            "https://example.com/post?utm_medium=email&gclid=abc&page=2#comments"
        )
        == "https://example.com/post?page=2"
    )


def test_normalize_tag_returns_none_for_empty_result():
    assert normalize_tag("Revenue Management") == "revenue-management"
    assert normalize_tag("!!!") is None
