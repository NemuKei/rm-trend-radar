# STATUS

Last Updated: 2026-05-14

## Current Task Bundle

- 主対象: 最新記事取得と副業リポ側 LP の短い記事一覧データ更新を自動化する
- この bundle で扱う範囲:
  - GitHub Actions で、取得対象 5 件の RSS メタデータを 3 日に 1 回程度で取得する
  - Codex アプリ automation で、翻訳、短い紹介文作成、公開カテゴリ付与、副業リポ側 LP 反映、検証レポートを実行する
- この bundle で扱わないこと:
  - AI API 実装そのもの
  - AI 候補生成の仕様確定
  - 記事本文全文の保存
  - 原文記事の構成を再現する長文要約の自動公開
  - 詳細な重要度、示唆、個別解説ページの自動確定
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
- 実記事一覧はカード表示では俯瞰しづらいため、`P4-06` で記事確認画面を表形式の俯瞰テーブルに変更し、副業リポ側 LP の公開候補フラグを追加した。
- 今後の方向性として、`rm-trend-radar` は非公開の収集、確認、編集、選別用リポジトリとし、副業リポ側 LP は確認済みで公開してよい内容だけを掲載する公開面として扱う。
- `P4-07` で、公開候補タブを追加した。対象は確認済みかつ公開候補の記事だけで、Markdown と JSON の preview を表示する。手動メモは export preview に含めない。
- `P4-09` で、記事タイトルだけから読む順番の候補を `high`, `medium`, `low` として保存する `title_priority` と、判定理由を保存する `title_priority_reason` を追加した。これは人間が確定する `importance` とは別項目であり、公開候補選定や週次ダイジェスト掲載の確定条件には使わない。
- ローカル DB の実記事 128 件を `title_priority` で再計算した結果は、`high` 62 件、`medium` 66 件、`low` 0 件である。これはタイトルだけに基づく仮分類であり、記事内容確認後の `importance` とは別に扱う。
- `P4-10` で、記事確認画面の一覧に `気になる` チェックを追加した。これは原文確認前に気になった記事を残す内部フラグであり、確認済み状態、重要度、公開候補とは別に扱う。
- 2026-05-03 時点で、利用者が気になる記事 42 件にチェックを入れた。そのうち `title_priority = high` の新しい順から 7 件を Codex が原文確認し、日本語要約、タグ、重要度、レベニューマネジメント担当者向けの示唆をローカル DB に下書き保存した。確認済み 7 件、気になる確認済み 7 件、公開候補 0 件である。
- `P4-11` で、確認済み記事だけを対象に、要約、レベニューマネジメント担当者向けの示唆、原文 URL、公開候補フラグを確認できる `確認済みレビュー` タブを追加した。
- 2026-05-03 時点で、確認済み 7 件の日本語要約とレベニューマネジメント担当者向けの示唆を、内部確認用に増量した。`summary_ja` はおおむね 246 から 270 文字、`rm_implication` はおおむね 156 から 184 文字である。これは原文の代替公開用本文ではなく、確認済みレビュー画面で内容を見極めるための下書きである。
- `P4-12` で、今後の確認済み記事に適用する要約レベルを `docs/spec_002_review_workflow.md` に仕様化した。`summary_ja` は原則 250 から 350 文字程度、`rm_implication` は原則 150 から 250 文字程度とし、どちらも公開 LP や X にそのまま掲載する文章ではなく、内部確認用テキストとして扱う。
- `P4-13` で、自分用の詳細要約または読解メモを保存する `personal_summary` を追加した。これは公開候補 export preview、週次ダイジェスト、副業リポ側 LP、X 投稿には含めない内部項目である。記事確認画面と確認済みレビュー画面から編集できる。
- `P4-14` で、ChatGPT Pro の出力を公開用途別に仕訳するための公開用コンテンツ項目を追加した。`public_tip_ja`, `sns_post_draft`, `newsletter_lead_draft`, `internal_share_summary`, `manager_checklist`, `source_credit` を保存できる。これらは公開候補 export preview に含め、`personal_summary` と `note` は引き続き含めない。
- 2026-05-03 時点のローカル DB では、確認済み 7 件、気になる確認済み 7 件、公開候補 1 件である。公開候補は `ホテルは直前料金を大幅に下げずに競争力を保てるのか` である。
- 2026-05-03 時点で、公開候補記事 `ホテルは直前料金を大幅に下げずに競争力を保てるのか` に ChatGPT Pro 出力を仕訳して保存した。元記事の読解メモは `personal_summary` に保存し、公開用本文、SNS 投稿案、メルマガ用リード文、社内共有用 3 行要約、支配人・現場向けチェックリスト、出典表記は、それぞれ公開用コンテンツ項目に保存した。
- 公開 LP と X は、記事の短い紹介、独自の示唆、原文リンクを届ける導線として扱う。詳細な内容理解は、原文サイトを開いてブラウザ翻訳も使いながら確認してもらう方針にする。
- `P4-08` で、副業リポ側 LP の初期掲載契約を `docs/spec_002_review_workflow.md` に追加した。初期掲載は、既存 LP 内の `overseas-rm-articles` セクションとして追加し、日本語タイトル、短い要約、取得元、公開日、原文リンクだけの一覧に限定する。`public_tip_ja` などの長い公開用コンテンツは、初期一覧には使わず、個別解説ページを作る場合の後続材料として扱う。
- 2026-05-04 時点で、気になるチェック済み 42 件すべてを公開 LP 一覧用の短い紹介にそろえた。原文ページの title と meta description を確認し、`summary_ja` を原文代替にならない短い紹介文へ更新した。42 件すべてが `review_status=confirmed`, `interest_candidate=True`, `public_candidate=True` である。
- 2026-05-04 に、LP 候補外だった記事から、レベニュー管理より現場サービスに近い記事 6 件を追加で公開候補にした。対象は、ゲスト体験、レセプション判断、フロントオフィス業務、従業員エンゲージメント、顧客関係管理、レピュテーション管理である。公開候補 export 対象は 48 件になり、追加 6 件の `public_category` は `organization_process` である。
- `P4-16` で、副業リポ側 LP に掲載する海外 RM サイト紹介セクションを `docs/spec_002_review_workflow.md` に仕様化した。初期対象は `IDeaS`, `SiteMinder`, `RoomPriceGenie`, `Revfine`, `Hotel Speak` の 5 件で、各サイトの短い紹介、主な確認テーマ、公式サイトまたは記事一覧へのリンクを表示する。
- IDeaS の live dry-run では `fetched=10`, `added=0`, `updated=0`, `unchanged=0`, `failed=0` を確認した。
- `.venv\Scripts\python.exe` は、`pyvenv.cfg` の参照先を現在の端末で利用できる Python 3.12.13 に合わせて復旧済み。`.venv` は git 管理外のため、この復旧内容はリポジトリ差分には含めない。
- 2026-05-04 に、次段階の自動化は記事取得だけに限定する方針を決めた。RSS の定期取得は追加してよいが、日本語化、重要度確定、公開候補フラグ付け、副業リポ側 LP への反映、X 投稿は自動化しない方針だった。この判断は 2026-05-11 の `D-20260511-014` で改定済みである。
- `P5-01` で、`scripts/Invoke-ScheduledFetch.ps1` と `scripts/Register-ScheduledFetch.ps1` を追加した。ローカル Windows で 1 日 1 回以下の頻度で既存の `fetch` CLI を呼び出し、SQLite への RSS item upsert だけを行う。実行ログは `logs/scheduled-fetch-YYYYMMDD.jsonl` に保存する。
- 2026-05-04 に、定期取得の主経路を GitHub Actions へ変更した。当時は private repository のまま `.github/workflows/fetch-rss-snapshot.yml` で毎日 23:00 UTC、日本時間 08:00 に RSS snapshot artifact を作り、GitHub Actions では SQLite、公開候補フラグ、副業リポ側 LP のファイルを更新しない方針だった。この頻度と LP 反映範囲は 2026-05-11 に改定済みである。
- `P5-02` で、`fetch-snapshot` CLI と `.github/workflows/fetch-rss-snapshot.yml` を追加した。出力は `artifacts/rss_snapshot.json` で、GitHub Actions の `rss-snapshot` artifact として 14 日保存する。出力 JSON は `lp_ready = false`、`publish_decision = manual_review_required` を持つ確認用データであり、LP 側の直接入力ではない。
- 初回手動実行 `Fetch RSS Snapshot #1` は、IDeaS 10 件、SiteMinder 50 件、RoomPriceGenie 40 件、Revfine 18 件を取得できたが、Hotel Speak だけ失敗したため exit 3 で失敗した。artifact upload 前に停止したため、GitHub Actions では `--allow-partial` を使い、少なくとも 1 source が成功した場合は失敗 source を JSON に記録した上で artifact を残す方針に修正した。
- Windows タスクスケジューラに登録していた `RM Trend Radar RSS Fetch` は、GitHub Actions へ寄せるため削除済み。ローカル script は手元で再登録したい場合の任意手段として残す。
- 2026-05-04 に、公開 LP 用の単一カテゴリ `public_category` を RTR 側の確認項目として追加した。公開候補 export preview には `public_category` と `public_category_label` を含める。既存の公開候補 42 件は、LP 側の 6 カテゴリへ分類済みである。
- 2026-05-11 に、次段階の自動化方針を変更した。最新記事取得から副業リポ側 LP の短い記事一覧データ更新までを自動化してよい。実行頻度は 3 日に 1 回程度を初期値にする。自動更新で公開 LP に出してよい項目は、日本語タイトル、原文記事の代替にならない短い紹介、取得元、公開日、原文 URL、公開カテゴリに限定する。
- 2026-05-11 に、`.github/workflows/fetch-rss-snapshot.yml` の schedule を毎日 08:00 JST 相当から、3 日に 1 回程度の 14:37 JST 相当に変更した。14:37 は、PC を開いていない朝 8 時を避け、他の自動化と競合しにくいように正時ではない時刻として選んだ。GitHub Actions の cron では月末から月初にかけて厳密な 72 時間周期にならない場合があるため、仕様では「3 日に 1 回程度」として扱う。
- 2026-05-11 に、副業リポ側 LP の日本語タイトル一覧は、カテゴリごとに初期表示件数を制限し、一定件数を超える場合は折りたたみまたは追加表示で確認する方針にした。
- 2026-05-11 に、取得済みで副業リポ側 LP にまだ載っていない記事のうち、`title_priority=high` で LP 読者に有用なものを 12 件追加反映した。追加記事は、短い `summary_ja`、`public_category`、`importance=4`、`review_status=confirmed`、`public_candidate=1` を保存済みである。
- 2026-05-11 に、SideBiz 側の `02_Service/web_lp/scripts/refresh_overseas_rm_articles.py` を使って LP 用データを再生成した。副業リポ側 LP の公開候補記事は 48 件から 60 件になった。カテゴリ別件数は、料金設定・価格最適化 10、需要予測・稼働・宿泊制限 10、収益指標・オーナー視点 10、AI・検索・予約行動 10、Distribution・OTA・直販 6、組織・業務プロセス 14 である。
- 2026-05-11 に、SideBiz 側の日本語タイトル一覧を、カテゴリごとに先頭 8 件だけ初期表示し、超過分を `さらにN件を表示` で展開する構成にした。60 件反映後は 5 カテゴリで折りたたみが生成され、超過件数は 2、2、2、2、6 件である。
- 2026-05-11 に、Codex アプリ automation `rm-trend-radar-lp-reflection` を作成した。実行頻度は 3 日に 1 回程度、15:10 JST である。GitHub Actions は RSS メタデータ取得だけを担当し、Codex automation は翻訳、短い紹介文作成、公開カテゴリ付与、副業リポ側 LP 反映、検証レポートを担当する。検証が通過した場合は、変更がある repository ごとに commit し、現在の追跡先 branch へ push する。
- 2026-05-11 に、Codex automation `rm-trend-radar-lp-reflection` の初回実行で、副業リポ側 LP の短い記事一覧データを更新した。
  - 新規に公開候補へ追加した記事数: 5
  - 副業リポ側 LP の公開候補記事数: 60 → 65
  - カテゴリ別件数:
    - 料金設定・価格最適化: 10 → 12
    - 需要予測・稼働・宿泊制限: 10（変更なし）
    - 収益指標・オーナー視点: 10（変更なし）
    - AI・検索・予約行動: 10 → 11
    - Distribution・OTA・直販: 6（変更なし）
    - 組織・業務プロセス: 14 → 16
  - 追加した 5 件:
    - 2026-05-07 RoomPriceGenie: https://roompricegenie.com/resort-hotel-seasonal-pricing-strategy/
    - 2026-05-07 RoomPriceGenie: https://roompricegenie.com/hotel-pricing-strategy-planner/
    - 2026-05-07 RoomPriceGenie: https://roompricegenie.com/casablanca-hotelsoftware-roompricegenie-integration/
    - 2026-04-20 Revfine: https://www.revfine.com/pms-integration/
    - 2026-03-25 Revfine: https://www.revfine.com/choose-to-be-chosen-how-hoteliers-use-ai-to-stay-ahead-of-hospitality-trends/
  - LP 用 JSON の公開項目制限:
    - `SideBiz_HotelRM/02_Service/web_lp/data/overseas_rm_articles.json` の `articles` は、`public_category`, `public_category_label`, `title_ja`, `summary_ja`, `source_name`, `published_date`, `url` の 7 項目だけであることを確認した。
  - 検証結果:
    - `rm-trend-radar`: `.venv\Scripts\python.exe -m compileall src app.py` 通過
    - `rm-trend-radar`: `.venv\Scripts\python.exe -m pytest tests -p no:cacheprovider` が 30 passed
- `SideBiz_HotelRM`: `refresh_overseas_rm_articles.py` の `py_compile` 通過
- `SideBiz_HotelRM`: HTML の生成ブロックが 65 記事で生成されることを確認
- 2026-05-13 の GitHub Actions `Fetch RSS Snapshot` は成功し、128 件の RSS メタデータを取得した。`rm_trend_radar.db` の `review_status=confirmed` かつ `public_candidate=1` の 65 件は、SideBiz 側 `overseas_rm_articles.json` の 65 件と引き続き一致したため、今回の LP 再生成は不要だった。

## Next Re-entry

次スレッドは、次回の GitHub Actions RSS snapshot 実行後に、未反映記事のうち公開候補にしてよい記事を最大 5 件まで追加し、同じ手順で LP 用データ更新を行う。

### Thread Contract

- 今回の種別: `mainline-task`
- 主対象: Codex automation による翻訳から副業リポ側 LP 反映までの自動化を運用確認する
- bundle に含める Task ID: `P5-06`
- 最初に読む正本:
  - `AGENTS.md`
  - `docs/context/STATUS.md`
  - `docs/tasks_backlog.md`
  - `docs/spec_001_sources.md`
  - `docs/spec_002_review_workflow.md`
  - `docs/context/DECISIONS.md`
- 次スレッドで最初にやること:
  1. `docs/context/INTENT.md` の判断原則を確認する。
  2. `docs/spec_002_review_workflow.md` の `Public Candidate Policy`、公開カテゴリ定義、`Side Business LP Initial Listing Contract` を確認する。
  3. `docs/spec_001_sources.md` の `GitHub Actions Scheduled Snapshot` と `Codex App LP Reflection Automation` を確認する。
  4. Codex automation `rm-trend-radar-lp-reflection` の初回実行結果を確認する。
  5. 追加/更新記事数、保留記事、カテゴリ別件数、SideBiz 側変更ファイル、commit hash、push 先 branch を確認する。
  6. LP 用 JSON に、`public_category`, `public_category_label`, `title_ja`, `summary_ja`, `source_name`, `published_date`, `url` 以外の項目が含まれないことを確認する。
- この bundle で変更しない契約:
  - 記事本文全文を保存しない。
  - 記事本文全文を転載しない。
  - ログインが必要なページ、有料記事、会員限定記事を取得対象にしない。
  - 記事本文全文を LP 側へ渡さない。
  - 原文記事の構成を再現する長文要約を自動公開しない。
  - 詳細な重要度、示唆、個別解説ページを自動確定しない。
  - Cloudflare、独自ドメイン、認証は初期 MVP の前提にしない。
  - AI API 実装は、入力データ、保存する出力、保存しないデータを文書化してから始める。
- 終了条件:
  - GitHub Actions が 3 日に 1 回程度で RSS snapshot を作る。
  - Codex automation が 3 日に 1 回程度、15:10 JST に実行される。
  - 副業リポ側 LP の記事一覧データが、`public_category`, `public_category_label`, `title_ja`, `summary_ja`, `source_name`, `published_date`, `url` だけで更新される。
  - LP 自動更新対象に、自分用要約、手動メモ、原文記事の代替になる長文が含まれていない。
  - 検証が通過した場合は、変更がある repository ごとに commit / push され、commit hash と push 先 branch が報告される。
- subagent 利用方針:
  - 委譲してよい作業: LP データ更新先の調査、既存 LP 表示構造の確認、日本語タイトル一覧の表示制限実装。
  - 委譲してはいけない作業: 仕様確定前の AI API 実装、記事本文全文保存、長文解説の自動公開、X 投稿またはメルマガ送信。
  - メインスレッドが担う作業: 自動化範囲の最終判断、正本 docs の同期、検証結果の確認。

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
  - `P4-10` 気になる記事チェックの追加
  - `.venv\Scripts\python.exe -m compileall src app.py` が通過することを確認
  - `.venv\Scripts\python.exe -m pytest tests\test_title_priority.py tests\test_digest.py tests\test_public_export.py tests\test_rss.py -p no:cacheprovider` が 16 passed になることを確認
  - `.venv\Scripts\python.exe` の手動 smoke で既存 schema に `interest_candidate` を追加できることを確認
  - `.venv\Scripts\python.exe` の手動 smoke で気になるフラグを保存でき、RSS 再取得で気になるフラグが上書きされないことを確認
  - `streamlit.testing.v1.AppTest` で `app.py` が画面実行例外を出さないことを確認。終了時に Python tempfile cleanup の `PermissionError [WinError 5]` が出るが、AppTest 本体は `streamlit AppTest ok` で終了する。
  - `http://127.0.0.1:8502/` が HTTP 200 を返すことを確認
  - CDP `127.0.0.1:60904` 経由で `http://127.0.0.1:8502/` の DOM を確認し、`気になる`、`気になるを保存`、`気になるのみ`、`詳細表示する記事` が表示されることを確認
  - `P4-11` 確認済みレビュー画面の追加
  - `.venv\Scripts\python.exe -m compileall src app.py` が通過することを確認
  - `.venv\Scripts\python.exe -m pytest tests\test_title_priority.py tests\test_digest.py tests\test_public_export.py tests\test_rss.py -p no:cacheprovider` が 16 passed になることを確認
  - `streamlit.testing.v1.AppTest` で `app.py` が画面実行例外を出さないことを確認。終了時に Python tempfile cleanup の `PermissionError [WinError 5]` が出るが、AppTest 本体は `streamlit AppTest ok` で終了する。
  - `http://127.0.0.1:8502/` が HTTP 200 を返すことを確認
  - Browser Use で `確認済みレビュー` タブを開き、表示件数 7、重要度5 が 5、公開候補 0、気になる 7、要約、RM担当者向けの示唆、公開導線の確認が表示されることを確認
  - `.venv\Scripts\python.exe` の手動確認で、確認済み 7 件の増量後の文字数が `summary_ja` 246 から 270 文字、`rm_implication` 156 から 184 文字であることを確認
  - Browser Use で `確認済みレビュー` タブを再読み込みし、増量後の日本語要約とレベニューマネジメント担当者向けの示唆が画面上で読めることを確認
  - `P4-12` 確認済み記事の要約レベル仕様の追加
  - `docs/spec_002_review_workflow.md` に、`summary_ja` と `rm_implication` の目的、文字数目安、含める内容、含めない内容が記録されていることを確認
  - `P4-13` 自分用要約フォームの追加
  - `.venv\Scripts\python.exe` の手動 smoke で既存 schema に `personal_summary` を追加できることを確認
  - `.venv\Scripts\python.exe` の手動 smoke で `personal_summary` を保存でき、RSS 再取得で上書きされないことを確認
  - `.venv\Scripts\python.exe -m pytest tests\test_db.py tests\test_public_export.py -p no:cacheprovider --basetemp=.pytest_basetemp_p4_13_elevated` が 12 passed になることを確認。通常権限では一時ディレクトリの列挙で `PermissionError [WinError 5]` が出るため、権限昇格で実行した。
  - Browser Use で `http://127.0.0.1:8502/` を開き、記事確認画面と確認済みレビュー画面の編集フォームに `自分用要約` 欄が表示されることを確認
  - `P4-14` ChatGPT 出力の公開用仕訳項目の追加
  - `.venv\Scripts\python.exe` の手動 smoke で既存 schema に公開用コンテンツ項目を追加できることを確認
  - `.venv\Scripts\python.exe` の手動 smoke で公開用コンテンツを保存でき、RSS 再取得で上書きされないことを確認
  - `.venv\Scripts\python.exe -m pytest tests\test_db.py tests\test_public_export.py -p no:cacheprovider --basetemp=.pytest_basetemp_p4_14_elevated` が 12 passed になることを確認
  - Browser Use で `http://127.0.0.1:8502/` を開き、記事確認画面と確認済みレビュー画面の編集フォームに `出典表記`, `日本施設向けTips`, `SNS投稿案`, `メルマガ用リード文`, `社内共有用3行要約`, `支配人・現場向けチェックリスト` が表示されることを確認
  - `.venv\Scripts\python.exe` の手動確認で、article id 123 の `personal_summary`, `public_tip_ja`, `sns_post_draft`, `newsletter_lead_draft`, `internal_share_summary`, `manager_checklist`, `source_credit` が非空で、`review_status=confirmed`, `interest_candidate=True`, `public_candidate=True` であることを確認
  - Browser Use で `http://localhost:8502/` の `公開候補` タブを開き、対象記事のタイトル、公開用本文、SNS 投稿案、メルマガ用リード文、社内共有用 3 行要約、支配人・現場向けチェックリストが表示されることを確認
  - `P4-14` 実装直後に CDP `127.0.0.1:60904` 経由で `http://127.0.0.1:8502/` を確認し、俯瞰テーブル、公開候補タブ、Markdown/JSON 欄、公開候補 0 件の空状態が表示されることを確認。この後、2026-05-03 の記事仕訳で公開候補は 1 件になった。
  - `P4-08` 副業リポ側 LP の初期掲載契約を `docs/spec_002_review_workflow.md` に追加し、`docs/context/DECISIONS.md` と `docs/tasks_backlog.md` を同期した。
  - `.venv\Scripts\python.exe` の権限付き手動確認で、気になる未確認 35 件の原文ページ title と meta description を取得できることを確認した。
  - `.venv\Scripts\python.exe` の手動確認で、気になるチェック済み 42 件すべてが `review_status=confirmed`, `interest_candidate=True`, `public_candidate=True` になり、公開候補 export 対象が 42 件になったことを確認した。
  - `P4-16` 副業リポ側 LP の海外 RM サイト紹介セクションを `docs/spec_002_review_workflow.md` に追加し、`docs/context/DECISIONS.md` と `docs/tasks_backlog.md` を同期した。
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
  - `scripts\Invoke-ScheduledFetch.ps1` と `scripts\Register-ScheduledFetch.ps1` が PowerShell parser error を出さないことを確認
  - `scripts\Register-ScheduledFetch.ps1 -At "08:00" -WhatIf` が、タスク登録内容を表示し、実登録せず exit 0 になることを確認
  - `scripts\Invoke-ScheduledFetch.ps1 -Source unknown -DryRun -LogDirectory .tmp_scheduled_fetch_logs` が、既存 CLI の未知 source を exit 1 として返し、JSONL log に `stderr: ["Unknown source: unknown"]` を保存することを確認
  - `.venv\Scripts\python.exe -m compileall src app.py` が通過することを確認
  - `.venv\Scripts\python.exe -m pytest tests\test_rss.py tests\test_public_export.py tests\test_title_priority.py -p no:cacheprovider` が 14 passed になることを確認
  - `scripts\Register-ScheduledFetch.ps1 -At "08:00"` で Windows タスク `RM Trend Radar RSS Fetch` の登録に成功したことを確認
  - `schtasks.exe /Query /TN "RM Trend Radar RSS Fetch" /FO LIST /V` で、状態が `Ready`、次回実行が 2026-05-05 08:00、実行コマンドが `Invoke-ScheduledFetch.ps1 -TimeoutSeconds 20` であることを確認
  - `fetch-snapshot` CLI が RSS メタデータだけを JSON artifact 用 payload に変換し、`lp_ready = false` と `publish_decision = manual_review_required` を含める実装になっていることを確認
  - `.github/workflows/fetch-rss-snapshot.yml` が `schedule` と `workflow_dispatch` で実行され、`contents: read` 権限だけで `rss-snapshot` artifact を作る構成になっていることを確認
  - `schtasks.exe /Delete /TN "RM Trend Radar RSS Fetch" /F` でローカル Windows タスクを削除したことを確認
  - `.venv\Scripts\python.exe -m compileall src app.py` が通過することを確認
  - `.venv\Scripts\python.exe -m pytest tests\test_rss.py tests\test_snapshot.py tests\test_public_export.py tests\test_title_priority.py -p no:cacheprovider` が 15 passed になることを確認
  - `.venv\Scripts\python.exe -m rm_trend_radar fetch-snapshot --source unknown --output artifacts\test_unknown.json` が exit 1 で未知 source を stderr 表示することを確認
  - ネットワーク許可後、`.venv\Scripts\python.exe -m rm_trend_radar fetch-snapshot --source IDeaS --output artifacts\rss_snapshot_smoke.json --timeout 20` が exit 0 で `source=IDeaS fetched=10 failed=0` を表示することを確認
  - `artifacts\rss_snapshot_smoke.json` に `lp_ready=false`, `publish_decision=manual_review_required`, `review_status=unreviewed`, `public_candidate=false` が含まれ、RSS `description` と日本語要約が含まれないことを確認
  - GitHub plugin で run `25300119228` の job log を取得し、失敗原因が `Hotel Speak fetched=0 failed=1` による `exit code 3` であることを確認
  - GitHub plugin で run `25300296439` の job `74165950407` を確認し、`Fetch RSS metadata snapshot` と `Upload RSS snapshot` を含む全 step が success であることを確認
  - GitHub plugin で run `25300296439` の artifact `rss-snapshot` を確認した。artifact id は `6776443565`、size は 8118 bytes、expires_at は 2026-05-18T03:59:06Z である。
  - artifact 内の `rss_snapshot.json` を確認し、IDeaS 10 件、SiteMinder 50 件、RoomPriceGenie 40 件、Revfine 18 件、Hotel Speak 10 件が `failed=0` で取得されていることを確認
  - artifact 内の `rss_snapshot.json` に `lp_ready=false`, `publish_decision=manual_review_required`, `review_status=unreviewed`, `public_candidate=false` が含まれ、`summary_ja`, `description`, `personal_summary`, `note`, `public_tip_ja` が含まれないことを確認
  - `P4-17` で `public_category` を DB に追加し、記事確認画面、確認済みレビュー画面、公開候補 export preview に反映した
  - 既存の公開候補 42 件すべてに、LP 側の 6 カテゴリに対応する `public_category` を保存した
  - `.venv\Scripts\python.exe -m compileall src app.py` が通過することを確認
  - `.venv\Scripts\python.exe -m pytest tests\test_db.py tests\test_public_export.py -p no:cacheprovider --basetemp=.tmp_public_category_tests_elevated` が 12 passed になることを確認
  - `.venv\Scripts\python.exe -m streamlit run app.py --server.headless=true --server.port=8505 --browser.gatherUsageStats=false` を一時起動し、`http://127.0.0.1:8505` が HTTP 200 を返すことを確認
  - LP 候補外から現場サービス寄りの記事 6 件を追加で確認済み公開候補にし、公開候補 export 対象が 48 件、未分類カテゴリが 0 件であることを確認
  - `P4-18` で、未掲載かつ `title_priority=high` の記事から 12 件を追加で確認済み公開候補にしたことを確認
  - `P4-18` 反映後の公開候補 export 対象が 60 件、カテゴリ別件数が 10、10、10、10、6、14 件であることを確認
  - `P5-05` で、SideBiz 側の日本語タイトル一覧がカテゴリごとに先頭 8 件を初期表示し、超過分を `さらにN件を表示` で展開できる構造になったことを確認
  - 2026-05-11 の最終確認で、`.venv\Scripts\python.exe -m compileall src app.py` が通過することを確認
  - 2026-05-11 の最終確認で、`.venv\Scripts\python.exe -m pytest tests -p no:cacheprovider --basetemp=.tmp_pytest_final_20260511_tests` が 30 passed になることを確認
  - 2026-05-11 の最終確認で、`git diff --check` が whitespace error なしで終了することを確認。警告は Git の改行コード変換予定のみである。
- 未確認:
  - タイトル仮重要度追加後の実サイト再取得
  - `.venv\Scripts\python.exe -m pytest` のリポジトリ全体探索は、リポジトリ直下の一時ディレクトリ `tmpiws6w9_m` を pytest が収集しようとして `PermissionError [WinError 5]` で終了する。`tests` ディレクトリを明示した実行では 30 passed を確認済みである。

## Open Questions

- AI 候補生成を行う場合、入力データを保存済みメタデータだけにするか、RSS `description` の一時利用まで広げるか。
- AI 出力を候補表示だけにするか、人間が確認して保存するか。
- 副業リポ側 LP の初期一覧実装後、個別解説ページを作るか、一覧だけを維持するか。
- Cloudflare と独自ドメインを、紹介 LP の導線だけに使うか、将来のアプリ公開先として使うか。
