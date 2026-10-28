# AGENTS.md

海外公開RM記事の収集・日本語での確認/選別を行うPython/Streamlit/SQLiteの個人用localアプリ。公開LPと発信はSideBiz_HotelRMが持つ。

- 公開RSS/ブログ一覧だけを取得し、ログイン/robots/規約/アクセス制御を回避しない。本文全文や原文の代替となる長文・構成再現を保存/公開しない。
- 記事DB、未確認記事、AI候補、手動メモはGit外の非公開SQLite。公開候補flagは公開承認ではない。
- automationはexports/public_rm_articles.jsonだけを更新する。1回最大5件、0件でもrun_at_utcを更新する。SideBiz反映はSideBiz Actionsの責務で、exportのpushと分けて確認する。
- 取得元契約はdocs/spec_001_sources.md。実データ破壊、schema migration、依存/権限変更、workflow dispatch、SideBiz反映、公開/deploy/releaseは明示承認が必要。
- secret、Cookie、token、PII、raw本文/ログ、端末cacheをGitへ入れない。
