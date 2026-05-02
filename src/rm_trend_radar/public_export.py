from __future__ import annotations

import json
from typing import Any


def build_public_candidate_records(articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for article in articles:
        records.append(
            {
                "source_name": article["source_name"],
                "url": article["url"],
                "published_date": article["published_date"],
                "title_ja": article["title_ja"],
                "title_en": article["title_en"],
                "summary_ja": article["summary_ja"],
                "tags": article["tags"],
                "importance": article["importance"],
                "rm_implication": article["rm_implication"],
            }
        )
    return records


def generate_public_candidate_json(articles: list[dict[str, Any]]) -> str:
    return json.dumps(
        build_public_candidate_records(articles),
        ensure_ascii=False,
        indent=2,
    )


def generate_public_candidate_markdown(articles: list[dict[str, Any]]) -> str:
    lines = [
        "# 公開候補記事",
        "",
        "- 対象: 確認済み、かつ副業リポ側 LP の公開候補にした記事",
        "- 注意: 原文記事の代替になる長文転載ではなく、公開ページ作成前の候補一覧として使う。",
        "",
    ]
    if not articles:
        lines.append("該当記事はありません。")
        return "\n".join(lines)

    for article in articles:
        lines.extend(
            [
                f"## {article['title_ja']}",
                "",
                f"- 取得元: {article['source_name']}",
                f"- 公開日: {article['published_date']}",
                f"- 重要度: {article['importance']}",
                f"- タグ: {', '.join(article['tags'])}",
                f"- 原文 URL: {article['url']}",
                "",
                "### 短い紹介",
                "",
                article["summary_ja"],
                "",
                "### 業務上の示唆",
                "",
                article["rm_implication"],
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
