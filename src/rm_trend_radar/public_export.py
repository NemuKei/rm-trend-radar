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
                "public_tip_ja": article["public_tip_ja"],
                "sns_post_draft": article["sns_post_draft"],
                "newsletter_lead_draft": article["newsletter_lead_draft"],
                "internal_share_summary": article["internal_share_summary"],
                "manager_checklist": article["manager_checklist"],
                "source_credit": article["source_credit"],
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
                "### 出典表記",
                "",
                article["source_credit"] or f"参考: {article['source_name']} {article['url']}",
                "",
                "### 日本施設向けTips",
                "",
                article["public_tip_ja"] or "未作成",
                "",
                "### SNS投稿案",
                "",
                article["sns_post_draft"] or "未作成",
                "",
                "### メルマガ用リード文",
                "",
                article["newsletter_lead_draft"] or "未作成",
                "",
                "### 社内共有用3行要約",
                "",
                article["internal_share_summary"] or "未作成",
                "",
                "### 支配人・現場向けチェックリスト",
                "",
                article["manager_checklist"] or "未作成",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
