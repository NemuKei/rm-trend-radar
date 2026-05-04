from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
from pathlib import Path

from .fetch import UrlOpen, fetch_source_items
from .sources import SourceConfig, get_initial_feed_sources

SNAPSHOT_CONTRACT = "rss-metadata-only-v1"


@dataclass(frozen=True)
class SnapshotSourceResult:
    source: str
    fetched: int
    failed: int
    error: str | None = None


def build_snapshot(
    *,
    source_names: list[str] | None = None,
    timeout_seconds: float = 20,
    opener: UrlOpen | None = None,
) -> dict[str, object]:
    sources = _filter_sources(get_initial_feed_sources(), source_names)
    source_results: list[SnapshotSourceResult] = []
    articles: list[dict[str, object]] = []

    for source in sources:
        kwargs = {"timeout_seconds": timeout_seconds}
        if opener is not None:
            kwargs["opener"] = opener
        items, error = fetch_source_items(source, **kwargs)
        source_results.append(
            SnapshotSourceResult(
                source=source.source_name,
                fetched=len(items),
                failed=1 if error else 0,
                error=error,
            )
        )
        articles.extend(_snapshot_article(item) for item in items)

    articles.sort(
        key=lambda article: (
            str(article["published_date"]),
            str(article["source_name"]),
            str(article["title_en"]),
        ),
        reverse=True,
    )

    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "contract": SNAPSHOT_CONTRACT,
        "lp_ready": False,
        "publish_decision": "manual_review_required",
        "sources": [asdict(result) for result in source_results],
        "articles": articles,
    }


def write_snapshot(snapshot: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def snapshot_has_failures(snapshot: dict[str, object]) -> bool:
    sources = snapshot.get("sources", [])
    return any(source.get("failed") for source in sources if isinstance(source, dict))


def _filter_sources(
    sources: tuple[SourceConfig, ...], source_names: list[str] | None
) -> list[SourceConfig]:
    if not source_names:
        return list(sources)
    requested = {name.lower() for name in source_names}
    return [source for source in sources if source.source_name.lower() in requested]


def _snapshot_article(item) -> dict[str, object]:
    return {
        "source_name": item.source_name,
        "url": item.url,
        "published_date": item.published_date,
        "title_en": item.title_en,
        "tags": list(item.tags),
        "review_status": "unreviewed",
        "public_candidate": False,
    }
