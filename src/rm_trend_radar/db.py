from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .rss import ParsedRssItem

DB_PATH = Path("rm_trend_radar.db")

FETCHED_SUMMARY_PLACEHOLDER = "未要約。原文リンクを確認してください。"
FETCHED_RM_IMPLICATION_PLACEHOLDER = "未記入。原文確認後に追記してください。"
FETCHED_NOTE_PLACEHOLDER = "RSS取得直後。要約、重要度、示唆は未確認。"
FETCHED_DEFAULT_IMPORTANCE = 3

SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    published_date TEXT NOT NULL,
    title_en TEXT NOT NULL,
    title_ja TEXT NOT NULL,
    summary_ja TEXT NOT NULL,
    tags_json TEXT NOT NULL,
    importance INTEGER NOT NULL CHECK (importance BETWEEN 1 AND 5),
    rm_implication TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

SAMPLE_ARTICLES = [
    {
        "source_name": "Sample Source",
        "url": "https://example.com/revenue-management-trend",
        "published_date": "2026-05-01",
        "title_en": "Revenue teams refine pricing workflows",
        "title_ja": "レベニューチームが価格調整業務を見直す動き",
        "summary_ja": "価格調整の判断を、需要変化、競合価格、予約ペースを組み合わせて行う事例が増えているという想定サンプルです。",
        "tags": ["pricing", "workflow"],
        "importance": 4,
        "rm_implication": "価格変更の理由を記録し、後から判断品質を振り返れる運用を作ることが重要です。",
        "note": "初期表示確認用のサンプルです。",
    },
    {
        "source_name": "Sample Source",
        "url": "https://example.com/hotel-forecasting-ai",
        "published_date": "2026-04-28",
        "title_en": "Hotels evaluate AI-assisted forecasting",
        "title_ja": "ホテルがAI支援の需要予測を検証する動き",
        "summary_ja": "需要予測の自動化だけでなく、担当者が予測根拠を確認できる説明性が重視されているという想定サンプルです。",
        "tags": ["forecast", "ai"],
        "importance": 5,
        "rm_implication": "予測値だけでなく、需要増減の要因、対象日、比較基準を画面で確認できることが導入判断に影響します。",
        "note": "初期表示確認用のサンプルです。",
    },
]


class UpsertResult(dict[str, int]):
    added: int
    updated: int
    unchanged: int


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(seed: bool = False) -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
        if seed:
            for article in SAMPLE_ARTICLES:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO articles (
                        source_name, url, published_date, title_en, title_ja,
                        summary_ja, tags_json, importance, rm_implication, note
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        article["source_name"],
                        article["url"],
                        article["published_date"],
                        article["title_en"],
                        article["title_ja"],
                        article["summary_ja"],
                        json.dumps(article["tags"], ensure_ascii=False),
                        article["importance"],
                        article["rm_implication"],
                        article["note"],
                    ),
                )


def upsert_rss_items(items: list[ParsedRssItem]) -> UpsertResult:
    result = UpsertResult(added=0, updated=0, unchanged=0)
    with connect() as conn:
        for item in items:
            existing = conn.execute(
                """
                SELECT source_name, published_date, title_en
                FROM articles
                WHERE url = ?
                """,
                (item.url,),
            ).fetchone()
            if existing is None:
                conn.execute(
                    """
                    INSERT INTO articles (
                        source_name, url, published_date, title_en, title_ja,
                        summary_ja, tags_json, importance, rm_implication, note
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item.source_name,
                        item.url,
                        item.published_date,
                        item.title_en,
                        item.title_en,
                        FETCHED_SUMMARY_PLACEHOLDER,
                        json.dumps(list(item.tags), ensure_ascii=False),
                        FETCHED_DEFAULT_IMPORTANCE,
                        FETCHED_RM_IMPLICATION_PLACEHOLDER,
                        FETCHED_NOTE_PLACEHOLDER,
                    ),
                )
                result["added"] += 1
                continue

            if (
                existing["source_name"],
                existing["published_date"],
                existing["title_en"],
            ) == (item.source_name, item.published_date, item.title_en):
                result["unchanged"] += 1
                continue

            conn.execute(
                """
                UPDATE articles
                SET source_name = ?,
                    published_date = ?,
                    title_en = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE url = ?
                """,
                (item.source_name, item.published_date, item.title_en, item.url),
            )
            result["updated"] += 1
    return result


def get_articles() -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT source_name, url, published_date, title_en, title_ja,
                   summary_ja, tags_json, importance, rm_implication, note
            FROM articles
            ORDER BY published_date DESC, id DESC
            """
        ).fetchall()
    return [
        {
            **dict(row),
            "tags": json.loads(row["tags_json"]),
        }
        for row in rows
    ]
