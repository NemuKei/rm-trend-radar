# AGENTS.md

## Purpose

このリポジトリは、ホテル・レベニューマネジメント領域の海外公開記事を収集し、日本語で確認するための個人用 Web アプリを開発する。

アプリは、原文記事へのリンク、日本語タイトル、日本語要約、タグ、重要度、レベニューマネジメント担当者向けの示唆、手動メモを扱う。記事本文の全文保存、全文転載、原文の代替公開は目的にしない。

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

## Engineering Rules

- 変更前に既存ファイルの責務を確認し、同じ情報を複数文書へ重複記載しない。
- データ取得、要約、タグ付け、画面表示、永続化は責務を分ける。
- 外部サイト取得を追加する場合は、対象サイト、取得方法、保存項目、取得頻度、停止条件を先に文書化する。
- Python 実行は `.venv\Scripts\python.exe` を優先する。
- Streamlit 起動は `.venv\Scripts\python.exe -m streamlit run app.py` を使う。

## Verification

- 実装変更後は、少なくとも次を確認する。
  - `.venv\Scripts\python.exe -m compileall src app.py`
  - `.venv\Scripts\python.exe -m pytest`（テストが存在する場合）
  - `.venv\Scripts\python.exe -m streamlit run app.py` で起動できること