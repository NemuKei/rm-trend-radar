from __future__ import annotations

from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from html import unescape
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import xml.etree.ElementTree as ET

from .sources import SourceConfig

TRACKING_QUERY_PREFIXES = ("utm_",)
TRACKING_QUERY_NAMES = {"fbclid", "gclid", "mc_cid", "mc_eid"}


@dataclass(frozen=True)
class ParsedRssItem:
    source_name: str
    url: str
    published_date: str
    title_en: str
    tags: tuple[str, ...]


def parse_rss_items(xml_text: str, source: SourceConfig) -> list[ParsedRssItem]:
    root = ET.fromstring(xml_text)
    parsed_items: list[ParsedRssItem] = []

    for item in root.findall(".//item"):
        parsed_item = _parse_item(item, source)
        if parsed_item is not None:
            parsed_items.append(parsed_item)

    return parsed_items


def normalize_article_url(url: str) -> str:
    parts = urlsplit(url.strip())
    query = [
        (name, value)
        for name, value in parse_qsl(parts.query, keep_blank_values=True)
        if not _is_tracking_query(name)
    ]
    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            urlencode(query, doseq=True),
            "",
        )
    )


def normalize_tag(value: str) -> str | None:
    tag = unescape(value).strip().lower()
    tag = re.sub(r"[^a-z0-9]+", "-", tag).strip("-")
    return tag or None


def _parse_item(item: ET.Element, source: SourceConfig) -> ParsedRssItem | None:
    link = _required_text(item, "link")
    title = _required_text(item, "title")
    pub_date = _required_text(item, "pubDate")
    if link is None or title is None or pub_date is None:
        return None

    try:
        published_date = parsedate_to_datetime(pub_date).date().isoformat()
    except (TypeError, ValueError, IndexError, OverflowError):
        return None

    tags = _extract_tags(item)
    return ParsedRssItem(
        source_name=source.source_name,
        url=normalize_article_url(link),
        published_date=published_date,
        title_en=unescape(title).strip(),
        tags=tags,
    )


def _required_text(item: ET.Element, name: str) -> str | None:
    value = item.findtext(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def _extract_tags(item: ET.Element) -> tuple[str, ...]:
    tags = []
    for category in item.findall("category"):
        if category.text is None:
            continue
        tag = normalize_tag(category.text)
        if tag is not None and tag not in tags:
            tags.append(tag)

    if "unreviewed" not in tags:
        tags.append("unreviewed")
    return tuple(tags)


def _is_tracking_query(name: str) -> bool:
    normalized_name = name.lower()
    return normalized_name in TRACKING_QUERY_NAMES or normalized_name.startswith(
        TRACKING_QUERY_PREFIXES
    )
