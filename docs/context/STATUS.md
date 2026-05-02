# STATUS

Last Updated: 2026-05-02

## Current Task Bundle

- 主対象: AI 要約、タグ付け、重要度付け、週次ダイジェストの MVP 範囲を決める
- この bundle で扱う範囲:
  - AI 要約、タグ付け、重要度付け、週次ダイジェストを MVP に含めるかの判断
  - 手動入力で開始する項目と自動生成を試作する項目の分離
  - 自動生成する場合の入力データ、出力項目、保存可否の仕様化
  - 実装タスクを追加する場合の backlog triage
- この bundle で扱わないこと:
  - AI 要約処理の実装そのもの
  - 定期実行
  - Cloudflare 連携
  - 公開アプリ化

## Current State

- `rm-trend-radar` は、ホテル・レベニューマネジメント領域の海外公開記事を日本語で確認する個人用 Web アプリとして開始した。
- MVP の構成は Python、Streamlit、SQLite とする。
- GitHub private repository `NemuKei/rm-trend-radar` を作成し、ローカル `origin` に設定した。
- 初期実装ではサンプル記事を SQLite に保存し、Streamlit で新着記事、重要記事、タグ別記事を表示する。
- 取得対象サイトの調査と取得契約は `docs/spec_001_sources.md` を正本にする。
- `P2-01` で初期 MVP の取得対象を IDeaS、SiteMinder、RoomPriceGenie、Revfine、Hotel Speak の 5 件に決めた。
- Mews、Lighthouse、Hospitality Net は初期 MVP では後回しにする。
- `P2-02` で RSS item の保存項目、重複判定、更新判定、取得失敗時の扱いを `docs/spec_001_sources.md` に仕様化した。
- `P3-01` で初期対象 5 件の source config と RSS item parser を実装した。
- `P3-02` で parser の戻り値を SQLite に upsert する処理を実装した。
- `P3-03` で手動 RSS 取得入口 `python -m rm_trend_radar fetch` を追加した。
- IDeaS の live dry-run では `fetched=10`, `added=0`, `updated=0`, `unchanged=0`, `failed=0` を確認した。
- `.venv\Scripts\python.exe` は、`pyvenv.cfg` の参照先を現在の端末で利用できる Python 3.12.13 に合わせて復旧済み。`.venv` は git 管理外のため、この復旧内容はリポジトリ差分には含めない。
- 次の本線は、AI 要約、タグ付け、重要度付け、週次ダイジェストの MVP 範囲を決めることから始める。

## Next Re-entry

次スレッドは、AI 要約、タグ付け、重要度付け、週次ダイジェストの MVP 範囲決定から始める。

### Thread Contract

- 今回の種別: `mainline-task`
- 主対象: AI 要約、タグ付け、重要度付け、週次ダイジェストの MVP 範囲を決める
- bundle に含める Task ID: 未採番。必要に応じて `P4-01` 以降を追加する。
- 最初に読む正本:
  - `AGENTS.md`
  - `docs/context/STATUS.md`
  - `docs/tasks_backlog.md`
  - `docs/spec_001_sources.md`
  - `docs/context/DECISIONS.md`
- 次スレッドで最初にやること:
  1. `docs/context/INTENT.md` の判断原則を確認する。
  2. 現在の `articles` テーブルで手動入力する項目と、AI で生成したい項目を分ける。
  3. AI 要約を使う場合に、RSS の `description` や記事本文を保存しない契約とどう両立するかを整理する。
  4. MVP では手動入力を優先するか、AI 生成を試作するかを決める。
  5. 決定内容を `DECISIONS.md`、必要な仕様を `spec_*.md`、実行タスクを `tasks_backlog.md` に反映する。
- この bundle で変更しない契約:
  - 記事本文全文を保存しない。
  - 記事本文全文を転載しない。
  - ログインが必要なページ、有料記事、会員限定記事を取得対象にしない。
  - Cloudflare、独自ドメイン、認証、定期実行は初期 MVP の前提にしない。
  - 実装は、取得対象と取得契約を文書化してから始める。
- 終了条件:
  - AI 要約、タグ、重要度、示唆、週次ダイジェストのうち、MVP で手動入力にする項目と自動生成の試作対象にする項目が分かれている。
  - 自動生成を行う場合、入力として使うデータ、保存する出力、保存しないデータが仕様化されている。
  - 実装タスクが backlog に追加され、Now/Next が更新されている。
- subagent 利用方針:
  - 委譲してよい作業: AI 要約ワークフロー案、タグ体系案、週次ダイジェスト案の比較整理。
  - 委譲してはいけない作業: 仕様確定前の AI API 実装、定期実行、Cloudflare 連携。
  - メインスレッドが担う作業: MVP 範囲決定、正本反映、backlog と STATUS の同期。

## Verify / Confirmation State

- verify 済み:
  - `.venv\Scripts\python.exe -m rm_trend_radar`
  - `.venv\Scripts\python.exe -m compileall src app.py`
  - `.venv\Scripts\python.exe -m pytest` は 2026-05-02 の初期実装時点では通過済み
  - `.venv\Scripts\python.exe -m streamlit run app.py --server.headless=true --server.port=8501 --browser.gatherUsageStats=false` を一時起動し、`http://127.0.0.1:8501` が HTTP 200 を返すことを確認
  - GitHub private repository `NemuKei/rm-trend-radar` へ `main` を push 済み
  - `P2-01` 初期取得対象サイト調査を `docs/spec_001_sources.md` へ反映済み
  - `P2-02` 記事取得スキーマを `docs/spec_001_sources.md` へ反映済み
  - `P3-01` source config と RSS item parser の追加
  - `P3-02` RSS item upsert の追加
  - `P3-03` 手動 RSS 取得 CLI の追加
  - `.venv\Scripts\python.exe --version` が `Python 3.12.13` を返すことを確認
  - `.venv\Scripts\python.exe -m compileall src app.py` が通過することを確認
  - `.venv\Scripts\python.exe -m pytest tests\test_rss.py -p no:cacheprovider` が 5 passed になることを確認
  - `.venv\Scripts\python.exe` の手動 smoke で RSS item の新規追加と placeholder 保存が成功することを確認
  - `.venv\Scripts\python.exe` の手動 smoke で fetch と upsert の接続が `added=1` になることを確認
  - `.venv\Scripts\python.exe -m rm_trend_radar fetch --source unknown` が exit 1 で未知 source を stderr 表示することを確認
  - ネットワーク許可後、`.venv\Scripts\python.exe -m rm_trend_radar fetch --dry-run --timeout 20` が exit 0 で初期対象 5 件すべてを取得できることを確認。件数は IDeaS 10、SiteMinder 50、RoomPriceGenie 40、Revfine 18、Hotel Speak 10
  - `.venv\Scripts\python.exe -m streamlit run app.py --server.headless=true --server.port=8502 --browser.gatherUsageStats=false` を一時起動し、`http://127.0.0.1:8502` が HTTP 200 を返すことを確認
  - `PYTHONPATH=src;.venv\Lib\site-packages` を指定し、バンドル Python で `tests\test_rss.py` が 5 passed
  - バンドル Python の手動 smoke で RSS item の新規追加、重複時更新、手動確認項目を上書きしないことを確認
  - User-Agent 修正後、バンドル Python の手動 smoke で fetch と upsert の接続が `added=1` になることを確認
  - バンドル Python で `python -m rm_trend_radar fetch --source unknown` が exit 1 で未知 source を stderr 表示することを確認
  - ネットワーク許可後、バンドル Python で `python -m rm_trend_radar fetch --source IDeaS --dry-run --timeout 20` が exit 0 で `fetched=10` を表示することを確認
  - ネットワーク許可後、バンドル Python で `python -m rm_trend_radar fetch --dry-run --timeout 20` が exit 0 で初期対象 5 件すべてを取得できることを確認。件数は IDeaS 10、SiteMinder 50、RoomPriceGenie 40、Revfine 18、Hotel Speak 10
- 未確認:
  - 実サイトからの記事取得
  - GitHub Actions などの CI 実行
  - `.venv\Scripts\python.exe -m pytest` の全件実行は、pytest が作成する一時ディレクトリを列挙できず `PermissionError [WinError 5]` で終了する。`tests\test_rss.py` と手動 smoke で主要処理は確認済みだが、`tmp_path` を使う DB/fetch テストの pytest 実行完了は未確認。

## Open Questions

- 要約、タグ、重要度、示唆を手動入力から始めるか、自動生成の試作を先に入れるか。
- Cloudflare と独自ドメインを、紹介 LP の導線だけに使うか、将来のアプリ公開先として使うか。
