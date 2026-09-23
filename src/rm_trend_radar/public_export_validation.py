from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlparse

from .public_category import PUBLIC_CATEGORY_LABELS

PUBLIC_FIELDS = ("public_category", "public_category_label", "title_ja", "summary_ja",
                 "source_name", "published_date", "url")
TITLE_MAX_CHARS = 80
SUMMARY_MAX_CHARS = 160
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_public_export(payload: dict[str, Any], *, now: datetime | None = None,
                           max_age_days: float | None = None) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    try:
        run_at = datetime.fromisoformat(str(payload.get("run_at_utc", "")).replace("Z", "+00:00"))
    except ValueError:
        errors.append("run_at_utc must be ISO 8601")
        run_at = None
    if run_at and now and max_age_days is not None and now - run_at > timedelta(days=max_age_days):
        errors.append(f"stale export: run_at_utc={payload['run_at_utc']}")
    articles = payload.get("articles")
    if not isinstance(articles, list):
        return errors + ["articles must be a list"]
    seen: set[str] = set()
    for i, a in enumerate(articles):
        where = f"articles[{i}]"
        if not isinstance(a, dict):
            errors.append(f"{where} must be an object"); continue
        keys = set(a)
        if keys != set(PUBLIC_FIELDS):
            errors.append(f"{where} fields must be exactly {PUBLIC_FIELDS}: extra={sorted(keys - set(PUBLIC_FIELDS))} missing={sorted(set(PUBLIC_FIELDS) - keys)}")
            continue
        if any(not isinstance(a[k], str) or not a[k].strip() for k in PUBLIC_FIELDS):
            errors.append(f"{where} has empty field"); continue
        if len(a["title_ja"]) > TITLE_MAX_CHARS:
            errors.append(f"{where} title_ja exceeds {TITLE_MAX_CHARS}")
        if len(a["summary_ja"]) > SUMMARY_MAX_CHARS:
            errors.append(f"{where} summary_ja exceeds {SUMMARY_MAX_CHARS}")
        if PUBLIC_CATEGORY_LABELS.get(a["public_category"]) != a["public_category_label"]:
            errors.append(f"{where} public_category/label mismatch")
        if not DATE_RE.match(a["published_date"]):
            errors.append(f"{where} published_date must be YYYY-MM-DD")
        url = urlparse(a["url"])
        if url.scheme != "https" or not url.hostname:
            errors.append(f"{where} url must be https")
        if a["url"] in seen:
            errors.append(f"{where} duplicate url")
        seen.add(a["url"])
    return errors
