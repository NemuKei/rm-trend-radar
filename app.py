from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from rm_trend_radar.db import (
    REVIEW_STATUS_CONFIRMED,
    REVIEW_STATUS_UNREVIEWED,
    get_articles,
    get_digest_articles,
    get_public_candidate_articles,
    init_db,
    update_article_interest_flags,
    update_article_review,
)
from rm_trend_radar.digest import generate_weekly_digest_markdown
from rm_trend_radar.public_export import (
    generate_public_candidate_json,
    generate_public_candidate_markdown,
)
from rm_trend_radar.title_priority import (
    TITLE_PRIORITY_HIGH,
    TITLE_PRIORITY_LOW,
    TITLE_PRIORITY_MEDIUM,
)


REVIEW_STATUS_LABELS = {
    REVIEW_STATUS_UNREVIEWED: "未確認",
    REVIEW_STATUS_CONFIRMED: "確認済み",
}
REVIEW_STATUS_BY_LABEL = {label: value for value, label in REVIEW_STATUS_LABELS.items()}
TITLE_PRIORITY_LABELS = {
    TITLE_PRIORITY_HIGH: "高",
    TITLE_PRIORITY_MEDIUM: "中",
    TITLE_PRIORITY_LOW: "低",
}
TITLE_PRIORITY_BY_LABEL = {
    label: value for value, label in TITLE_PRIORITY_LABELS.items()
}


st.set_page_config(page_title="RM Trend Radar", page_icon="📡", layout="wide")

init_db(seed=False)

st.title("RM Trend Radar")
st.caption("海外レベニューマネジメント記事を日本語で確認する個人用ダッシュボード")

tab_articles, tab_reviewed, tab_digest, tab_public_candidates = st.tabs(
    ["記事確認", "確認済みレビュー", "週次ダイジェスト", "公開候補"]
)


def split_tags(value: str) -> list[str]:
    return [tag.strip() for tag in value.replace("\n", ",").split(",") if tag.strip()]


def filter_articles(
    articles: list[dict],
    *,
    review_status: str | None,
    selected_sources: list[str],
    selected_tag: str,
    interest_candidate_filter: str,
    public_candidate_filter: str,
    title_priority_filter: str | None,
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
        if interest_candidate_filter == "気になるのみ" and not article["interest_candidate"]:
            continue
        if interest_candidate_filter == "未指定" and article["interest_candidate"]:
            continue
        if public_candidate_filter == "候補のみ" and not article["public_candidate"]:
            continue
        if public_candidate_filter == "候補外" and article["public_candidate"]:
            continue
        if (
            title_priority_filter is not None
            and article["title_priority"] != title_priority_filter
        ):
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
        article["title_priority"],
        article["title_priority_reason"],
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
                "気になる": article["interest_candidate"],
                "確認": REVIEW_STATUS_LABELS[article["review_status"]],
                "仮重要度": TITLE_PRIORITY_LABELS[article["title_priority"]],
                "重要度": article["importance"],
                "公開候補": "候補" if article["public_candidate"] else "",
                "タイトル": article["title_ja"],
                "タグ": ", ".join(article["tags"][:4]),
            }
        )
    return rows


def iter_editor_rows(edited_rows) -> list[dict]:
    if hasattr(edited_rows, "to_dict"):
        return edited_rows.to_dict("records")
    return list(edited_rows)


def render_article_detail(article: dict) -> None:
    status_label = REVIEW_STATUS_LABELS[article["review_status"]]
    st.divider()
    st.subheader(article["title_ja"])

    meta_cols = st.columns([0.12, 0.12, 0.14, 0.14, 0.13, 0.13, 0.13, 0.09])
    meta_cols[0].metric("重要度", article["importance"])
    meta_cols[1].metric(
        "仮重要度",
        TITLE_PRIORITY_LABELS[article["title_priority"]],
    )
    meta_cols[2].write(f"気になる: {'対象' if article['interest_candidate'] else '未指定'}")
    meta_cols[3].write(f"確認状態: {status_label}")
    meta_cols[4].write(f"公開候補: {'候補' if article['public_candidate'] else '未指定'}")
    meta_cols[5].write(f"取得元: {article['source_name']}")
    meta_cols[6].write(f"公開日: {article['published_date']}")
    meta_cols[7].markdown(f"[原文]({article['url']})")

    st.write("タグ: " + ", ".join(article["tags"]))
    st.write("タイトル仮重要度の理由: " + article["title_priority_reason"])
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
            interest_candidate = st.checkbox(
                "気になる記事として残す",
                value=article["interest_candidate"],
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
                interest_candidate=interest_candidate,
            )
            st.success("保存しました。")
            st.rerun()


def reviewed_table_rows(articles: list[dict]) -> list[dict]:
    return [
        {
            "id": article["id"],
            "公開日": article["published_date"],
            "取得元": article["source_name"],
            "重要度": article["importance"],
            "公開候補": "候補" if article["public_candidate"] else "",
            "タイトル": article["title_ja"],
            "タグ": ", ".join(article["tags"][:5]),
        }
        for article in articles
    ]


def render_reviewed_article(article: dict) -> None:
    st.subheader(article["title_ja"])
    st.caption(article["title_en"])

    meta_cols = st.columns([0.12, 0.16, 0.18, 0.18, 0.18, 0.18])
    meta_cols[0].metric("重要度", article["importance"])
    meta_cols[1].write(f"取得元: {article['source_name']}")
    meta_cols[2].write(f"公開日: {article['published_date']}")
    meta_cols[3].write(f"公開候補: {'候補' if article['public_candidate'] else '未指定'}")
    meta_cols[4].write(f"気になる: {'対象' if article['interest_candidate'] else '未指定'}")
    meta_cols[5].markdown(f"[原文で詳細を見る]({article['url']})")

    st.write("タグ: " + ", ".join(article["tags"]))
    st.markdown("#### 要約")
    st.write(article["summary_ja"])
    st.markdown("#### RM担当者向けの示唆")
    st.write(article["rm_implication"])

    with st.expander("公開導線の確認", expanded=True):
        st.write("LP 掲載時の役割: 短い紹介と独自の示唆だけを掲載し、詳細理解は原文サイトへ戻す。")
        st.write("X 投稿時の役割: 記事の論点を短く知らせ、詳細は LP または原文リンクで確認してもらう。")
        st.markdown(f"- 原文 URL: {article['url']}")

    with st.expander("編集", expanded=False):
        with st.form(key=f"reviewed_form_{article['id']}"):
            title_ja = st.text_input("日本語タイトル", value=article["title_ja"])
            summary_ja = st.text_area(
                "日本語要約",
                value=article["summary_ja"],
                height=220,
            )
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
                height=180,
            )
            note = st.text_area("手動メモ", value=article["note"], height=140)
            public_candidate = st.checkbox(
                "複業リポ側 LP の公開候補にする",
                value=article["public_candidate"],
            )
            interest_candidate = st.checkbox(
                "気になる記事として残す",
                value=article["interest_candidate"],
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
                review_status=REVIEW_STATUS_CONFIRMED,
                public_candidate=public_candidate,
                interest_candidate=interest_candidate,
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
        interest_candidate_filter = st.sidebar.radio(
            "気になる",
            ["すべて", "気になるのみ", "未指定"],
        )
        title_priority_filter_label = st.sidebar.radio(
            "タイトル仮重要度",
            ["すべて", "高", "中", "低"],
        )
        title_priority_filter = None
        if title_priority_filter_label != "すべて":
            title_priority_filter = TITLE_PRIORITY_BY_LABEL[title_priority_filter_label]
        min_importance = st.sidebar.slider("最低重要度", 1, 5, 1)
        selected_tag = st.sidebar.selectbox("タグ", ["すべて", *all_tags])
        keyword = st.sidebar.text_input("検索")

        visible_articles = filter_articles(
            articles,
            review_status=review_status_filter,
            selected_sources=selected_sources,
            selected_tag=selected_tag,
            interest_candidate_filter=interest_candidate_filter,
            public_candidate_filter=public_candidate_filter,
            title_priority_filter=title_priority_filter,
            min_importance=min_importance,
            keyword=keyword,
        )

        summary_cols = st.columns(6)
        summary_cols[0].metric("表示件数", len(visible_articles))
        summary_cols[1].metric(
            "高候補",
            sum(
                1
                for article in visible_articles
                if article["title_priority"] == TITLE_PRIORITY_HIGH
            ),
        )
        summary_cols[2].metric(
            "気になる",
            sum(1 for article in visible_articles if article["interest_candidate"]),
        )
        summary_cols[3].metric(
            "未確認",
            sum(
                1
                for article in visible_articles
                if article["review_status"] == REVIEW_STATUS_UNREVIEWED
            ),
        )
        summary_cols[4].metric(
            "確認済み",
            sum(
                1
                for article in visible_articles
                if article["review_status"] == REVIEW_STATUS_CONFIRMED
            ),
        )
        summary_cols[5].metric(
            "公開候補",
            sum(1 for article in visible_articles if article["public_candidate"]),
        )

        if not visible_articles:
            st.info("条件に一致する記事データがありません。")
        else:
            edited_rows = st.data_editor(
                table_rows(visible_articles),
                hide_index=True,
                use_container_width=True,
                height=430,
                column_config={
                    "id": None,
                    "公開日": st.column_config.TextColumn(width="small"),
                    "取得元": st.column_config.TextColumn(width="small"),
                    "気になる": st.column_config.CheckboxColumn(width="small"),
                    "確認": st.column_config.TextColumn(width="small"),
                    "仮重要度": st.column_config.TextColumn(width="small"),
                    "重要度": st.column_config.NumberColumn(width="small"),
                    "公開候補": st.column_config.TextColumn(width="small"),
                    "タイトル": st.column_config.TextColumn(width="large"),
                    "タグ": st.column_config.TextColumn(width="medium"),
                },
                disabled=[
                    "公開日",
                    "取得元",
                    "確認",
                    "仮重要度",
                    "重要度",
                    "公開候補",
                    "タイトル",
                    "タグ",
                ],
                key="article_interest_editor",
            )
            if st.button("気になるを保存", type="primary"):
                update_article_interest_flags(
                    {
                        int(row.get("id", visible_articles[index]["id"])): bool(
                            row["気になる"]
                        )
                        for index, row in enumerate(iter_editor_rows(edited_rows))
                    }
                )
                st.success("気になるフラグを保存しました。")
                st.rerun()

            detail_options = {
                f"{article['published_date']} | {article['source_name']} | {article['title_ja']}": index
                for index, article in enumerate(visible_articles)
            }
            selected_detail_label = st.selectbox(
                "詳細表示する記事",
                list(detail_options),
            )
            render_article_detail(visible_articles[detail_options[selected_detail_label]])

with tab_reviewed:
    reviewed_articles = get_articles(review_status=REVIEW_STATUS_CONFIRMED)

    if not reviewed_articles:
        st.info("確認済み記事はまだありません。")
    else:
        reviewed_sources = sorted(
            {article["source_name"] for article in reviewed_articles}
        )
        reviewed_source_filter = st.multiselect(
            "取得元",
            reviewed_sources,
            default=reviewed_sources,
            key="reviewed_sources",
        )
        reviewed_public_filter = st.radio(
            "公開候補",
            ["すべて", "候補のみ", "候補外"],
            key="reviewed_public_filter",
        )
        reviewed_min_importance = st.slider(
            "最低重要度",
            min_value=1,
            max_value=5,
            value=1,
            key="reviewed_min_importance",
        )
        reviewed_keyword = st.text_input("検索", key="reviewed_keyword")

        visible_reviewed = []
        for article in reviewed_articles:
            if (
                reviewed_source_filter
                and article["source_name"] not in reviewed_source_filter
            ):
                continue
            if reviewed_public_filter == "候補のみ" and not article["public_candidate"]:
                continue
            if reviewed_public_filter == "候補外" and article["public_candidate"]:
                continue
            if article["importance"] < reviewed_min_importance:
                continue
            if reviewed_keyword.strip().lower() not in _search_text(article):
                continue
            visible_reviewed.append(article)

        reviewed_cols = st.columns(4)
        reviewed_cols[0].metric("表示件数", len(visible_reviewed))
        reviewed_cols[1].metric(
            "重要度5",
            sum(1 for article in visible_reviewed if article["importance"] == 5),
        )
        reviewed_cols[2].metric(
            "公開候補",
            sum(1 for article in visible_reviewed if article["public_candidate"]),
        )
        reviewed_cols[3].metric(
            "気になる",
            sum(1 for article in visible_reviewed if article["interest_candidate"]),
        )

        if not visible_reviewed:
            st.info("条件に一致する確認済み記事がありません。")
        else:
            st.dataframe(
                reviewed_table_rows(visible_reviewed),
                hide_index=True,
                use_container_width=True,
                height=250,
                column_config={
                    "id": None,
                    "公開日": st.column_config.TextColumn(width="small"),
                    "取得元": st.column_config.TextColumn(width="small"),
                    "重要度": st.column_config.NumberColumn(width="small"),
                    "公開候補": st.column_config.TextColumn(width="small"),
                    "タイトル": st.column_config.TextColumn(width="large"),
                    "タグ": st.column_config.TextColumn(width="medium"),
                },
            )
            reviewed_options = {
                f"{article['importance']} | {article['published_date']} | {article['title_ja']}": index
                for index, article in enumerate(visible_reviewed)
            }
            selected_reviewed_label = st.selectbox(
                "読む記事",
                list(reviewed_options),
            )
            render_reviewed_article(
                visible_reviewed[reviewed_options[selected_reviewed_label]]
            )

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

with tab_public_candidates:
    public_candidate_articles = get_public_candidate_articles()
    public_markdown = generate_public_candidate_markdown(public_candidate_articles)
    public_json = generate_public_candidate_json(public_candidate_articles)

    st.write(f"対象記事数: {len(public_candidate_articles)}")
    st.markdown(public_markdown)
    st.text_area("Markdown", value=public_markdown, height=320)
    st.text_area("JSON", value=public_json, height=320)
