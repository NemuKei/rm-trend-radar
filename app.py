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

init_db(seed=True)

st.title("RM Trend Radar")
st.caption("海外レベニューマネジメント記事を日本語で確認する個人用ダッシュボード")

tab_articles, tab_digest = st.tabs(["記事確認", "週次ダイジェスト"])


def split_tags(value: str) -> list[str]:
    return [tag.strip() for tag in value.replace("\n", ",").split(",") if tag.strip()]


def render_article_card(article: dict) -> None:
    status_label = REVIEW_STATUS_LABELS[article["review_status"]]
    with st.container(border=True):
        cols = st.columns([0.7, 0.3])
        with cols[0]:
            st.subheader(article["title_ja"])
            st.write(article["summary_ja"])
            st.markdown(f"[原文を開く]({article['url']})")
        with cols[1]:
            st.metric("重要度", article["importance"])
            st.write(f"確認状態: {status_label}")
            st.write(f"取得元: {article['source_name']}")
            st.write(f"公開日: {article['published_date']}")
            st.write("タグ: " + ", ".join(article["tags"]))
        st.write("RM担当者向けの示唆")
        st.write(article["rm_implication"])

        with st.expander("確認内容を編集"):
            with st.form(key=f"review_form_{article['id']}"):
                title_ja = st.text_input("日本語タイトル", value=article["title_ja"])
                summary_ja = st.text_area("日本語要約", value=article["summary_ja"])
                tag_text = st.text_input("タグ", value=", ".join(article["tags"]))
                importance = st.slider("重要度", min_value=1, max_value=5, value=article["importance"])
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
                )
                st.success("保存しました。")
                st.rerun()


with tab_articles:
    status_filter_label = st.sidebar.radio("確認状態", ["すべて", "未確認", "確認済み"])
    review_status_filter = None
    if status_filter_label != "すべて":
        review_status_filter = REVIEW_STATUS_BY_LABEL[status_filter_label]

    articles = get_articles(review_status=review_status_filter)

    if not articles:
        st.info("条件に一致する記事データがありません。")
    else:
        tags = sorted({tag for article in articles for tag in article["tags"]})
        selected_view = st.sidebar.radio("表示", ["新着記事", "重要記事", "タグ別記事"])
        selected_tag = None
        if selected_view == "タグ別記事":
            selected_tag = st.sidebar.selectbox("タグ", tags)

        if selected_view == "重要記事":
            visible_articles = [article for article in articles if article["importance"] >= 4]
        elif selected_view == "タグ別記事" and selected_tag:
            visible_articles = [
                article for article in articles if selected_tag in article["tags"]
            ]
        else:
            visible_articles = articles

        for article in visible_articles:
            render_article_card(article)

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
