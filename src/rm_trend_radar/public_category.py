from __future__ import annotations

PUBLIC_CATEGORY_EMPTY = ""

PUBLIC_CATEGORY_OPTIONS = [
    ("pricing_optimization", "料金設定・価格最適化"),
    ("forecast_occupancy_controls", "需要予測・稼働・宿泊制限"),
    ("revenue_metrics_owner_view", "収益指標・オーナー視点"),
    ("ai_search_booking_behavior", "AI・検索・予約行動"),
    ("distribution_ota_direct", "Distribution・OTA・直販"),
    ("organization_process", "組織・業務プロセス"),
]

PUBLIC_CATEGORY_LABELS = dict(PUBLIC_CATEGORY_OPTIONS)
PUBLIC_CATEGORY_ORDER = {
    slug: index
    for index, (slug, _label) in enumerate(PUBLIC_CATEGORY_OPTIONS)
}


def validate_public_category(value: str) -> str:
    normalized = value.strip()
    if normalized == PUBLIC_CATEGORY_EMPTY:
        return normalized
    if normalized not in PUBLIC_CATEGORY_LABELS:
        raise ValueError(f"Unknown public_category: {value}")
    return normalized


def public_category_label(value: str) -> str:
    return PUBLIC_CATEGORY_LABELS.get(value, "")
