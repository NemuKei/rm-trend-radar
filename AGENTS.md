<!-- agents-catalog-basis: repo-template-codex@8877297d; profile=solo-product; overlays=data-contract-and-migration,architecture-and-dependencies,second-brain-capture -->
# AGENTS.md

## Purpose

このリポジトリは、ホテル・レベニューマネジメント領域の海外公開記事を収集し、日本語で確認・選別するための個人用local Web appの正本である。

扱うのは原文link、日本語title、短いsummary、tag、priority、RM担当者向けの示唆、手動memo、公開候補判断である。記事本文の全文保存・転載、原文の代替公開は目的にしない。

## Working Contract

- 初手で読むのはroot `AGENTS.md`だけにする。追加文書は現在の問いと責務が一致するときだけ読む。
- 既定は`main`上のlinear workflowとする。branch / worktree / child taskは、利用者が並列進行を明示した場合だけ増やす。
- product挙動を変える前に、利用者が得る成果、今回の成功状態、変える対象、変えない対象、確認方法を短く固定する。
- source取得からSQLite保存、確認・編集、絞込、digestまたは公開候補exportまで、利用者が確認できる出口を含むvertical sliceとして実装する。途中layerだけを変えて完了にしない。
- 日常的で局所的な修正は直接進める。再発問題、複数境界をまたぐ変更、将来のproduct / data contractを狭める変更では、局所patch、boundedな根本修正、大きな再設計を比較する。
- `すすめて`系は、同じ利用者可視成果、spec、責務境界、verify setで閉じられるbundleとして扱う。`見解だけ`はread-only、`Docs整備して`はdocs-onlyとする。

## Source Map And Priority

- Security、法令、著作権、公開制約を最優先する。
- `docs/spec_*.md`: 外部挙動、取得契約、入出力、保存data、受け入れ条件。
- `docs/context/INTENT.md`: 複数仕様にまたがる判断原則。
- `docs/context/DECISIONS.md`: durable decisionとsupersession history。
- `docs/context/STATUS.md`: 現在地、re-entry、verification notes。
- `docs/tasks_backlog.md`: 実行順とtask tracking。追加だけでは仕様確定にならない。
- `README.md`: setup、実行、検証command。
- 実装codeはlive behaviorの証拠であり、specやactive decisionと食い違う場合はfresh testと合わせて不整合を解消する。

optional docsは存在するだけで毎回全文を読まない。sourceが衝突し、外部挙動、保存data、公開範囲へ影響する場合は推測せず、利用者確認または新decisionへrouteする。

## Product And Publication Boundaries

- app本体はPython、Streamlit、SQLiteによる個人利用のlocal管理面として扱う。公開面、認証、cloud DBを暗黙に追加しない。
- 収集対象は公開RSSまたは公開blog一覧pageに限定し、loginが必要なpage、robots.txtや利用規約に反する取得、access control回避を行わない。
- summaryは原文確認の補助であり、原文を読まずに代替できる長文や構成再現を作らない。公開面には短い紹介、独自の示唆、source、日付、原文linkだけを渡す。
- `rm-trend-radar`は非公開の収集・確認正本、`SideBiz_HotelRM`は公開LPと発信の正本である。公開候補flagがあっても自動的な公開承認を意味しない。
- RSS snapshot、SideBiz反映、automationの許可範囲と停止条件はactive spec / decisionを正本とし、取得、翻訳、公開判断、公開file更新の責務を混ぜない。

## Data, Architecture, And Dependencies

- data取得、正規化、summary / tag候補、確認、画面表示、永続化、public exportを、変更理由と検証境界に沿って分ける。architecture上きれいに見せるためだけにlayer、interface、fileを増やさない。
- 新しいsourceを追加する前に、対象site、取得方法、保存項目、取得頻度、停止条件、著作権・規約上の境界を`docs/spec_001_sources.md`へ反映する。
- SQLite schema、保存JSON、public export、CLI、config、file形式、SideBiz連携入出力をcontractとして扱う。意味またはshapeを変える場合はbefore / after、consumer、forward migration、validation、rollback、旧pathの削除条件を確認する。
- 既存dataを無断で削除、初期化、再解釈せず、適用済みの可能性があるmigrationを書き換えない。意味や新旧値が衝突する場合はsilent selectionしない。
- 独自実装や新packageの前に、repo内の既存実装、dependency、current documentation、type、APIを確認する。dependency追加 / 更新はmaintenance、security、license、lock-in、重複を確認してから承認境界へ進む。

## Safety And Knowledge Routing

- 明示承認なしで、実dataの破壊的変更、schema migration、dependency追加 / 更新、credential / secret / 権限変更、workflow dispatch、SideBiz反映、公開、deploy、releaseを行わない。
- secret、Cookie、token、PII、raw article本文、raw log全文、端末固有cacheをrepo管理対象へ入れない。
- Skillはtask-specific procedureだけを持ち、repo-wide ruleや設計原則を複製しない。CLIの外部contractを設計・変更するときだけ`create-cli`を使う。
- repo内docsを仕様・進捗・決定・taskの正本とする。SecondBrainは横断判断、他repoのfailure / verification、外部知識が今回の判断に必要な場合だけ参照する。
- SecondBrainへの保存は利用者が明示した場合だけ`second-brain-capture`で行う。routine taskやcloseoutに`capture-needed`を課さず、secret、credential、PII、raw log全文を保存しない。

## Verification And Closeout

- docs-onlyでは`git diff --check`、参照path、BOM、secret / credential / PII marker、`git status --short --branch`を確認する。
- implementation変更では、影響に応じて次を実行する。
  - macOS: `.venv/bin/python -m compileall src app.py`
  - macOS: `.venv/bin/python -m pytest tests -q -p no:cacheprovider --basetemp=<run-specific-dir>`
  - `.venv\Scripts\python.exe -m compileall src app.py`
  - `.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider --basetemp=<run-specific-dir>`
  - UI変更時は対象OSの同じPythonで`-m streamlit run app.py --server.headless=true --server.port=<port> --browser.gatherUsageStats=false`を一時起動し、HTTP 200と対象flowを確認する。
- 外部sourceのlive取得、SideBiz連携、automationは、taskが明示的に対象とする場合だけ個別のnetwork / cross-repo checkを追加する。
- 完了時は、変更、実行済み・未実行の検証、GUI確認要否、data / copyright / publication境界、SideBizへの`sync-needed`、残存riskを報告する。
