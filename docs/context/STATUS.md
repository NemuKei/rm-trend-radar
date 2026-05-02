# STATUS

Last Updated: 2026-05-02

## Current Task Bundle

- 主対象: 実記事を取得して確認ワークフローを画面評価する
- この bundle で扱う範囲:
  - 初期対象 5 件から実記事を取得する
  - 記事確認タブで、未確認記事の見え方、確認フォームの入力しやすさ、タグ表示、重要度表示を確認する
  - 週次ダイジェストタブで、対象期間、最低重要度、Markdown の読みやすさを確認する
  - 実記事で見つかった調整点を backlog に追加する
  - 実装タスクを追加する場合の backlog triage
- この bundle で扱わないこと:
  - AI API 実装そのもの
  - AI 候補生成の仕様確定
  - 記事本文全文の保存
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
- `P4-01` で初期 MVP では AI API を使わず、人間が確認済みデータを蓄積する方針を決めた。
- `P4-02` で記事の確認状態、手動確認項目の保存処理、Streamlit の記事編集フォームを追加した。
- `P4-03` で確認済み記事だけから Markdown 形式の週次ダイジェストを表示する画面を追加した。
- 2026-05-02 の画面確認では、現在の画面構成は暫定的に許容し、次の調整は実記事を可視化してから判断する方針とした。
- `P4-05` で初期対象 5 件から実記事 128 件をローカル SQLite に取得した。内訳は IDeaS 10、SiteMinder 50、RoomPriceGenie 40、Revfine 18、Hotel Speak 10。
- 実記事確認の邪魔にならないように、Streamlit 起動時のサンプル記事自動投入を停止した。既存ローカル DB から `Sample Source` のサンプル記事 2 件も削除した。
- 実記事一覧はカード表示では俯瞰しづらいため、`P4-06` で記事確認画面を表形式の俯瞰テーブルに変更し、複業リポ側 LP の公開候補フラグを追加した。
- 今後の方向性として、`rm-trend-radar` は非公開の収集、確認、編集、選別用リポジトリとし、複業リポ側 LP は確認済みで公開してよい内容だけを掲載する公開面として扱う。
- `P4-07` で、公開候補タブを追加した。対象は確認済みかつ公開候補の記事だけで、Markdown と JSON の preview を表示する。手動メモは export preview に含めない。
- `P4-09` で、記事タイトルだけから読む順番の候補を `high`, `medium`, `low` として保存する `title_priority` と、判定理由を保存する `title_priority_reason` を追加した。これは人間が確定する `importance` とは別項目であり、公開候補選定や週次ダイジェスト掲載の確定条件には使わない。
- ローカル DB の実記事 128 件を `title_priority` で再計算した結果は、`high` 62 件、`medium` 66 件、`low` 0 件である。これはタイトルだけに基づく仮分類であり、記事内容確認後の `importance` とは別に扱う。
- IDeaS の live dry-run では `fetched=10`, `added=0`, `updated=0`, `unchanged=0`, `failed=0` を確認した。
- `.venv\Scripts\python.exe` は、`pyvenv.cfg` の参照先を現在の端末で利用できる Python 3.12.13 に合わせて復旧済み。`.venv` は git 管理外のため、この復旧内容はリポジトリ差分には含めない。
- 次の本線は、タイトル仮重要度で実記事を絞り込み、確認済みにする記事と公開候補にする記事を選ぶことから始める。

## Next Re-entry

次スレッドは、実記事を取得して確認ワークフローを画面評価することから始める。

### Thread Contract

- 今回の種別: `mainline-task`
- 主対象: 実記事を取得して確認ワークフローを画面評価する
- bundle に含める Task ID: `P4-05`
- 最初に読む正本:
  - `AGENTS.md`
  - `docs/context/STATUS.md`
  - `docs/tasks_backlog.md`
  - `docs/spec_001_sources.md`
  - `docs/spec_002_review_workflow.md`
  - `docs/context/DECISIONS.md`
- 次スレッドで最初にやること:
  1. `docs/context/INTENT.md` の判断原則を確認する。
  2. `http://localhost:8502/` を更新し、記事確認タブで俯瞰テーブル、取得元 filter、確認状態 filter、公開候補 filter、タイトル仮重要度 filter、最低重要度 filter、タグ filter、検索が使いやすいか確認する。
  3. 必要に応じて、いくつかの記事を確認済みまたは公開候補に変更し、詳細欄と週次ダイジェストタブで表示を確認する。
  4. UI、タグ、重要度、公開候補、ダイジェスト Markdown、公開候補 preview の調整点を整理する。
  5. 必要な調整を `tasks_backlog.md` に追加し、Now/Next を更新する。
- この bundle で変更しない契約:
  - 記事本文全文を保存しない。
  - 記事本文全文を転載しない。
  - ログインが必要なページ、有料記事、会員限定記事を取得対象にしない。
  - Cloudflare、独自ドメイン、認証、定期実行は初期 MVP の前提にしない。
  - AI API 実装は、入力データ、保存する出力、保存しないデータを文書化してから始める。
- 終了条件:
  - 初期対象 5 件から取得した実記事が画面に表示されている。
  - 記事確認タブと週次ダイジェストタブについて、維持する点と調整する点が分かれている。
  - 調整が必要な場合、実装タスクが backlog に追加され、Now/Next が更新されている。
- subagent 利用方針:
  - 委譲してよい作業: 実記事表示後の UI 調整候補、タグ整理候補、ダイジェスト文面構造の比較整理。
  - 委譲してはいけない作業: 仕様確定前の AI API 実装、記事本文全文保存、定期実行、Cloudflare 連携。
  - メインスレッドが担う作業: 実記事取得、画面確認、調整タスク化、backlog と STATUS の同期。

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
  - `P4-01` 初期 MVP の AI 範囲と確認ワークフロー仕様の確定
  - `P4-02` 記事確認状態と手動確認項目の保存処理の追加
  - `P4-03` 確認済み記事から週次ダイジェストを表示する処理の追加
  - `.venv\Scripts\python.exe --version` が `Python 3.12.13` を返すことを確認
  - `.venv\Scripts\python.exe -m compileall src app.py` が通過することを確認
  - `.venv\Scripts\python.exe -m pytest tests\test_rss.py -p no:cacheprovider` が 5 passed になることを確認
  - `.venv\Scripts\python.exe -m pytest tests\test_digest.py tests\test_rss.py -p no:cacheprovider` が 7 passed になることを確認
  - `.venv\Scripts\python.exe` の手動 smoke で RSS item の新規追加と placeholder 保存が成功することを確認
  - `.venv\Scripts\python.exe` の手動 smoke で fetch と upsert の接続が `added=1` になることを確認
  - `.venv\Scripts\python.exe` の手動 smoke で既存 schema に `review_status` と `reviewed_at` を追加できることを確認
  - `.venv\Scripts\python.exe` の手動 smoke で記事確認項目を保存でき、RSS 再取得で確認項目と確認状態が上書きされないことを確認
  - `.venv\Scripts\python.exe` の手動 smoke で確認済み、対象期間内、重要度条件を満たす記事だけがダイジェスト対象になることを確認
  - `.venv\Scripts\python.exe` の手動 smoke で fetch した新規記事が `review_status=unreviewed` になることを確認
  - `.venv\Scripts\python.exe -m streamlit run app.py --server.headless=true --server.port=8503 --browser.gatherUsageStats=false` を一時起動し、`http://127.0.0.1:8503` が HTTP 200 を返すことを確認
  - `.venv\Scripts\python.exe -m rm_trend_radar fetch --timeout 20` で実記事を取得し、128 件が `review_status=unreviewed` として保存されることを確認
  - 実記事取得後、`http://127.0.0.1:8502` が HTTP 200 を返すことを確認
  - `P4-06` 俯瞰テーブルと公開候補フラグの追加
  - `P4-07` 公開候補タブと Markdown/JSON preview の追加
  - `P4-09` タイトルベースの仮重要度と判定理由の追加
  - `.venv\Scripts\python.exe -m compileall src app.py` が通過することを確認
  - 判定語の部分一致による誤分類を避ける調整後、`.venv\Scripts\python.exe -m pytest tests\test_title_priority.py tests\test_digest.py tests\test_public_export.py tests\test_rss.py -p no:cacheprovider` が 16 passed になることを確認
  - `.venv\Scripts\python.exe` の手動 smoke で既存 schema に `title_priority` と `title_priority_reason` を追加し、既存記事の `title_en` から再計算できることを確認
  - `.venv\Scripts\python.exe` の手動 smoke で RSS 再取得時に手動確認項目を維持したまま、変更後の `title_en` から `title_priority` と `title_priority_reason` を再計算できることを確認
  - `streamlit.testing.v1.AppTest` で `app.py` が画面実行例外を出さないことを確認。終了時に Python tempfile cleanup の `PermissionError [WinError 5]` が出るが、AppTest 本体は `streamlit AppTest ok` で終了する。
  - `http://127.0.0.1:8502/` が HTTP 200 を返すことを確認
  - CDP `127.0.0.1:60904` 経由で `http://127.0.0.1:8502/` の DOM を確認し、`タイトル仮重要度`、`仮重要度`、`高候補`、`タイトル仮重要度の理由` が表示されることを確認
  - ローカル DB の実記事で `title_priority` を再計算し、件数が `high` 62、`medium` 66 になることを確認
  - `.venv\Scripts\python.exe -m pytest -p no:cacheprovider` は 18 passed, 9 errors。失敗理由は `C:\Users\n-kei\AppData\Local\Temp\pytest-of-n-kei` を pytest が列挙できない `PermissionError [WinError 5]` で、`tmp_path` を使う `tests\test_db.py` と `tests\test_fetch.py` の setup 前に停止する。
  - CDP `127.0.0.1:60904` 経由で `http://127.0.0.1:8502/` を確認し、俯瞰テーブル、公開候補タブ、Markdown/JSON 欄、公開候補 0 件の空状態が表示されることを確認
  - `.venv\Scripts\python.exe` の手動 smoke で既存 schema に `public_candidate` を追加できることを確認
  - `.venv\Scripts\python.exe` の手動 smoke で公開候補フラグを保存でき、RSS 再取得で公開候補フラグが上書きされないことを確認
  - `streamlit.testing.v1.AppTest` で `app.py` が画面実行例外を出さないことを確認
  - `.venv\Scripts\python.exe -m streamlit run app.py --server.headless=true --server.port=8504 --browser.gatherUsageStats=false` を一時起動し、`http://127.0.0.1:8504` が HTTP 200 を返すことを確認
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
  - タイトル仮重要度追加後の実サイト再取得
  - GitHub Actions などの CI 実行
  - `.venv\Scripts\python.exe -m pytest` の全件実行は、pytest が作成する一時ディレクトリを列挙できず `PermissionError [WinError 5]` で終了する。`tests\test_title_priority.py`、`tests\test_digest.py`、`tests\test_public_export.py`、`tests\test_rss.py` と手動 smoke で主要処理は確認済みだが、`tmp_path` を使う DB/fetch テストの pytest 実行完了は未確認。

## Open Questions

- AI 候補生成を行う場合、入力データを保存済みメタデータだけにするか、RSS `description` の一時利用まで広げるか。
- AI 出力を候補表示だけにするか、人間が確認して保存するか。
- 複業リポ側 LP に公開候補記事を載せる場合のドメインページ URL、見出し構成、掲載粒度、反映手順をどう定義するか。
- Cloudflare と独自ドメインを、紹介 LP の導線だけに使うか、将来のアプリ公開先として使うか。
