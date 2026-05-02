# STATUS

Last Updated: 2026-05-02

## Current Task Bundle

- 主対象: 次スレッド移行に耐える正本文書整備
- この bundle で扱う範囲:
  - 初期立ち上げ結果の正本反映
  - 次スレッドの task bundle 明確化
  - `P2-01` と `P2-02` の仕様受け皿作成
  - README の初期化コマンド確認
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
- 取得対象サイトの調査と取得契約は `docs/spec_001_sources.md` を正本にする。

## Next Re-entry

次スレッドは、実サイト取得に入る前の対象サイト調査から始める。

### Thread Contract

- 今回の種別: `mainline-task`
- 主対象: `P2-01` 初期取得対象サイトを調査する
- bundle に含める Task ID: `P2-01`, `P2-02`
- 最初に読む正本:
  - `AGENTS.md`
  - `docs/context/STATUS.md`
  - `docs/tasks_backlog.md`
  - `docs/spec_001_sources.md`
  - `docs/context/DECISIONS.md`
- 次スレッドで最初にやること:
  1. `docs/spec_001_sources.md` の `Candidate Sources` を確認する。
  2. IDeaS、SiteMinder、Mews、RoomPriceGenie、Lighthouse、Revfine、Hospitality Net、Hotel Speak から、初期調査対象を 3〜5 件に絞る。
  3. 各サイトについて、公式 RSS の有無、公開ブログ一覧 URL、取得してよい項目、想定取得頻度、注意点を確認する。
  4. 調査結果を `docs/spec_001_sources.md` の `Source Evaluation Table` に反映する。
- この bundle で変更しない契約:
  - 記事本文全文を保存しない。
  - 記事本文全文を転載しない。
  - ログインが必要なページ、有料記事、会員限定記事を取得対象にしない。
  - Cloudflare、独自ドメイン、認証、定期実行は初期 MVP の前提にしない。
  - 実装は、取得対象と取得契約を文書化してから始める。
- 終了条件:
  - 初期取得対象 3〜5 件が選ばれている。
  - 各対象について、RSS の有無、公開ブログ一覧 URL、保存項目、取得頻度、取得上の注意点が記録されている。
  - `P2-02` で確定すべき取得スキーマの未決事項が分かる。
- subagent 利用方針:
  - 委譲してよい作業: 各候補サイトの RSS、公開ブログ一覧 URL、robots.txt、利用規約の確認。
  - 委譲してはいけない作業: 取得可否の最終判断、保存項目の契約確定、実装開始。
  - メインスレッドが担う作業: 調査結果の統合、`docs/spec_001_sources.md` の更新、backlog と STATUS の同期。

## Verify / Confirmation State

- verify 済み:
  - `.venv\Scripts\python.exe -m rm_trend_radar`
  - `.venv\Scripts\python.exe -m compileall src app.py`
  - `.venv\Scripts\python.exe -m pytest`
  - `.venv\Scripts\python.exe -m streamlit run app.py --server.headless=true --server.port=8501 --browser.gatherUsageStats=false` を一時起動し、`http://127.0.0.1:8501` が HTTP 200 を返すことを確認
  - GitHub private repository `NemuKei/rm-trend-radar` へ `main` を push 済み
- 未確認:
  - 実サイトからの記事取得
  - GitHub Actions などの CI 実行

## Open Questions

- 初期取得対象サイトをどこまで絞るか。
- 要約、タグ、重要度、示唆を手動入力から始めるか、自動生成の試作を先に入れるか。
- Cloudflare と独自ドメインを、紹介 LP の導線だけに使うか、将来のアプリ公開先として使うか。
