# AGENTS.md

## Purpose

このリポジトリは、ホテル・レベニューマネジメント領域の海外公開記事を収集し、日本語で確認するための個人用 Web アプリを開発する。

アプリは、原文記事へのリンク、日本語タイトル、日本語要約、タグ、重要度、レベニューマネジメント担当者向けの示唆、手動メモを扱う。記事本文の全文保存、全文転載、原文の代替公開は目的にしない。

## Read Budget

- 初手で読むのは root `AGENTS.md` のみ。
- 追加読込は、タスク遂行に必要な最小数に限定する。
- 不足があれば推測せず、必要ファイルを特定して読む。

## Task Read

- 仕様変更や挙動確認: `docs/spec_*.md`
- 判断原則の確認: `docs/context/INTENT.md`
- 現在地の確認: `docs/context/STATUS.md`
- 判断理由の確認: `docs/context/DECISIONS.md`
- 実行順の確認: `docs/tasks_backlog.md`
- リポジトリ固有運用の確認: `Engineering Rules` と `Verification`

## Source Priority

1. セキュリティ、法令、著作権、公開制約
2. `docs/spec_*.md`
3. `docs/context/INTENT.md`
4. `docs/context/DECISIONS.md`
5. `docs/context/STATUS.md`
6. `docs/tasks_backlog.md`
7. `README.md`
8. 実装コード

同順位で矛盾した場合は、より新しい決定を優先する。未解決の判断は、`docs/context/DECISIONS.md` に `D-YYYYMMDD-xxx` 形式で暫定記録してから進める。

## Scope Rules

- MVP は個人利用のローカルアプリとして扱う。
- 初期構成は Python、Streamlit、SQLite とする。
- 収集対象は公開 RSS または公開ブログ一覧ページに限定する。
- 原文記事の全文保存、全文転載、ログインが必要なページの取得、robots.txt や利用規約に反する取得は行わない。
- 要約は原文確認の補助であり、原文を読まずに転載可能な本文として扱わない。
- 公開アプリ化、Cloudflare 連携、独自ドメイン連携、認証、定期実行は MVP 後の検討対象とする。

## Documentation Rules

- 現在地は `docs/context/STATUS.md` に置く。
- 固定判断は `docs/context/DECISIONS.md` に置く。
- 複数の仕様判断にまたがる判断原則は `docs/context/INTENT.md` に置く。
- 実行タスクは `docs/tasks_backlog.md` に置く。
- 外部挙動、入出力、保存データ、受け入れ条件は `docs/spec_*.md` に置く。
- 会話内容だけを正本にしない。正本化する場合は、対象文書を更新して確定する。

## Skill Rules

- Skill は task-specific procedure だけを持つ。repo-wide の常時ルールや設計原則は root `AGENTS.md` に置く。
- 依頼を実行または verify しようとして、未導入のツール、ライブラリ、Skill、preset が不足能力の原因になっている場合は、短く導入提案してよい。提案すべきか迷う場合は、提案を抑えるより、不足内容と候補を短く示す方を優先する。
- 新しい外部ツールや依存ライブラリを提案する前に、既存手段で代替できないか確認する。外部導入を候補に残す場合は、供給網、過剰権限、install script、version 固定の観点を確認する。
- 導入提案を見送られた場合は、少なくとも `not-now`、`policy-reject`、`security-reject`、`cost-reject` のいずれかで理由を整理する。`policy-reject` と `security-reject` は、明示的な再検討があるまで再提案しない。
- スレッド開始時と終了時には、thread/handoff 系 Skill の発火要否を必ず判断し、使う場合も使わない場合も理由を短く明示する。
- 本線タスクでは handoff prompt を入口の前提にせず、必要なら thread/handoff 系 Skill を使って正本確認、task bundle、subagent 利用、handoff 要否を判断する。
- task bundle は Task ID ごとに機械的に切らず、同じ仕様、名称、責務境界を共有する task 群を候補として把握し、実際にどこまで扱うかはスレッド開始時に確定する。
- 新しい CLI、サブコマンド、引数体系、出力契約を設計または変更するときは `create-cli` を使う。内部実装だけを変える場合は使わない。

## Obsidian SecondBrain Capture

### Purpose

この repo での Codex 作業のうち、次回以降も参照する価値がある情報は、Obsidian SecondBrain vault へ記録する。

Obsidian vault:

```text
C:\Users\n-kei\Documents\Obsidian\SecondBrain
```

### Source Of Truth

この repo の仕様、進捗、決定、タスクの正本は repo 内ドキュメントである。

Obsidian は、repo をまたいで検索、比較、再利用するための横断索引と、Codex の作業文脈を維持するための補助情報である。

repo 内正本と Obsidian が矛盾する場合は、repo 内正本を優先する。

### Capture Triggers

次の作業を行った場合、終了前に Obsidian への記録対象を判断する。

- 非自明な実装、調査、設計判断、docs handoff
- 次スレッドの再開地点が重要な作業
- repo をまたいで再利用できる判断、検証方法、失敗知識
- ユーザーの説明粒度、確認頻度、委任範囲に関する作業認識の更新
- `AGENTS.md`、Skill、handoff、automation、Obsidian vault 運用の変更

### Completion Checkpoint

次のいずれかを行った場合、最終回答の前に `capture-needed: yes | no` を明示的に判定する。

- 非自明な実装、調査、設計判断、docs 更新、handoff
- `AGENTS.md`、Skill、automation、Obsidian vault 運用の変更
- repo をまたいで再利用できる判断、検証方法、失敗知識の発見

`capture-needed: yes` の場合は、`second-brain-capture` Skill を使い、repo 内正本と Obsidian note の境界を分けて記録する。

`capture-needed: no` の場合は、保存しない理由を短く示す。例: 単発回答、repo 内正本に十分記録済み、再利用価値がない、秘密情報を含むため保存しない。

この判定を省略したまま、非自明な作業を完了扱いにしない。

### Capture Rules

- 新規作業記録は `00_Inbox/Codex Captures/` に作成する。
- note には `audience`、`update_mode`、`confidence` を入れる。
- `audience: codex` の note は、Codex が次回以降の作業文脈として使う。
- `audience: user` の note は、ユーザー本人が後で読む知識体系として扱う。
- `audience: shared` の note は、Codex とユーザーの両方が参照する運用ルールや判断基準として扱う。
- Codex 側の作業プロファイルは `update_mode: automatic` として自動更新してよい。
- 誤りが後続のやり取りで見つかった場合は、必要に応じて `Revision Notes` に修正理由を残す。

### Do Not Capture

- API key、Cookie、token、認証情報
- 不必要な個人情報
- 一時ログ全文
- repo 内正本と矛盾する未確認情報
- 人格評価、感情の断定、開発支援に不要な推測

### Skill

Obsidian capture を作成または更新する場合は、`second-brain-capture` Skill を使う。

## Engineering Rules

- 変更前に既存ファイルの責務を確認し、同じ情報を複数文書へ重複記載しない。
- データ取得、要約、タグ付け、画面表示、永続化は責務を分ける。
- 外部サイト取得を追加する場合は、対象サイト、取得方法、保存項目、取得頻度、停止条件を先に文書化する。
- Python 実行は `.venv\Scripts\python.exe` を優先する。
- Streamlit 起動は `.venv\Scripts\python.exe -m streamlit run app.py` を使う。

## Subagent Policy

- メインスレッド側は、全体判断、統合、最終 verify、最終報告を担う。
- subagent の既定は未使用とする。使うのは、対象範囲、返却形式、寿命を事前に固定できる bounded delegation の場合だけに限る。
- クリティカルパス、責務境界をまたぐ変更、高判断コスト変更、write-heavy な変更は、既定でメインスレッド側に残す。
- 委譲を優先するのは、調査、影響範囲確認、レビュー、テスト切り分け、要約、文書配置判断などの read-heavy な作業とする。
- 実装を委譲する場合は、対象ファイルまたは責務、write set、期待する返却形式を開始前に明示する。
- 同一ファイル、同一責務、共有設定、同一 verify 対象を複数の subagent に重ねて割り当てない。競合が見込まれる変更はメインスレッド側へ戻す。
- subagent による部分 verify や調査用テストは許容するが、最終 verify 判定はメインスレッド側だけが行う。
- 依存追加や更新、設定変更、migration、認証、秘密情報、権限、外部接続変更、正本文書への反映要否の最終判断は、メインスレッド側が保持する。

## Verification

- 実装変更後は、少なくとも次を確認する。
  - `.venv\Scripts\python.exe -m compileall src app.py`
  - `.venv\Scripts\python.exe -m pytest`（テストが存在する場合）
  - `.venv\Scripts\python.exe -m streamlit run app.py` で起動できること
