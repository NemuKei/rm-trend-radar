# BACKLOG

## Rules

- ID は `P<phase>-<連番>` を使う。
- 各タスクに Done 条件を書く。
- 依存関係がある場合は、どのタスク完了後に着手するかを明記する。
- `Next候補` は 1〜3 件に絞る。
- 実装候補 task には、必要に応じて次の metadata を付ける。
  - `spec-impact: yes | no | unknown`
  - `spec-checkpoint: before-impl | during-impl | not-needed`
  - `target-spec: path`
  - `open-spec-questions: ...`

## Phase 1: MVP の土台を作る

- [x] `P1-01` 新規リポジトリを作成する
  Done条件: `rm-trend-radar` のローカル git リポジトリが作成され、初期ファイルが配置されている。
  spec-impact: no
  spec-checkpoint: not-needed

- [x] `P1-02` Python と Streamlit の最小構成を作る
  Done条件: Streamlit アプリが SQLite のサンプル記事を読み込み、記事一覧を表示できる。
  依存: `P1-01`
  spec-impact: yes
  spec-checkpoint: before-impl
  target-spec: docs/spec_000_overview.md

- [x] `P1-03` GitHub private remote を作成する
  Done条件: GitHub 上に private repository が作成され、ローカル `origin` が設定されている。
  依存: `P1-01`
  spec-impact: no
  spec-checkpoint: not-needed

- [x] `P1-04` 次スレッド移行用の正本文書を整備する
  Done条件: `STATUS`、`tasks_backlog`、`spec_001_sources` が、次スレッドで `P2-01` から再開できる内容になっている。
  依存: `P1-03`
  spec-impact: yes
  spec-checkpoint: before-impl
  target-spec: docs/spec_001_sources.md

## Phase 2: 初期取得対象を決める

- [x] `P2-01` 初期取得対象サイトを調査する
  Done条件: 3〜5 サイトについて、RSS の有無、公開ブログ一覧 URL、想定取得頻度、保存項目、注意点が文書化されている。
  依存: `P1-02`
  spec-impact: yes
  spec-checkpoint: before-impl
  target-spec: docs/spec_001_sources.md
  結果: 初期対象は IDeaS、SiteMinder、RoomPriceGenie、Revfine、Hotel Speak の 5 件とする。Mews、Lighthouse、Hospitality Net は後回しにする。

- [x] `P2-02` 記事取得スキーマを確定する
  Done条件: RSS または公開ブログ一覧ページから取り込む項目、重複判定、更新判定、取得失敗時の扱いが仕様化されている。
  依存: `P2-01`
  spec-impact: yes
  spec-checkpoint: before-impl
  target-spec: docs/spec_001_sources.md

## Phase 3: RSS 取得を実装する

- [x] `P3-01` 初期対象 5 件の source config と RSS item parser を実装する
  Done条件: IDeaS、SiteMinder、RoomPriceGenie、Revfine、Hotel Speak の feed URL をコードから参照でき、RSS XML から `source_name`, `url`, `published_date`, `title_en`, `tags` を取り出す単体テストが存在する。
  依存: `P2-02`
  spec-impact: no
  spec-checkpoint: not-needed

- [x] `P3-02` RSS item を SQLite に upsert する
  Done条件: 正規化した原文 URL を一意キーとして新規記事を追加でき、既存記事の `title_ja`, `summary_ja`, `tags_json`, `importance`, `rm_implication`, `note` を RSS 再取得で上書きしないテストが存在する。
  依存: `P3-01`
  spec-impact: no
  spec-checkpoint: not-needed

- [x] `P3-03` 手動実行できる RSS 取得入口を追加する
  Done条件: `.venv\Scripts\python.exe -m rm_trend_radar fetch` のような手動コマンドで初期対象 5 件を取得でき、取得件数、追加件数、更新件数、失敗 source を確認できる。
  依存: `P3-02`
  spec-impact: yes
  spec-checkpoint: before-impl
  target-spec: docs/spec_001_sources.md
  結果: CLI は `python -m rm_trend_radar fetch` とし、`--source`, `--dry-run`, `--json`, `--timeout` を持つ。CLI 契約は `docs/spec_001_sources.md` に記録した。

## Phase 4: 記事確認ワークフローを実装する

- [x] `P4-01` 初期 MVP の AI 範囲と確認ワークフロー仕様を確定する
  Done条件: 初期 MVP では AI API を呼び出さず、取得済み記事を人間が確認する方針が `DECISIONS` と `spec_002_review_workflow` に記録されている。
  依存: `P3-03`
  spec-impact: yes
  spec-checkpoint: before-impl
  target-spec: docs/spec_002_review_workflow.md

- [x] `P4-02` 記事の確認状態と手動確認項目の保存処理を実装する
  Done条件: 既存 DB に `review_status` と `reviewed_at` を追加でき、画面から `title_ja`, `summary_ja`, `tags_json`, `importance`, `rm_implication`, `note`, `review_status` を保存できる。
  依存: `P4-01`
  spec-impact: yes
  spec-checkpoint: before-impl
  target-spec: docs/spec_002_review_workflow.md

- [x] `P4-03` 確認済み記事から週次ダイジェストを表示する
  Done条件: Streamlit 画面で、確認済み、対象期間内、重要度条件を満たす記事だけを使い、Markdown 形式の週次ダイジェストを表示できる。
  依存: `P4-02`
  spec-impact: yes
  spec-checkpoint: before-impl
  target-spec: docs/spec_002_review_workflow.md

- [ ] `P4-04` AI 候補生成の後続検討を行う
  Done条件: AI に渡す入力データ、保存する出力、保存しないデータ、候補表示と自動保存の違いが仕様化され、実装する場合のタスクが追加されている。
  依存: `P4-03`
  spec-impact: yes
  spec-checkpoint: before-impl
  target-spec: docs/spec_002_review_workflow.md

- [ ] `P4-05` 実記事を取得して確認ワークフローを画面評価する
  Done条件: 初期対象 5 件から実記事を取得し、記事確認タブと週次ダイジェストタブで、未確認記事の見え方、確認フォームの入力しやすさ、タグ表示、重要度条件、ダイジェスト Markdown の読みやすさを確認し、必要な調整タスクが backlog に追加されている。
  依存: `P4-03`
  spec-impact: unknown
  spec-checkpoint: during-impl
  target-spec: docs/spec_002_review_workflow.md
  備考: 現在の画面構成は暫定的に許容する。次の調整は、サンプル記事ではなく実記事を可視化してから判断する。2026-05-02 に初期対象 5 件から 128 件を取得し、実データ確認用にアプリ起動時のサンプル自動投入を停止した。次は画面上で記事確認タブと週次ダイジェストタブを確認する。

- [x] `P4-06` 俯瞰テーブルと公開候補フラグを追加する
  Done条件: 記事確認画面で、公開日、取得元、確認状態、重要度、公開候補、タイトル、タグを表形式で俯瞰でき、各記事に複業リポ側 LP の公開候補フラグを保存できる。
  依存: `P4-05`
  spec-impact: yes
  spec-checkpoint: before-impl
  target-spec: docs/spec_002_review_workflow.md

- [x] `P4-07` 複業リポ側 LP への公開候補 export 契約を決める
  Done条件: 公開候補記事を複業リポ側 LP に渡す場合の出力形式、出力項目、掲載前チェック、原文代替公開を避ける制約が仕様化され、公開候補タブで Markdown と JSON の preview を確認できる。
  依存: `P4-06`
  spec-impact: yes
  spec-checkpoint: before-impl
  target-spec: docs/spec_002_review_workflow.md

- [ ] `P4-08` 複業リポ側 LP のドメインページ構成を決める
  Done条件: 公開候補記事を掲載するドメインページの URL、見出し構成、掲載粒度、掲載前チェック、`rm-trend-radar` からの反映手順が仕様化されている。
  依存: `P4-07`
  spec-impact: yes
  spec-checkpoint: before-impl
  target-spec: docs/spec_002_review_workflow.md

- [x] `P4-09` タイトルベースの仮重要度を追加する
  Done条件: 記事タイトルから読む順番の候補を `high`, `medium`, `low` として保存し、記事確認画面の表、詳細、絞り込み条件で確認できる。人間が確定する `importance` は上書きしない。
  依存: `P4-05`
  spec-impact: yes
  spec-checkpoint: before-impl
  target-spec: docs/spec_002_review_workflow.md

- [x] `P4-10` 気になる記事チェックを追加する
  Done条件: 記事確認画面の一覧で、タイトルを見ながら気になる記事にチェックを入れて保存でき、気になる記事だけで絞り込める。気になるフラグは公開候補フラグとは別に保存する。
  依存: `P4-09`
  spec-impact: yes
  spec-checkpoint: before-impl
  target-spec: docs/spec_002_review_workflow.md

## Remaining Task Triage

Now:
- 実記事を取得して確認ワークフローを画面評価する。タイトル仮重要度を使い、先に読む記事候補を絞り込む。

Next:
- 複業リポ側 LP のドメインページ構成を決める
- AI 候補生成の後続検討を行う

After Next:
- Cloudflare 連携、独自ドメイン導線、公開用認証を検討する

Later:
- なし

## Next候補

1. 実記事に気になるフラグを付け、原文確認する候補を絞り込む
2. 複業リポ側 LP のドメインページ構成を決める
3. AI 候補生成の後続検討を行う
