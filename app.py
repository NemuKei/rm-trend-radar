from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from rm_trend_radar.db import (
    REVIEW_STATUS_CONFIRMED,
    REVIEW_STATUS_UNREVIEWED,
    get_articles,
    get_digest_articles,
    init_db,
    update_article_review,
)
from rm_trend_radar.digest import generate_weekly_digest_markdown


REVIEW_STATUS_LABELS = {
    REVIEW_STATUS_UNREVIEWED: "未確認",
    REVIEW_STATUS_CONFIRMED: "確認済み",
}
REVIEW_STATUS_BY_LABEL = {label: value for value, label in REVIEW_STATUS_LABELS.items()}


st.set_page_config(page_title="RM Trend Radar", page_icon="📡", layout="wide")

init_db(seed=False)

st.title("RM Trend Radar")
st.caption("海外レベニューマネジメント記事を日本語で確認する個人用ダッシュボード")

tab_articles, tab_digest = st.tabs(["記事確認", "週次ダイジェスト"])


def split_tags(value: str) -> list[str]:
    return [tag.strip() for tag in value.replace("\n", ",").split(",") if tag.strip()]


def filter_articles(
    articles: list[dict],
    *,
    review_status: str | None,
    selected_sources: list[str],
    selected_tag: str,
    public_candidate_filter: str,
    min_importance: int,
    keyword: str,
) -> list[dict]:
    keyword = keyword.strip().lower()
    visible_articles = []
    for article in articles:
        if review_status is not None and article["review_status"] != review_status:
            continue
        if selected_sources and article["source_name"] not in selected_sources:
            continue
        if selected_tag != "すべて" and selected_tag not in article["tags"]:
            continue
        if public_candidate_filter == "候補のみ" and not article["public_candidate"]:
            continue
        if public_candidate_filter == "候補外" and article["public_candidate"]:
            continue
        if article["importance"] < min_importance:
            continue
        if keyword and keyword not in _search_text(article):
            continue
        visible_articles.append(article)
    return visible_articles


def _search_text(article: dict) -> str:
    values = [
        article["title_ja"],
        article["title_en"],
        article["summary_ja"],
        article["rm_implication"],
        article["source_name"],
        " ".join(article["tags"]),
    ]
    return " ".join(values).lower()


def table_rows(articles: list[dict]) -> list[dict]:
    rows = []
    for article in articles:
        rows.append(
            {
                "id": article["id"],
                "公開日": article["published_date"],
                "取得元": article["source_name"],
                "確認": REVIEW_STATUS_LABELS[article["review_status"]],
                "重要度": article["importance"],
                "公開候補": "候補" if article["public_candidate"] else "",
                "タイトル": article["title_ja"],
                "タグ": ", ".join(article["tags"][:4]),
            }
        )
    return rows


def render_article_detail(article: dict) -> None:
    status_label = REVIEW_STATUS_LABELS[article["review_status"]]
    st.divider()
    st.subheader(article["title_ja"])

    meta_cols = st.columns([0.18, 0.18, 0.16, 0.16, 0.16, 0.16])
    meta_cols[0].metric("重要度", article["importance"])
    meta_cols[1].write(f"確認状態: {status_label}")
    meta_cols[2].write(f"公開候補: {'候補' if article['public_candidate'] else '未指定'}")
    meta_cols[3].write(f"取得元: {article['source_name']}")
    meta_cols[4].write(f"公開日: {article['published_date']}")
    meta_cols[5].markdown(f"[原文を開く]({article['url']})")

    st.write("タグ: " + ", ".join(article["tags"]))
    st.write("英語タイトル: " + article["title_en"])
    st.write(article["summary_ja"])
    st.write("RM担当者向けの示唆")
    st.write(article["rm_implication"])

    with st.expander("確認内容を編集", expanded=False):
        with st.form(key=f"review_form_{article['id']}"):
            title_ja = st.text_input("日本語タイトル", value=article["title_ja"])
            summary_ja = st.text_area("日本語要約", value=article["summary_ja"])
            tag_text = st.text_input("タグ", value=", ".join(article["tags"]))
            importance = st.slider(
                "重要度",
                min_value=1,
                max_value=5,
                value=article["importance"],
            )
            rm_implication = st.text_area(
                "RM担当者向けの示唆",
                value=article["rm_implication"],
            )
            note = st.text_area("手動メモ", value=article["note"])
            review_status_label = st.selectbox(
                "確認状態",
                list(REVIEW_STATUS_BY_LABEL),
                index=list(REVIEW_STATUS_BY_LABEL).index(status_label),
            )
            public_candidate = st.checkbox(
                "複業リポ側 LP の公開候補にする",
                value=article["public_candidate"],
            )
            submitted = st.form_submit_button("保存")

        if submitted:
            update_article_review(
                article_id=article["id"],
                title_ja=title_ja,
                summary_ja=summary_ja,
                tags=split_tags(tag_text),
                importance=importance,
                rm_implication=rm_implication,
                note=note,
                review_status=REVIEW_STATUS_BY_LABEL[review_status_label],
                public_candidate=public_candidate,
            )
            st.success("保存しました。")
            st.rerun()


with tab_articles:
    articles = get_articles()

    if not articles:
        st.info("記事データがまだありません。")
    else:
        all_sources = sorted({article["source_name"] for article in articles})
        all_tags = sorted({tag for article in articles for tag in article["tags"]})

        status_filter_label = st.sidebar.radio(
            "確認状態",
            ["すべて", "未確認", "確認済み"],
        )
        review_status_filter = None
        if status_filter_label != "すべて":
            review_status_filter = REVIEW_STATUS_BY_LABEL[status_filter_label]
        selected_sources = st.sidebar.multiselect(
            "取得元",
            all_sources,
            default=all_sources,
        )
        public_candidate_filter = st.sidebar.radio(
            "公開候補",
            ["すべて", "候補のみ", "候補外"],
        )
        min_importance = st.sidebar.slider("最低重要度", 1, 5, 1)
        selected_tag = st.sidebar.selectbox("タグ", ["すべて", *all_tags])
        keyword = st.sidebar.text_input("検索")

        visible_articles = filter_articles(
            articles,
            review_status=review_status_filter,
            selected_sources=selected_sources,
            selected_tag=selected_tag,
            public_candidate_filter=public_candidate_filter,
            min_importance=min_importance,
            keyword=keyword,
        )

        summary_cols = st.columns(4)
        summary_cols[0].metric("表示件数", len(visible_articles))
        summary_cols[1].metric(
            "未確認",
            sum(1 for article in visible_articles if article["review_status"] == REVIEW_STATUS_UNREVIEWED),
        )
        summary_cols[2].metric(
            "確認済み",
            sum(1 for article in visible_articles if article["review_status"] == REVIEW_STATUS_CONFIRMED),
        )
        summary_cols[3].metric(
            "公開候補",
            sum(1 for article in visible_articles if article["public_candidate"]),
        )

        if not visible_articles:
            st.info("条件に一致する記事データがありません。")
        else:
            event = st.dataframe(
                table_rows(visible_articles),
                hide_index=True,
                use_container_width=True,
                height=430,
                on_select="rerun",
                selection_mode="single-row",
                column_config={
                    "id": None,
                    "公開日": st.column_config.TextColumn(width="small"),
                    "取得元": st.column_config.TextColumn(width="small"),
                    "確認": st.column_config.TextColumn(width="small"),
                    "重要度": st.column_config.NumberColumn(width="small"),
                    "公開候補": st.column_config.TextColumn(width="small"),
                    "タイトル": st.column_config.TextColumn(width="large"),
                    "タグ": st.column_config.TextColumn(width="medium"),
                },
            )
            selected_rows = event.selection.rows
            selected_index = selected_rows[0] if selected_rows else 0
            render_article_detail(visible_articles[selected_index])

with tab_digest:
    today = date.today()
    default_start = today - timedelta(days=6)
    digest_dates = st.date_input(
        "対象期間",
        value=(default_start, today),
    )
    min_importance = st.slider(
        "週次ダイジェストに含める最低重要度",
        min_value=1,
        max_value=5,
        value=4,
    )

    if isinstance(digest_dates, tuple) and len(digest_dates) == 2:
        start_date, end_date = digest_dates
    else:
        start_date, end_date = default_start, today

    digest_articles = get_digest_articles(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        min_importance=min_importance,
    )
    digest_markdown = generate_weekly_digest_markdown(
        digest_articles,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        min_importance=min_importance,
    )

    st.write(f"対象記事数: {len(digest_articles)}")
    st.markdown(digest_markdown)
    st.text_area("Markdown", value=digest_markdown, height=360)
