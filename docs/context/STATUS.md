# STATUS

Last Updated: 2026-05-02

## Current Task Bundle

- 主対象: 新規 `rm-trend-radar` リポジトリの初期立ち上げ
- この bundle で扱う範囲:
  - ローカルリポジトリ作成
  - GitHub private remote 作成
  - Python 仮想環境作成
  - 依存関係インストール
  - README と最小正本文書の整備
  - SQLite 初期化
  - Streamlit の最小起動確認
- この bundle で扱わないこと:
  - 実サイトからの記事自動取得
  - AI 要約処理の実装
  - 定期実行
  - Cloudflare 連携
  - 公開アプリ化

## Current State

- `rm-trend-radar` は、ホテル・レベニューマネジメント領域の海外公開記事を日本語で確認する個人用 Web アプリとして開始した。
- MVP の構成は Python、Streamlit、SQLite とする。
- GitHub private repository `NemuKei/rm-trend-radar` を作成し、ローカル `origin` に設定した。
- 初期実装ではサンプル記事を SQLite に保存し、Streamlit で新着記事、重要記事、タグ別記事を表示する。

## Next Re-entry

次に扱う候補は、実サイト取得に入る前の対象サイト調査である。

1. 初期取得対象サイトを 3〜5 件に絞る。
2. 各サイトについて RSS の有無、公開ブログ一覧 URL、取得頻度の妥当性、保存してよい項目を確認する。
3. `docs/spec_001_sources.md` を作成するか、`docs/spec_000_overview.md` に追記するかを判断する。

## Verify / Confirmation State

- verify 済み:
  - `.venv\Scripts\python.exe -m rm_trend_radar`
  - `.venv\Scripts\python.exe -m compileall src app.py`
  - `.venv\Scripts\python.exe -m pytest`
  - `.venv\Scripts\python.exe -m streamlit run app.py --server.headless=true --server.port=8501 --browser.gatherUsageStats=false` を一時起動し、`http://127.0.0.1:8501` が HTTP 200 を返すことを確認
- 未確認:
  - 実サイトからの記事取得
  - GitHub Actions などの CI 実行

## Open Questions

- 初期取得対象サイトをどこまで絞るか。
- 要約、タグ、重要度、示唆を手動入力から始めるか、自動生成の試作を先に入れるか。
- Cloudflare と独自ドメインを、紹介 LP の導線だけに使うか、将来のアプリ公開先として使うか。