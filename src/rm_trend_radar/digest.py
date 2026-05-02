from __future__ import annotations

from typing import Any


def generate_weekly_digest_markdown(
    articles: list[dict[str, Any]],
    *,
    start_date: str,
    end_date: str,
    min_importance: int = 4,
) -> str:
    lines = [
        "# RM Trend Radar 週次ダイジェスト",
        "",
        f"- 対象期間: {start_date} から {end_date}",
        f"- 対象条件: 確認済み、重要度 {min_importance} 以上",
        "- 生成方法: 保存済みの確認済み記事データから機械的に整形。AI による新規文章生成は行わない。",
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
                f"- 原文 URL: {article['url']}",
                "",
                "### 要約",
                "",
                article["summary_ja"],
                "",
                "### レベニューマネジメント担当者向けの示唆",
                "",
                article["rm_implication"],
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"
