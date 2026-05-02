from __future__ import annotations

import re
from dataclasses import dataclass

TITLE_PRIORITY_HIGH = "high"
TITLE_PRIORITY_MEDIUM = "medium"
TITLE_PRIORITY_LOW = "low"
VALID_TITLE_PRIORITIES = {
    TITLE_PRIORITY_HIGH,
    TITLE_PRIORITY_MEDIUM,
    TITLE_PRIORITY_LOW,
}

HIGH_PRIORITY_TERMS = (
    "revenue management",
    "revenue manager",
    "revenue",
    "dynamic pricing",
    "pricing",
    "rate strategy",
    "rate",
    "rates",
    "adr",
    "revpar",
    "forecast",
    "forecasting",
    "demand",
    "booking pace",
    "pace",
    "distribution",
    "channel manager",
    "direct booking",
    "inventory",
    "profit",
)
MEDIUM_PRIORITY_TERMS = (
    "hotel technology",
    "automation",
    "operations",
    "guest experience",
    "marketing",
    "upsell",
    "ancillary",
    "strategy",
    "guide",
)
LOW_PRIORITY_TERMS = (
    "award",
    "awards",
    "webinar",
    "podcast",
    "conference",
    "event",
    "partnership",
    "press release",
    "announcement",
    "brand",
    "opening",
)


@dataclass(frozen=True)
class TitlePriorityResult:
    priority: str
    reason: str


def classify_title_priority(title: str) -> TitlePriorityResult:
    normalized_title = _normalize_title(title)
    if not normalized_title:
        return TitlePriorityResult(
            priority=TITLE_PRIORITY_MEDIUM,
            reason="title is empty, defaulted to medium",
        )

    matched_high = _first_matching_term(normalized_title, HIGH_PRIORITY_TERMS)
    if matched_high is not None:
        return TitlePriorityResult(
            priority=TITLE_PRIORITY_HIGH,
            reason=f"title includes revenue-management term: {matched_high}",
        )

    matched_medium = _first_matching_term(normalized_title, MEDIUM_PRIORITY_TERMS)
    if matched_medium is not None:
        return TitlePriorityResult(
            priority=TITLE_PRIORITY_MEDIUM,
            reason=f"title includes hospitality operations term: {matched_medium}",
        )

    matched_low = _first_matching_term(normalized_title, LOW_PRIORITY_TERMS)
    if matched_low is not None:
        return TitlePriorityResult(
            priority=TITLE_PRIORITY_LOW,
            reason=f"title includes announcement or event term: {matched_low}",
        )

    return TitlePriorityResult(
        priority=TITLE_PRIORITY_MEDIUM,
        reason="no title rule matched, defaulted to medium",
    )


def _first_matching_term(title: str, terms: tuple[str, ...]) -> str | None:
    for term in terms:
        pattern = rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])"
        if re.search(pattern, title):
            return term
    return None


def _normalize_title(title: str) -> str:
    title = title.lower().replace("-", " ").replace("_", " ").replace("/", " ")
    return " ".join(title.split())
