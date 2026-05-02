from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceConfig:
    source_name: str
    feed_url: str | None
    listing_url: str
    use_in_initial_mvp: bool


INITIAL_SOURCES: tuple[SourceConfig, ...] = (
    SourceConfig(
        source_name="IDeaS",
        feed_url="https://ideas.com/feed/",
        listing_url="https://ideas.com/blog/",
        use_in_initial_mvp=True,
    ),
    SourceConfig(
        source_name="SiteMinder",
        feed_url="https://www.siteminder.com/r/feed/",
        listing_url="https://www.siteminder.com/r/",
        use_in_initial_mvp=True,
    ),
    SourceConfig(
        source_name="RoomPriceGenie",
        feed_url="https://roompricegenie.com/feed/",
        listing_url="https://roompricegenie.com/category/blog/",
        use_in_initial_mvp=True,
    ),
    SourceConfig(
        source_name="Revfine",
        feed_url="https://www.revfine.com/category/hotel-blog/revenue-management/feed/",
        listing_url="https://www.revfine.com/category/hotel-blog/revenue-management/",
        use_in_initial_mvp=True,
    ),
    SourceConfig(
        source_name="Hotel Speak",
        feed_url="https://www.hotelspeak.com/category/hotel-revenue-management/feed/",
        listing_url="https://www.hotelspeak.com/category/hotel-revenue-management/",
        use_in_initial_mvp=True,
    ),
    SourceConfig(
        source_name="Mews",
        feed_url=None,
        listing_url="https://www.mews.com/en/blog",
        use_in_initial_mvp=False,
    ),
    SourceConfig(
        source_name="Lighthouse",
        feed_url=None,
        listing_url="https://www.mylighthouse.com/resources/blog",
        use_in_initial_mvp=False,
    ),
    SourceConfig(
        source_name="Hospitality Net",
        feed_url="https://www.hospitalitynet.org/rss/news.xml",
        listing_url="https://www.hospitalitynet.org/news",
        use_in_initial_mvp=False,
    ),
)


def get_initial_feed_sources() -> tuple[SourceConfig, ...]:
    return tuple(
        source
        for source in INITIAL_SOURCES
        if source.use_in_initial_mvp and source.feed_url is not None
    )
