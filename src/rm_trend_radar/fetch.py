from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from .db import UpsertResult, upsert_rss_items
from .rss import ParsedRssItem, parse_rss_items
from .sources import SourceConfig, get_initial_feed_sources

UrlOpen = Callable[..., object]
USER_AGENT = "RMTrendRadar/0.1 (+https://github.com/NemuKei/rm-trend-radar)"


@dataclass(frozen=True)
class SourceFetchResult:
    source: str
    fetched: int
    added: int
    updated: int
    unchanged: int
    failed: int
    error: str | None = None

    def to_dict(self) -> dict[str, int | str | None]:
        return asdict(self)


def fetch_sources(
    *,
    source_names: list[str] | None = None,
    dry_run: bool = False,
    timeout_seconds: float = 20,
    opener: UrlOpen = urlopen,
) -> list[SourceFetchResult]:
    sources = _filter_sources(get_initial_feed_sources(), source_names)
    return [
        fetch_source(
            source,
            dry_run=dry_run,
            timeout_seconds=timeout_seconds,
            opener=opener,
        )
        for source in sources
    ]


def fetch_source(
    source: SourceConfig,
    *,
    dry_run: bool = False,
    timeout_seconds: float = 20,
    opener: UrlOpen = urlopen,
) -> SourceFetchResult:
    if source.feed_url is None:
        return _failed(source.source_name, "feed URL is not configured")

    try:
        xml_text = _read_url(source.feed_url, timeout_seconds, opener)
        items = parse_rss_items(xml_text, source)
        result = UpsertResult(added=0, updated=0, unchanged=0)
        if not dry_run:
            result = upsert_rss_items(items)
        return SourceFetchResult(
            source=source.source_name,
            fetched=len(items),
            added=result["added"],
            updated=result["updated"],
            unchanged=result["unchanged"],
            failed=0,
        )
    except (ET.ParseError, HTTPError, URLError, TimeoutError, OSError) as exc:
        return _failed(source.source_name, str(exc))


def fetch_source_items(
    source: SourceConfig,
    *,
    timeout_seconds: float = 20,
    opener: UrlOpen = urlopen,
) -> tuple[list[ParsedRssItem], str | None]:
    if source.feed_url is None:
        return [], "feed URL is not configured"

    try:
        xml_text = _read_url(source.feed_url, timeout_seconds, opener)
        return parse_rss_items(xml_text, source), None
    except (ET.ParseError, HTTPError, URLError, TimeoutError, OSError) as exc:
        return [], str(exc)


def unknown_source_names(source_names: list[str]) -> list[str]:
    known = {source.source_name.lower() for source in get_initial_feed_sources()}
    return [name for name in source_names if name.lower() not in known]


def has_failures(results: list[SourceFetchResult]) -> bool:
    return any(result.failed for result in results)


def exit_code_for_results(results: list[SourceFetchResult]) -> int:
    if not results:
        return 1
    failed_count = sum(result.failed for result in results)
    if failed_count == 0:
        return 0
    if failed_count == len(results):
        return 2
    return 3


def _filter_sources(
    sources: tuple[SourceConfig, ...], source_names: list[str] | None
) -> list[SourceConfig]:
    if not source_names:
        return list(sources)
    requested = {name.lower() for name in source_names}
    return [source for source in sources if source.source_name.lower() in requested]


def _read_url(url: str, timeout_seconds: float, opener: UrlOpen) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with opener(request, timeout=timeout_seconds) as response:
        raw = response.read()
        charset = "utf-8"
        headers = getattr(response, "headers", None)
        if headers is not None:
            charset = headers.get_content_charset() or charset
        return raw.decode(charset, errors="replace")


def _failed(source_name: str, error: str) -> SourceFetchResult:
    return SourceFetchResult(
        source=source_name,
        fetched=0,
        added=0,
        updated=0,
        unchanged=0,
        failed=1,
        error=error,
    )
