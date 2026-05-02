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

- [ ] `P2-01` 初期取得対象サイトを調査する
  Done条件: 3〜5 サイトについて、RSS の有無、公開ブログ一覧 URL、想定取得頻度、保存項目、注意点が文書化されている。
  依存: `P1-02`
  spec-impact: yes
  spec-checkpoint: before-impl
  target-spec: docs/spec_001_sources.md
  open-spec-questions: 初期対象を 3 件に絞るか、5 件まで広げるか。

- [ ] `P2-02` 記事取得スキーマを確定する
  Done条件: RSS または公開ブログ一覧ページから取り込む項目、重複判定、更新判定、取得失敗時の扱いが仕様化されている。
  依存: `P2-01`
  spec-impact: yes
  spec-checkpoint: before-impl
  target-spec: docs/spec_001_sources.md

## Remaining Task Triage

Now:
- `P2-01` 初期取得対象サイトを調査する

Next:
- `P2-02` 記事取得スキーマを確定する

After Next:
- AI 要約、タグ付け、重要度付け、週次ダイジェストの MVP 範囲を決める

Later:
- Cloudflare 連携、独自ドメイン導線、公開用認証を検討する。

## Next候補

1. `P2-01` 初期取得対象サイトを調査する
2. `P2-02` 記事取得スキーマを確定する
3. AI 要約、タグ付け、重要度付け、週次ダイジェストの MVP 範囲を決める
