from __future__ import annotations

from rm_trend_radar.title_priority import classify_title_priority


def test_classify_title_priority_marks_pricing_titles_high():
    result = classify_title_priority("Hotels rethink dynamic pricing for demand shifts")

    assert result.priority == "high"
    assert "pricing" in result.reason


def test_classify_title_priority_marks_operations_titles_medium():
    result = classify_title_priority("A practical guide to hotel operations automation")

    assert result.priority == "medium"
    assert "automation" in result.reason


def test_classify_title_priority_marks_event_titles_low():
    result = classify_title_priority("Vendor announces annual hospitality webinar")

    assert result.priority == "low"
    assert "webinar" in result.reason


def test_classify_title_priority_defaults_to_medium_without_rule_match():
    result = classify_title_priority("Five trends to watch this summer")

    assert result.priority == "medium"
    assert result.reason == "no title rule matched, defaulted to medium"


def test_classify_title_priority_does_not_match_terms_inside_other_words():
    result = classify_title_priority("Brand strategy update")

    assert result.priority == "medium"
    assert result.reason == "title includes hospitality operations term: strategy"
