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
## Purpose

この repo での Codex 作業のうち、次回以降も参照する価値がある情報は、Obsidian SecondBrain vault へ記録する。

Obsidian vault:

```text
Windows canonical vault: C:\Users\n-kei\Documents\Obsidian\SecondBrain
WSL access path: /mnt/c/Users/n-kei/Documents/Obsidian/SecondBrain
```

## Source Of Truth

この repo の仕様、進捗、決定、タスクの正本は repo 内ドキュメントである。

Obsidian は、repo をまたいで検索、比較、再利用するための横断索引と、Codex の作業文脈を維持するための補助情報である。

repo 内正本と Obsidian が矛盾する場合は、repo 内正本を優先する。

## Capture Triggers

次の作業を行った場合、終了前に Obsidian への記録対象を判断する。

- 非自明な実装、調査、設計判断、docs handoff
- 次スレッドの再開地点が重要な作業
- repo をまたいで再利用できる判断、検証方法、失敗知識
- ユーザーの説明粒度、確認頻度、委任範囲に関する作業認識の更新
- AGENTS.md、Skill、handoff、automation、Obsidian vault 運用の変更
- ユーザー向けに噛み砕いて残す価値がある論文、外部知識、開発概念、専門用語
- 今後の開発判断に使えそうな補助メモ

## Completion Checkpoint

次のいずれかを行った場合、最終回答の前に `capture-needed: yes | no` を明示的に判定する。

- 非自明な実装、調査、設計判断、docs 更新、handoff
- AGENTS.md、Skill、automation、Obsidian vault 運用の変更
- 論文、外部知識、開発概念、専門用語に関する整理
- repo をまたいで再利用できる判断、検証方法、失敗知識の発見

`capture-needed: yes` の場合は、`second-brain-capture` Skill を使い、repo 内正本と Obsidian note の境界を分けて記録する。

`capture-needed: no` の場合は、保存しない理由を短く示す。例: 単発回答、repo 内正本に十分記録済み、再利用価値がない、秘密情報を含むため保存しない。

この判定を省略したまま、非自明な作業を完了扱いにしない。

## Capture Rules

- 新規作業記録は `00_Inbox/Codex Captures/` に作成する。
- note には `audience`、`update_mode`、`confidence` を入れる。
- `audience: codex` の note は、Codex が次回以降の作業文脈として使う。
- `audience: user` の note は、ユーザー本人が後で読む知識体系として扱う。
- `audience: shared` の note は、Codex とユーザーの両方が参照する運用ルールや判断基準として扱う。
- Codex 側の作業プロファイルは `update_mode: automatic` として自動更新してよい。
- 誤りが後続のやり取りで見つかった場合は、必要に応じて `Revision Notes` に修正理由を残す。
- ユーザー向け知識 note は日本語で噛み砕き、英語の正式名称、略語、検索語、論文タイトル、API 名、ライブラリ名は保持する。
- 専門用語、略語、モデル名、評価指標、データ概念、設計概念、業務概念は glossary note または candidate queue へ接続する。
- ユーザー向け note に書くと冗長だが今後の開発に応用できる補助メモは、Codex Application Memos へ分ける。
- Glossary note と論文 note は、Obsidian Bases の一覧に出るように必要な frontmatter property を埋める。
- 未確認、出典確認、開発応用の棚卸しは Knowledge Dashboard と review 系 Base から辿れるようにする。

## Do Not Capture

- API key、Cookie、token、認証情報
- 不必要な個人情報
- 一時ログ全文
- repo 内正本と矛盾する未確認情報
- 人格評価、感情の断定、開発支援に不要な推測

## Skill

Obsidian capture を作成または更新する場合は、`second-brain-capture` Skill を使う。

## Subagent Orchestration

SecondBrain 更新が非自明な場合は、subagent 利用を標準候補にする。

メインスレッドが担うこと:

- 保存先、`audience`、`update_mode`、`confidence` の最終判断
- repo 内正本と Obsidian note の境界判断
- subagent 結果の統合
- 最終差分、verify、commit、最終報告

subagent に委譲してよいこと:

- 既存 note の探索
- 関連 glossary 候補の抽出
- 論文や外部資料の source、DOI、Open Access 状態の確認
- ユーザー向け説明と Codex 向けメモの分離案作成
- frontmatter、wikilink、秘密情報、repo 正本混同のレビュー

同じファイルを複数 agent が同時に編集する作業、repo 正本か Obsidian note かの最終判断、commit、push、最終報告はメインスレッドが担う。

### Knowledge Note Rules

ユーザー向け知識体系は、日本語で読める説明を基本にする。

英語の正式名称、略語、検索語、論文タイトル、API 名、ライブラリ名、モデル名、評価指標は、後から公式資料、論文、実装へ接続するために残す。

Glossary note は `99_System/Bases/Glossary.base`、論文 note は `99_System/Bases/Academic Papers.base` に表示される property を埋める。未確認、出典確認、開発応用は `20_Areas/Knowledge Dashboard.md`、`99_System/Bases/Knowledge Review Queue.base`、`99_System/Bases/Source Access Review.base`、`99_System/Bases/Development Application.base` から辿れるようにする。Base file は一覧の定義であり、知識の本体は個別 Markdown note に残す。

初出では、可能な限り次の形を使う。

```text
日本語での理解（English formal name、略語）
```

## Engineering Rules

- 変更前に既存ファイルの責務を確認し、同じ情報を複数文書へ重複記載しない。
- 依頼で求められていない将来拡張、汎用化、設定化、抽象化は追加しない。追加する場合は、今回の依頼で必要な入力、処理、出力、または既存運用上の差し替え点を説明できることを条件にする。
- 変更は最小差分を原則とする。差分が大きい、横断的、または危険操作が混ざる場合は、そのまま進めず、分割案を先に出す。
- 編集後は、変更した行が利用者の依頼、必要な verify、または自分の変更で発生した不要 import、不要変数、不要設定の cleanup に対応しているか確認する。対応を説明できない隣接 refactor、表記統一、整形、削除は行わない。
- 実装または文書更新を始める前に、作業の成功条件を短く定義する。成功条件には、変更する対象、変えない対象、確認するコマンドまたは確認観点を含める。3ステップ以上、または責務境界・仕様判断を含むタスクでは、`変更範囲`、`保持すべき公開挙動`、`最小 verify` を先に明示する。
- 解釈が複数あり、外部契約、公開挙動、削除、破壊的操作、仕様判断、利用者の明示判断が必要な項目に影響する場合は、前提を置いて進めず利用者に確認する。影響が局所的で戻せる場合は、前提を明示して進め、最終報告でその前提と確認結果を書く。
- データ取得、要約、タグ付け、画面表示、永続化は責務を分ける。
- 外部サイト取得を追加する場合は、対象サイト、取得方法、保存項目、取得頻度、停止条件を先に文書化する。
- Python 実行は WSL では `.venv/bin/python`、Windows では `.venv\Scripts\python.exe` を優先する。
- Streamlit 起動は WSL では `.venv/bin/python -m streamlit run app.py`、Windows では `.venv\Scripts\python.exe -m streamlit run app.py` を使う。

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
  - WSL: `.venv/bin/python -m compileall src app.py`
  - WSL: `.venv/bin/python -m pytest tests -p no:cacheprovider --basetemp=<run-specific-dir>`
  - WSL: `.venv/bin/python -m streamlit run app.py --server.headless=true --server.port=<port> --browser.gatherUsageStats=false` を一時起動し、`http://127.0.0.1:<port>` が HTTP 200 を返すこと

## Delivery Rule

- 最終報告は、何を変えたか、なぜ変えたか、影響範囲、GUI確認要否を優先する。
- 最終報告では、実施済み、未実施、未確認、承認待ちを分けて書く。
- GUI 確認が不要な変更なら、その理由を明記する。
- verify 未通過では通常の commit / push を行わない。Codex がセッション中に意味のある差分を作った場合、ユーザーが停止を明示しない限り、verify 通過後は commit と `origin/main` への push までを既定の完了状態とする。verify 手段が未整備なら勝手に増やさず、その旨を報告する。

## Short Command Defaults

ユーザーの短い指示は、追加説明を要求せずに次の既定動作へ展開する。

- `すすめて`: `STATUS.md` の現在の task bundle と `tasks_backlog` の優先順位を確認し、完了済み task を再開せず、次の 1 task を進める。実装を伴う場合は verify、関連 docs 同期、Session Git Sync Gate まで進める。
- `次にすすめて`: 現在の task が完了済みであることを確認し、`STATUS.md` または `tasks_backlog` に明記された次 task へ移る。完了済み task の追加掘り下げを既定にしない。
- `Docs整備して`: docs-only として扱う。実装ファイルを編集せず、`STATUS.md`、`tasks_backlog`、`DECISIONS.md`、関連 `spec` の整合性を確認し、次スレッド入口、非対象、完了条件を明記する。
- `スレッド移行して`: 次スレッドが会話履歴を読まなくても再開できるように、最初に読む正本、次の 1 task、非対象、終了条件、verify / commit 状態を `STATUS.md` などの正本へ残す。
- `見解だけ`: read-only として扱う。実装、commit、push をしない。必要な現物確認は行い、結論、根拠、不確実性、実装するなら最初に確認する事項を分けて報告する。
- `Pushまでしておいて`: 通常の追加要件ではなく、Session Git Sync Gate の実行漏れを補正する指示として扱う。この指示がなくても、意味のある差分があり条件を満たす場合は commit / push まで行う。

## Session Git Sync Gate

Codex がセッション中に意味のある差分を作った場合、ユーザーが停止を明示していない限り、既定の完了状態は次のすべてを満たす状態である。

1. 変更内容に対応する verify が通っている。
2. 必要な docs、`STATUS.md`、`tasks_backlog`、`DECISIONS.md`、関連 `spec` が同期されている。
3. 現在 task に関係する差分だけが stage されている。
4. active branch が `main` である。
5. commit が作成されている。
6. commit が `origin/main` へ push されている。
7. push 後に `git status --short --branch` を再確認し、未コミット差分なし、remote と同期済みであることを確認している。

次の場合は commit / push しない。

- verify が失敗している。
- 秘密情報、個人情報、生成キャッシュ、巨大な一時ファイルの混入疑いがある。
- ユーザー由来の無関係差分が同じファイルまたは同じ working tree に残っており、現在 task の差分だけを安全に stage できない。
- 仕様判断、release 判断、公開判断、削除判断など、ユーザー判断待ちの項目が残っている。
- no-op で、repo に意味のある差分がない。
- ユーザーが `commitしない`、`pushしない`、`見解だけ`、`docs案だけ` など、保存しない意図を明示している。

commit / push しない場合は、最終報告で理由、残っている差分、未実施または失敗した verify、次に必要な判断を明記する。
