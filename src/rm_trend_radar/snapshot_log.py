"""Bounded, metadata-only Actions logs; never a publication approval."""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta
import hashlib
import json
from pathlib import Path
import re
from typing import TextIO
import unicodedata
from urllib.parse import urlsplit

from .snapshot import SNAPSHOT_CONTRACT
from .sources import get_initial_feed_sources

LOG_PREFIX = "RM_SELECTION_V1 "
MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_LOG_BYTES = 128 * 1024
MAX_ARTICLES = 200
MAX_TITLE_CHARS = 240
MAX_URL_CHARS = 512
_HOSTS = {s.source_name: urlsplit(s.listing_url).netloc for s in get_initial_feed_sources()}
_EMAIL = re.compile(r"[\w.+%-]+@[\w.-]+\.[A-Za-z]{2,}")
_PHONE = re.compile(r"\+?\d[\d ().-]{6,}\d")
_SENSITIVE = re.compile(
    r"(?i)(?:\b(?:api[_ -]?key|access[_ -]?token|refresh[_ -]?token|password|passwd|"
    r"secret|credential|session[_ -]?id|authorization|bearer)\b\s*[:=/ ]|"
    r"\b(?:token|key|auth|cookie|session)\b\s*[:=]|"
    r"github_pat_|gh[pousr]_|AKIA[0-9A-Z]{16}|sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{16,}|"
    r"[A-Za-z0-9_=]{32,})"
)
_PRIVATE_PATH = re.compile(
    r"(?i)(?:^|/)(?:api|auth|token|key|secret|session|user|users|profile|email|login|account)"
    r"(?:/|[-_=])"
)
_PUBLIC_PATH = re.compile(r"/(?:[a-z]{1,30}|[0-9]{1,4})(?:[-/](?:[a-z]{1,30}|[0-9]{1,4}))*/?")


def _json_line(record: dict) -> str:
    # The runner recognizes commands inside a line too. Neutralize both command
    # syntaxes, and JSON-escape all controls/unicode without changing decoded data.
    return json.dumps(record, ensure_ascii=True, separators=(",", ":")).replace(
        "::", r"\u003a\u003a"
    ).replace("##[", r"\u0023\u0023[")


def _sensitive(value: str) -> bool:
    return bool(_EMAIL.search(value) or _PHONE.search(value) or _SENSITIVE.search(value))


def _article_record(article: dict) -> tuple[dict | None, str | None]:
    source = article.get("source_name")
    title = article.get("title_en")
    url = article.get("url")
    published = article.get("published_date")
    if not isinstance(title, str) or not 1 <= len(title) <= MAX_TITLE_CHARS or not title.strip():
        return None, "invalid_title"
    if (any(unicodedata.category(c).startswith("C") for c in title)
            or "<" in title or ">" in title or re.search(r"https?://|www\.", title, re.I)
            or _sensitive(title)):
        return None, "unsafe_title"
    if (not isinstance(url, str) or not 1 <= len(url) <= MAX_URL_CHARS
            or not url.isascii() or any(ord(c) <= 32 or ord(c) == 127 for c in url)):
        return None, "unsafe_url"
    try:
        parts = urlsplit(url)
    except ValueError:
        return None, "unsafe_url"
    # No URL rewriting: links with queries, fragments, credentials, ports,
    # encoded/opaque paths or unexpected hosts are held rather than exposed.
    if (parts.scheme != "https" or parts.netloc != _HOSTS[source]
            or parts.query or parts.fragment or url != url.strip()
            or not _PUBLIC_PATH.fullmatch(parts.path)
            or _sensitive(parts.path) or _PRIVATE_PATH.search(parts.path)):
        return None, "unsafe_url"
    if not isinstance(published, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", published):
        return None, "invalid_date"
    try:
        date.fromisoformat(published)
    except ValueError:
        return None, "invalid_date"
    return {"kind": "article", "source_name": source, "title_en": title,
            "url": url, "published_date": published}, None


def render_snapshot_log(snapshot: dict, *, run_id: str, run_attempt: str, head_sha: str) -> str:
    """Render safe NDJSON, with counts and an end checksum to detect truncation.

    Invalid envelopes raise a fixed error without echoing input. Held articles
    contribute only to reason counts; raw errors and non-allowlisted fields
    never enter this log. The original snapshot is not modified.
    """
    if (not re.fullmatch(r"[1-9][0-9]{0,19}", run_id)
            or not re.fullmatch(r"[1-9][0-9]{0,5}", run_attempt)
            or not re.fullmatch(r"[0-9a-f]{40}", head_sha)):
        raise ValueError("invalid run identity")
    if (snapshot.get("contract") != SNAPSHOT_CONTRACT or snapshot.get("lp_ready") is not False
            or snapshot.get("publish_decision") != "manual_review_required"):
        raise ValueError("invalid snapshot contract")
    generated = snapshot.get("generated_at_utc")
    if not isinstance(generated, str) or len(generated) > 40:
        raise ValueError("invalid snapshot time")
    timestamp = datetime.fromisoformat(generated.replace("Z", "+00:00"))
    if timestamp.utcoffset() != timedelta(0):
        raise ValueError("snapshot time must be UTC")
    sources, articles = snapshot.get("sources"), snapshot.get("articles")
    if (not isinstance(sources, list) or not 1 <= len(sources) <= len(_HOSTS)
            or not isinstance(articles, list) or len(articles) > 10000):
        raise ValueError("invalid snapshot counts")
    source_records, counts = [], {}
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("invalid source")
        name, fetched, failed = source.get("source"), source.get("fetched"), source.get("failed")
        if (not isinstance(name, str) or name not in _HOSTS or name in counts
                or type(fetched) is not int or not 0 <= fetched <= 10000
                or type(failed) is not int or failed not in (0, 1)
                or (failed and fetched)):
            raise ValueError("invalid source status")
        counts[name] = fetched
        source_records.append({"kind": "source", "source": name, "fetched": fetched, "failed": failed})
    actual_counts = Counter()
    for article in articles:
        if (not isinstance(article, dict) or not isinstance(article.get("source_name"), str)
                or article["source_name"] not in counts):
            raise ValueError("invalid article source")
        actual_counts[article["source_name"]] += 1
    if any(actual_counts[name] != count for name, count in counts.items()):
        raise ValueError("source/article count mismatch")
    header = {"kind": "snapshot", "contract": "rss-selection-log-v1", "run_id": run_id,
              "run_attempt": int(run_attempt), "head_sha": head_sha,
              "generated_at_utc": timestamp.isoformat(), "source_count": len(sources),
              "article_count": len(articles), "lp_ready": False,
              "publish_decision": "manual_review_required"}
    lines = [_json_line(record) for record in [header, *source_records]]
    used_bytes = sum(len(LOG_PREFIX) + len(line) + 1 for line in lines)
    omitted: Counter[str] = Counter()
    emitted, seen = 0, set()
    for index, article in enumerate(articles):
        if index >= MAX_ARTICLES:
            omitted["article_limit"] += len(articles) - index
            break
        record, reason = _article_record(article)
        if reason:
            omitted[reason] += 1
            continue
        if record["url"] in seen:
            omitted["duplicate_url"] += 1
            continue
        line = _json_line(record)
        line_bytes = len(LOG_PREFIX) + len(line) + 1  # ASCII JSON, including prefix/newline.
        if used_bytes + line_bytes > MAX_LOG_BYTES - 2048:
            omitted["byte_limit"] += 1
            continue
        lines.append(line)
        used_bytes += line_bytes
        emitted += 1
        seen.add(record["url"])
    digest = hashlib.sha256(("\n".join(lines) + "\n").encode("ascii")).hexdigest()
    lines.append(_json_line({"kind": "end", "emitted_count": emitted,
                             "omitted_count": sum(omitted.values()), "omitted_reasons": dict(omitted),
                             "complete": not omitted, "sha256": digest}))
    return "".join(LOG_PREFIX + line + "\n" for line in lines)


def emit_snapshot_log(path: Path, *, run_id: str, run_attempt: str, head_sha: str,
                      stream: TextIO) -> int:
    """The workflow boundary: bounded read, no input-bearing exception messages."""
    try:
        with path.open("rb") as handle:
            raw = handle.read(MAX_INPUT_BYTES + 1)
        if len(raw) > MAX_INPUT_BYTES:
            raise ValueError("snapshot too large")
        text = render_snapshot_log(json.loads(raw), run_id=run_id,
                                   run_attempt=run_attempt, head_sha=head_sha)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError, RecursionError):
        stream.write(LOG_PREFIX + '{"kind":"error","reason":"invalid_snapshot_or_run"}\n')
        return 1
    stream.write(text)
    return 0
