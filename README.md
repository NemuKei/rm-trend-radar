# rm-trend-radar

`rm-trend-radar` は、ホテル・レベニューマネジメント領域の海外公開記事を収集し、日本語で確認するための個人用 Web アプリです。

初期 MVP は、Python、Streamlit、SQLite でローカル実行する軽量構成です。対象は IDeaS、SiteMinder、Mews、RoomPriceGenie、Lighthouse、Revfine、Hospitality Net、Hotel Speak などの公開ブログや記事サイトを想定します。

## MVP の目的

- 海外のレベニューマネジメント関連トレンドを、日本語で短時間に確認できるようにする。
- 原文リンク、日本語タイトル、日本語要約、タグ、重要度、レベニューマネジメント担当者向けの示唆、手動メモを一元管理する。
- 自動収集、要約、重要度付けを将来追加できるデータ構造と画面構成を先に確認する。

## MVP で扱わないこと

- 記事本文の全文保存
- 記事本文の全文転載
- ログインが必要なページの取得
- 原文記事の代替公開
- Cloudflare、独自ドメイン、認証付き公開アプリへの展開
- 定期実行基盤の本番運用

## セットアップ

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m rm_trend_radar
```

## 起動

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

ブラウザで Streamlit が表示するローカル URL を開きます。通常は `http://localhost:8501` です。

## 現在の実装範囲

- SQLite データベースを初期化する。
- サンプル記事を登録する。
- Streamlit で新着記事、重要記事、タグ別記事を確認する。
- 記事本文ではなく、原文リンクと日本語の確認用情報を表示する。

## 保存する主なデータ

- 原文 URL
- 取得元サイト名
- 原文公開日
- 英語タイトル
- 日本語タイトル
- 日本語要約
- タグ
- 重要度
- レベニューマネジメント担当者向けの示唆
- 手動メモ

## ドキュメント

- 現在地: `docs/context/STATUS.md`
- 判断原則: `docs/context/INTENT.md`
- 意思決定: `docs/context/DECISIONS.md`
- タスク: `docs/tasks_backlog.md`
- 仕様概要: `docs/spec_000_overview.md`
- 取得対象調査と取得契約: `docs/spec_001_sources.md`
