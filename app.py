from __future__ import annotations

import streamlit as st

from rm_trend_radar.db import get_articles, init_db


st.set_page_config(page_title="RM Trend Radar", page_icon="📡", layout="wide")

init_db(seed=True)

st.title("RM Trend Radar")
st.caption("海外レベニューマネジメント記事を日本語で確認する個人用ダッシュボード")

articles = get_articles()

if not articles:
    st.info("記事データがまだありません。")
    st.stop()

tags = sorted({tag for article in articles for tag in article["tags"]})
selected_view = st.sidebar.radio("表示", ["新着記事", "重要記事", "タグ別記事"])
selected_tag = None
if selected_view == "タグ別記事":
    selected_tag = st.sidebar.selectbox("タグ", tags)

if selected_view == "重要記事":
    visible_articles = [article for article in articles if article["importance"] >= 4]
elif selected_view == "タグ別記事" and selected_tag:
    visible_articles = [article for article in articles if selected_tag in article["tags"]]
else:
    visible_articles = articles

for article in visible_articles:
    with st.container(border=True):
        cols = st.columns([0.72, 0.28])
        with cols[0]:
            st.subheader(article["title_ja"])
            st.write(article["summary_ja"])
            st.markdown(f"[原文を開く]({article['url']})")
        with cols[1]:
            st.metric("重要度", article["importance"])
            st.write(f"取得元: {article['source_name']}")
            st.write(f"公開日: {article['published_date']}")
            st.write("タグ: " + ", ".join(article["tags"]))
        st.divider()
        st.write("RM担当者向けの示唆")
        st.write(article["rm_implication"])