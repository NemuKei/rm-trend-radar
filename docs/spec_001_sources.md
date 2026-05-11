# spec_001_sources

## Purpose

この仕様は、`rm-trend-radar` が扱う公開記事ソースの選定基準、取得方法、保存項目、取得頻度、取得停止条件を定義する。

この文書は、実サイトから記事を取得する実装を始める前の正本である。次スレッドでは、まず候補サイトを調査し、この文書へ結果を反映する。

## Scope

### In scope

- 公開 RSS の有無を確認する。
- 公開ブログ一覧ページの URL を確認する。
- 原文 URL、公開日、記事タイトル、取得元サイト名を取得できるか確認する。
- 取得頻度の初期案を決める。
- 取得してよい項目と保存しない項目を分ける。
- 取得対象から外す条件を定義する。

### Out of scope

- ログインが必要なページの取得
- 有料記事、会員限定記事、認証が必要な情報の取得
- 記事本文全文の保存
- 記事本文全文の転載
- 要約、タグ、重要度、示唆を生成する AI 処理の実装
- 副業リポ側 LP への無制限な自動反映。LP 自動反映を行う場合は、公開する項目、保存しない項目、実行頻度、停止条件を `docs/spec_002_review_workflow.md` とこの文書で定義してから実装する。
- Cloudflare、独自ドメイン、公開アプリ化の設計

## Source Selection Criteria

初期取得対象は、次の条件を満たす候補を優先する。

- ホテル、宿泊業、レベニューマネジメント、価格最適化、需要予測、流通、予約行動に関係する公開記事を継続的に発信している。
- RSS がある、または公開ブログ一覧ページから記事 URL、公開日、タイトルを安定して確認できる。
- ログイン、有料会員登録、フォーム送信、JavaScript 実行後の閉じた API 取得を必要としない。
- robots.txt、利用規約、サイト上の明示的な禁止表示に反しない範囲で取得できる。
- 取得頻度を低くしても情報確認の価値が残る。

## Candidate Sources

2026-05-02 の初期調査では、候補 8 件から初期 MVP の取得対象を 5 件に絞った。

初期 MVP の取得対象は、公式 RSS またはカテゴリ別 RSS が確認でき、robots.txt で RSS またはブログ記事への一般取得が明示的に禁止されていない候補を優先した。

初期 MVP の取得対象:

- IDeaS
- SiteMinder
- RoomPriceGenie
- Revfine
- Hotel Speak

初期 MVP では後回しにする候補:

- Mews
- Lighthouse
- Hospitality Net

後回しにする理由は `Source Evaluation Table` の `Notes` に記録する。

初期調査前の候補一覧は次の通りであった。

- IDeaS
- SiteMinder
- Mews
- RoomPriceGenie
- Lighthouse
- Revfine
- Hospitality Net
- Hotel Speak

この一覧は、初期候補であり、取得対象として確定していない。RSS URL、公開ブログ一覧 URL、robots.txt、利用規約、取得してよい項目を確認するまでは、実装に入らない。

## Source Evaluation Table

調査結果は次の表に追記する。

| Source | Status | RSS | Public listing URL | Allowed fields | Proposed frequency | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| IDeaS | 初期対象 | `https://ideas.com/feed/` | `https://ideas.com/blog/` | RSS の `link`, `title`, `pubDate`, `category`, `description`。`content:encoded` と画像 URL は取得しても保存しない。 | 1 日 1 回以下 | robots.txt は `User-agent: *` に対して全体 Disallow なし。RSS はサイト全体フィードで、ホテル以外に駐車場領域の記事も含まれるため、P2-02 でカテゴリまたはキーワードによる採否判定を決める。 |
| SiteMinder | 初期対象 | `https://www.siteminder.com/r/feed/` | `https://www.siteminder.com/r/` | RSS の `link`, `title`, `pubDate`, `category`, `description`。`content:encoded` と画像 URL は取得しても保存しない。 | 1 日 1 回以下 | robots.txt は `/wp-admin/` などを禁止し、`/r/` と `/r/feed/` は禁止対象ではない。RSS の記事量が多いため、P2-02 でカテゴリ採否を決める。 |
| Mews | 後回し | 公式 RSS は未採用。robots.txt に `Disallow: */feed` があるため feed 形式の取得を初期対象にしない。 | `https://www.mews.com/en/blog` | 公開一覧ページから記事 URL、タイトル、公開日、カテゴリを確認できる可能性はあるが、初期 MVP ではページ解析を実装しない。 | 未設定 | 公開ブログ一覧は確認できたが、RSS 利用が robots.txt で禁止されている。RSS なしのページ解析は、RSS 対象の取得契約が固まった後に再検討する。 |
| RoomPriceGenie | 初期対象 | `https://roompricegenie.com/feed/` | `https://roompricegenie.com/category/blog/` | RSS の `link`, `title`, `pubDate`, `category`, `description`。`content:encoded` と画像 URL は取得しても保存しない。 | 1 日 1 回以下 | robots.txt は `/wp-admin/` を禁止し、主要検索クローラと主要 AI クローラを許可している。RSS はサイト全体フィードで、Revenue Management 以外の記事も含まれるため、P2-02 でカテゴリ採否を決める。 |
| Lighthouse | 後回し | 公式 RSS は確認できない。`https://www.mylighthouse.com/resources/blog/rss.xml` は 404 相当の HTML を返す。 | `https://www.mylighthouse.com/resources/blog` | 公開一覧ページから記事 URL、タイトル、公開日、カテゴリを確認できる可能性はあるが、初期 MVP ではページ解析を実装しない。 | 未設定 | robots.txt は一般取得を許可しているが、RSS が確認できない。ページ構造は Next.js 生成 HTML で、RSS 対象より実装負荷が高いため後回しにする。 |
| Revfine | 初期対象 | `https://www.revfine.com/category/hotel-blog/revenue-management/feed/` | `https://www.revfine.com/category/hotel-blog/revenue-management/` | RSS の `link`, `title`, `pubDate`, `category`, `description`。`content:encoded` と画像 URL は取得しても保存しない。 | 1 日 1 回以下 | 公式 RSS 一覧に Revenue Management Tips がある。robots.txt は `User-agent: *` に対して全体 Disallow なし。カテゴリ別 RSS を優先する。 |
| Hospitality Net | 後回し | `https://www.hospitalitynet.org/rss/news.xml` | `https://www.hospitalitynet.org/news` | RSS の `link`, `title`, `pubDate`, `category`, `description` は確認できる。 | 未設定 | 公式 RSS ページと robots.txt の `/rss/` Allow は確認済み。ただしニュース量が多く、プレスリリース、投資、採用、開業など幅広い記事が混在する。初期 MVP では対象を広げすぎない方針のため、RSS 対象 5 件の取得契約を先に固める。 |
| Hotel Speak | 初期対象 | `https://www.hotelspeak.com/category/hotel-revenue-management/feed/` | `https://www.hotelspeak.com/category/hotel-revenue-management/` | RSS の `link`, `title`, `pubDate`, `category`, `description`。`content:encoded` と画像 URL は取得しても保存しない。 | 1 日 1 回以下 | robots.txt は `User-agent: *` に対して全体 Disallow なし。カテゴリ別 RSS を優先する。更新頻度は高すぎないため初期対象に適する。 |

## Research Evidence

2026-05-02 時点で確認した公開 URL は次の通りである。

| Source | Evidence URLs |
| --- | --- |
| IDeaS | `https://ideas.com/blog/`, `https://ideas.com/feed/`, `https://ideas.com/robots.txt` |
| SiteMinder | `https://www.siteminder.com/r/`, `https://www.siteminder.com/r/feed/`, `https://www.siteminder.com/robots.txt` |
| Mews | `https://www.mews.com/en/blog`, `https://www.mews.com/robots.txt` |
| RoomPriceGenie | `https://roompricegenie.com/category/blog/`, `https://roompricegenie.com/feed/`, `https://roompricegenie.com/robots.txt` |
| Lighthouse | `https://www.mylighthouse.com/resources/blog`, `https://www.mylighthouse.com/resources/blog/rss.xml`, `https://www.mylighthouse.com/robots.txt` |
| Revfine | `https://www.revfine.com/rss-feeds/`, `https://www.revfine.com/category/hotel-blog/revenue-management/feed/`, `https://www.revfine.com/robots.txt` |
| Hospitality Net | `https://www.hospitalitynet.org/rss`, `https://www.hospitalitynet.org/rss/news.xml`, `https://www.hospitalitynet.org/robots.txt` |
| Hotel Speak | `https://www.hotelspeak.com/category/hotel-revenue-management/`, `https://www.hotelspeak.com/category/hotel-revenue-management/feed/`, `https://www.hotelspeak.com/robots.txt` |

## Allowed Stored Fields

初期 MVP で保存してよい項目は次の通りである。

- 原文 URL
- 取得元サイト名
- 原文公開日
- 英語タイトル
- 日本語タイトル
- 日本語要約
- タグ
- 重要度
- レベニューマネジメント担当者向けの示唆
- 自分用要約
- 公開用コンテンツ
- 手動メモ
- 取得日時
- 更新確認日時

## Initial Fetch Method

初期 MVP の記事取得は RSS を優先する。

- 初期対象 5 件は、`Source Evaluation Table` に記録した RSS URL から取得する。
- RSS が確認できない Mews と Lighthouse は、初期 MVP の取得実装に含めない。
- Hospitality Net は RSS が確認できるが、記事範囲が広いため初期 MVP の取得実装に含めない。
- 公開ブログ一覧ページの HTML 解析は、初期 RSS 取得が安定してから別タスクで検討する。

RSS に `content:encoded` が含まれる場合でも、記事本文全文として扱い、保存しない。RSS item の `description` は記事概要または抜粋を含むことがあるため、初期 MVP では永続化しない。将来、要約生成の入力として一時的に使う場合も、保存可否を別途仕様化してから実装する。

## RSS Item Mapping

RSS item から読み取る項目と、SQLite の `articles` テーブルへ保存する項目の対応は次の通りである。

| RSS item field | Use | Stored column | Rule |
| --- | --- | --- | --- |
| `link` | 原文 URL と重複判定キー | `url` | 前後空白を除去し、URL フラグメントと `utm_*`, `fbclid`, `gclid`, `mc_cid`, `mc_eid` などの追跡用クエリを除去した URL を保存する。記事本文は取得しない。 |
| `title` | 英語タイトル | `title_en` | HTML エンティティを文字として復元し、前後空白を除去して保存する。 |
| `pubDate` | 原文公開日 | `published_date` | RSS の日時を解釈し、日付部分を `YYYY-MM-DD` で保存する。`pubDate` が存在しない item は初期 MVP では取り込まない。 |
| source config | 取得元サイト名 | `source_name` | RSS URL ごとに固定値を持つ。例: `IDeaS`, `SiteMinder`, `RoomPriceGenie`, `Revfine`, `Hotel Speak`。 |
| `category` | 初期タグ候補 | `tags_json` | RSS category を小文字化し、空白を `-` に置換したタグにする。すべての新規取得記事に `unreviewed` を追加する。category がない場合は `unreviewed` のみ保存する。 |
| `guid` | 補助情報 | 保存しない | `link` がない場合の代替キーには使わない。初期 MVP では `link` がない item を取り込まない。 |
| `description` | 将来の要約入力候補 | 保存しない | 初期 MVP では永続化しない。画面表示にも使わない。 |
| `content:encoded` | 使用しない | 保存しない | 記事本文全文を含む可能性があるため、読み取っても保存、表示、要約欄への転記をしない。 |
| image, enclosure, media fields | 使用しない | 保存しない | 画像、動画、添付資料本体は初期 MVP の対象外とする。 |

RSS 取得直後の記事は、手動確認または将来の自動処理の前段階である。既存の `articles` テーブルは日本語確認項目を必須としているため、新規取得時の初期値は次の通りにする。

| Stored column | Initial value for fetched item |
| --- | --- |
| `title_ja` | `title_en` と同じ値を入れる。これは翻訳済みタイトルではなく、未翻訳の仮表示である。 |
| `title_priority` | `title_en` のキーワードだけから機械的に付ける仮重要度。`high`, `medium`, `low` のいずれかを保存する。人間が確定する `importance` とは別項目である。 |
| `title_priority_reason` | `title_priority` の判定に使ったタイトル内キーワード、または既定値にした理由を保存する。 |
| `summary_ja` | `未要約。原文リンクを確認してください。` |
| `importance` | `3` |
| `rm_implication` | `未記入。原文確認後に追記してください。` |
| `personal_summary` | 空文字。自分用の詳細要約または読解メモは、原文確認後に画面から保存する。 |
| `public_tip_ja` | 空文字。日本施設向けTips本文は、原文確認後に画面から保存する。 |
| `sns_post_draft` | 空文字。SNS 投稿用の短文下書きは、原文確認後に画面から保存する。 |
| `newsletter_lead_draft` | 空文字。メルマガ冒頭文の下書きは、原文確認後に画面から保存する。 |
| `internal_share_summary` | 空文字。社内共有用の短い要約は、原文確認後に画面から保存する。 |
| `manager_checklist` | 空文字。支配人または現場担当者向けの確認項目は、原文確認後に画面から保存する。 |
| `source_credit` | 空文字。参考元記事の出典表記は、原文確認後に画面から保存する。 |
| `note` | `RSS取得直後。要約、重要度、示唆は未確認。` |

## Duplicate and Update Rules

重複判定は、正規化した `url` を唯一のキーとして行う。

- 同じ `url` が存在しない場合は、新規記事として追加する。
- 同じ `url` が存在する場合は、既存記事として扱い、手動確認済みの項目を上書きしない。
- 既存記事で上書きしてよい項目は、`source_name`, `published_date`, `title_en`, `title_priority`, `title_priority_reason`, `updated_at` に限定する。
- `title_ja`, `summary_ja`, `tags_json`, `importance`, `rm_implication`, `personal_summary`, `public_tip_ja`, `sns_post_draft`, `newsletter_lead_draft`, `internal_share_summary`, `manager_checklist`, `source_credit`, `note` は、利用者が手動編集する可能性があるため RSS 再取得では上書きしない。
- `interest_candidate` と `public_candidate` は、利用者が画面で付ける内部フラグであるため RSS 再取得では上書きしない。
- RSS 側から item が消えても、SQLite の既存記事は削除しない。

このルールにより、RSS 再取得は「新着記事の追加」と「原文側メタデータの軽い更新」だけを行う。手動メモ、重要度、示唆は、利用者が明示的に変更したデータとして扱う。

## Fetch Failure Handling

取得失敗時の扱いは次の通りである。

- 1 つの source の取得に失敗しても、他の source の取得は続行する。
- 取得失敗時に即時再試行しない。
- 失敗した source は次回実行時に再確認する。
- 失敗した source の既存記事を削除しない。
- RSS の XML 解析に失敗した場合、その source の item は取り込まない。
- 必須項目である `link`, `title`, `pubDate` のいずれかが欠ける item は取り込まない。
- 初期 MVP では取得エラーを SQLite に保存しない。実行ログまたは画面上の一時メッセージで確認する。

## Initial Source Config

初期実装では、取得対象 source をコード内または設定ファイルで次のように固定定義する。実装時に配置先を決めるが、設定が表す契約はこの表を正本にする。

| source_name | feed_url | listing_url | use in initial MVP |
| --- | --- | --- | --- |
| IDeaS | `https://ideas.com/feed/` | `https://ideas.com/blog/` | yes |
| SiteMinder | `https://www.siteminder.com/r/feed/` | `https://www.siteminder.com/r/` | yes |
| RoomPriceGenie | `https://roompricegenie.com/feed/` | `https://roompricegenie.com/category/blog/` | yes |
| Revfine | `https://www.revfine.com/category/hotel-blog/revenue-management/feed/` | `https://www.revfine.com/category/hotel-blog/revenue-management/` | yes |
| Hotel Speak | `https://www.hotelspeak.com/category/hotel-revenue-management/feed/` | `https://www.hotelspeak.com/category/hotel-revenue-management/` | yes |
| Mews | none | `https://www.mews.com/en/blog` | no |
| Lighthouse | none | `https://www.mylighthouse.com/resources/blog` | no |
| Hospitality Net | `https://www.hospitalitynet.org/rss/news.xml` | `https://www.hospitalitynet.org/news` | no |

## Manual Fetch Command

初期 MVP の RSS 取得は、人間が端末から明示的に実行する手動コマンドとして開始する。定期実行、バックグラウンド常駐、クラウド実行は初期 MVP に含めない。

### Command

```powershell
.venv\Scripts\python.exe -m rm_trend_radar fetch
```

`.venv` が壊れている環境では、同等の Python 実行環境から `PYTHONPATH=src` を指定して実行してよい。ただし正本の利用コマンドは、リポジトリの標準に合わせて `.venv\Scripts\python.exe -m rm_trend_radar fetch` とする。

### Options

| Option | Required | Default | Meaning |
| --- | --- | --- | --- |
| `--source SOURCE_NAME` | no | all initial MVP sources | 指定した source だけを取得する。複数回指定できる。source 名は `Initial Source Config` の `source_name` を使う。大文字小文字は区別しない。 |
| `--dry-run` | no | false | RSS を取得して parser までは実行するが、SQLite へ追加または更新しない。 |
| `--json` | no | false | 人間向けの行表示ではなく、機械可読な JSON を標準出力へ出す。 |
| `--timeout SECONDS` | no | 20 | 1 source あたりの HTTP 取得 timeout 秒数。 |

## Scheduled Fetch Policy

初期 MVP の次段階では、記事取得を定期実行してよい。2026-05-11 以降は、取得した記事を副業リポ側 LP の短い記事一覧データへ反映する処理も自動化してよい。ここでいう定期実行は、初期対象 5 件の RSS から新規記事メタデータを取得し、LP に出してよい項目だけを後続処理へ渡す処理である。

記事取得と LP 反映は、実行場所と責務を分ける。

- GitHub Actions: RSS メタデータ取得だけを担当する。SQLite、公開候補フラグ、副業リポ側 LP ファイルは更新しない。
- Codex アプリ automation: 翻訳、短い紹介文作成、公開カテゴリ付与、副業リポ側 LP ファイル更新、検証、実行結果レポートを担当する。

定期実行で行ってよいことは次の通りである。

- `Initial Source Config` で `use in initial MVP = yes` の source だけを取得する。
- 実行頻度は source ごとに 1 日 1 回以下にする。通常運用の初期値は 3 日に 1 回程度とする。
- 保存項目、重複判定、更新判定、取得失敗時の扱いは、この文書の `RSS Item Mapping`、`Duplicate and Update Rules`、`Fetch Failure Handling` に従う。
- `title_ja`, `summary_ja`, `importance`, `rm_implication`, `personal_summary`, `public_tip_ja`, `sns_post_draft`, `newsletter_lead_draft`, `internal_share_summary`, `manager_checklist`, `source_credit`, `note`, `review_status`, `interest_candidate`, `public_candidate` は、定期実行でも上書きしない。
- 定期実行の結果は、追加件数、更新件数、失敗 source、LP 更新対象件数をログまたは実行結果で確認できるようにする。

定期実行で行ってはいけないことは次の通りである。

- 記事本文全文を保存する。
- RSS の `description` または `content:encoded` を日本語要約として自動保存する。
- AI API を呼び出して、記事本文の代替になる長文要約、詳細な独自解説、重要度、示唆を自動確定する。
- 記事本文全文、RSS `description`、RSS `content:encoded` を LP 表示本文として保存または転記する。
- 副業リポ側 LP に、自分用要約、手動メモ、SNS 投稿案、メルマガ用リード文、社内共有用 3 行要約、支配人・現場向けチェックリストを自動反映する。
- X、メルマガ、その他の外部公開先へ送信する。

副業リポ側 LP へ自動反映してよい項目は、日本語タイトル、原文記事の代替にならない短い紹介、取得元、公開日、原文 URL、公開カテゴリに限定する。詳細な重要度、業務上の示唆、個別解説ページの掲載判断は、定期取得とは別の人間の確認ワークフローに残す。

### GitHub Actions Scheduled Snapshot

定期取得の主経路は GitHub Actions とする。GitHub Actions は private repository のまま利用できる。公開 repository に変更する必要はない。ただし、private repository で GitHub-hosted runner を使う場合は、GitHub Actions の利用枠または課金条件の対象になる。

GitHub Actions workflow は `.github/workflows/fetch-rss-snapshot.yml` に置く。実行条件は次の通りである。

- `schedule`: 3 日に 1 回程度、05:37 UTC。これは日本時間 14:37 に相当する。
- `workflow_dispatch`: 手動実行。
- `permissions`: `contents: read` のみ。
- 実行時間上限: 10 分。

GitHub Actions では、次の command を実行する。

```powershell
python -m rm_trend_radar fetch-snapshot --output artifacts/rss_snapshot.json --timeout 20 --allow-partial
```

`fetch-snapshot` は SQLite を更新しない。RSS から取得できるメタデータだけを JSON artifact として出力する。

GitHub Actions では `--allow-partial` を付ける。これは、一部 source の取得に失敗しても、少なくとも 1 source の取得に成功している場合は workflow を成功扱いにし、失敗 source を `sources[].failed` と `sources[].error` に記録した artifact を残すためである。全 source が失敗した場合、または CLI 引数が不正な場合は失敗扱いにする。

出力 JSON の契約は次の通りである。

```json
{
  "generated_at_utc": "2026-05-04T00:00:00+00:00",
  "contract": "rss-metadata-only-v1",
  "lp_ready": false,
  "publish_decision": "manual_review_required",
  "sources": [
    {
      "source": "IDeaS",
      "fetched": 10,
      "failed": 0,
      "error": null
    }
  ],
  "articles": [
    {
      "source_name": "IDeaS",
      "url": "https://example.com/article",
      "published_date": "2026-05-01",
      "title_en": "Article title",
      "tags": ["revenue-management", "unreviewed"],
      "review_status": "unreviewed",
      "public_candidate": false
    }
  ]
}
```

この JSON は LP 側の直接入力ではない。`lp_ready` は常に `false` とし、`publish_decision` は `manual_review_required` とする。LP 側に渡すデータは、LP 自動反映用に別途生成する短い記事一覧データとする。LP 自動反映用データには、記事本文全文、RSS `description`、RSS `content:encoded`、自分用要約、手動メモ、長い公開用コンテンツを含めない。

### Codex App LP Reflection Automation

GitHub Actions の取得結果を確認した後、翻訳、短い紹介文作成、公開カテゴリ付与、副業リポ側 LP 反映は Codex アプリの automation で実行する。

- automation ID: `rm-trend-radar-lp-reflection`
- schedule: 3 日に 1 回程度、15:10 JST。
- 対象 workspace:
  - `C:\Users\n-kei\dev\github\rm-trend-radar`
  - `C:\Users\n-kei\dev\SideBiz_HotelRM`
- 入力: GitHub Actions の RSS snapshot、または `rm-trend-radar` のローカル SQLite に保存された取得済みメタデータ。
- 出力: `SideBiz_HotelRM` の `02_Service\web_lp\data\overseas_rm_articles.json` と `02_Service\web_lp\overseas_rm_articles.html`。
- 1 回の実行で新規に LP へ追加する記事数の目安: 最大 5 件。判断に迷う記事は公開候補にせず、実行結果に保留理由を残す。
- commit / push: 検証が通過した場合、変更がある repository ごとに commit し、現在の追跡先 branch へ push する。検証失敗、公開対象外項目の混入、原文記事の代替になる長文、判断に迷う差分がある場合は commit / push しない。

Codex automation が LP 用データへ含めてよい項目は、`public_category`, `public_category_label`, `title_ja`, `summary_ja`, `source_name`, `published_date`, `url` に限定する。記事本文全文、RSS `description`、RSS `content:encoded`、自分用要約、手動メモ、SNS 投稿案、メルマガ用リード文、社内共有用 3 行要約、支配人・現場向けチェックリスト、原文記事の代替になる長文は含めない。

Codex automation の実行後は、少なくとも次を検証する。

- `rm-trend-radar`: `.venv\Scripts\python.exe -m compileall src app.py`
- `rm-trend-radar`: `.venv\Scripts\python.exe -m pytest tests -p no:cacheprovider --basetemp=<run-specific-dir>`
- `SideBiz_HotelRM`: `02_Service\web_lp\scripts\refresh_overseas_rm_articles.py` の `py_compile`
- `SideBiz_HotelRM`: `data\overseas_rm_articles.json` に許可項目以外が含まれていないこと
- `SideBiz_HotelRM`: `overseas_rm_articles.html` の記事件数、カテゴリ件数、日本語タイトル一覧の折りたたみ件数
- 両 repository: `git diff --check`

検証が通過し commit / push した場合は、実行結果に repository ごとの commit hash と push 先 branch を含める。

### Local Windows Scheduled Task

ローカル Windows では、必要な場合だけ次の script を使って RSS 取得を登録できる。通常運用の主経路は GitHub Actions の RSS snapshot と Codex アプリ automation であり、この Windows タスクは手元で追加確認したい場合の任意手段である。

```powershell
.\scripts\Register-ScheduledFetch.ps1 -At "14:37"
```

登録されたタスクは、次の script を呼び出す。

```powershell
.\scripts\Invoke-ScheduledFetch.ps1
```

`Invoke-ScheduledFetch.ps1` は、リポジトリ直下を working directory として `.venv\Scripts\python.exe -m rm_trend_radar fetch --json --timeout 20` を実行する。実行結果は標準出力にも表示し、`logs/scheduled-fetch-YYYYMMDD.jsonl` に 1 実行 1 行の JSON Lines として保存する。

登録 script の引数は次の通りである。

| Option | Required | Default | Meaning |
| --- | --- | --- | --- |
| `-TaskName NAME` | no | `RM Trend Radar RSS Fetch` | Windows タスクスケジューラに登録するタスク名。 |
| `-At HH:MM` | no | `14:37` | 1 日 1 回の実行時刻。 |
| `-TimeoutSeconds SECONDS` | no | `20` | 1 source あたりの HTTP 取得 timeout 秒数。 |
| `-PythonPath PATH` | no | `.venv\Scripts\python.exe` | 使用する Python executable。 |
| `-DryRun` | no | false | 登録したタスクで SQLite へ書き込まない試験実行を行う。 |
| `-WhatIf` | no | false | Windows タスクスケジューラへ登録せず、登録内容だけを確認する。 |

実行 script の引数は次の通りである。

| Option | Required | Default | Meaning |
| --- | --- | --- | --- |
| `-PythonPath PATH` | no | `.venv\Scripts\python.exe` | 使用する Python executable。 |
| `-TimeoutSeconds SECONDS` | no | `20` | 1 source あたりの HTTP 取得 timeout 秒数。 |
| `-Source SOURCE_NAME` | no | all initial MVP sources | 指定した source だけを取得する。複数指定できる。 |
| `-DryRun` | no | false | RSS を取得して parser までは実行するが、SQLite へ追加または更新しない。 |
| `-LogDirectory PATH` | no | `logs` | 実行ログの保存先。 |

### Output Contract

通常出力では、source ごとに次の値を標準出力へ表示する。

- `source`: 取得元サイト名
- `fetched`: RSS item から parser が取り出した item 数
- `added`: SQLite に新規追加した記事数
- `updated`: SQLite 上の原文メタデータを更新した記事数
- `unchanged`: 既存記事と同じだった記事数
- `failed`: source 取得または XML 解析に失敗した場合は `1`、成功した場合は `0`

失敗理由は標準エラーへ表示する。`--json` の場合も、失敗理由は JSON の `error` に含める。

### Exit Codes

| Exit code | Meaning |
| --- | --- |
| `0` | 指定された全 source の取得、解析、保存処理が成功した。 |
| `1` | CLI の引数が不正、または未定義の source が指定された。 |
| `2` | 指定された全 source の取得または解析に失敗した。 |
| `3` | 一部 source は成功し、一部 source は失敗した。成功した source の記事は保存される。 |

### Safety Behavior

- 取得失敗 source があっても、成功した source の処理は取り消さない。
- `--dry-run` 指定時は SQLite に書き込まない。
- 手動確認項目である `title_ja`, `summary_ja`, `tags_json`, `importance`, `rm_implication`, `personal_summary`, `public_tip_ja`, `sns_post_draft`, `newsletter_lead_draft`, `internal_share_summary`, `manager_checklist`, `source_credit`, `note`, `interest_candidate`, `public_candidate` は RSS 再取得で上書きしない。
- `title_priority` と `title_priority_reason` は `title_en` から機械的に再計算できる項目であり、RSS 再取得で `title_en` が変わった場合は更新してよい。
- 記事本文全文、`description`, `content:encoded`, 画像、動画、添付資料は保存しない。

## Disallowed Stored Fields

初期 MVP で保存しない項目は次の通りである。

- 記事本文全文
- 原文記事の代替になる長文転載
- 有料記事、会員限定記事、認証が必要な情報
- 画像、動画、添付資料など、権利関係を追加確認する必要があるコンテンツ本体

## Fetch Frequency Policy

初期調査では、各サイトごとに次を確認する。

- RSS がある場合、1 日 1 回以下で確認してよいか。
- RSS がない場合、公開ブログ一覧ページを 2〜3 日に 1 回以下で確認してよいか。
- 更新頻度が低いサイトでは、週 1 回で十分か。
- 取得失敗時に即時再試行せず、次回実行まで待つ設計でよいか。

実装前の初期案は、取得先サイトへの負荷を下げるため、日次以下の頻度を上限とする。2026-05-11 以降の通常運用では、3 日に 1 回程度を初期値にする。GitHub Actions の cron で日付の `*/3` 指定を使う場合、月末から月初にかけて実行間隔が厳密な 72 時間にならない場合がある。この仕様では、厳密な 72 時間周期ではなく、月内でおおむね 3 日間隔の実行を許容する。

## Stop Conditions

次の条件に該当する場合、そのサイトは初期取得対象から外す。

- robots.txt または利用規約で自動取得が禁止されている。
- 記事一覧の確認にログイン、会員登録、有料契約、フォーム送信が必要である。
- 公開記事 URL、公開日、タイトルを安定して取得できない。
- 取得処理が記事本文全文の保存を前提にしないと成立しない。
- サイト構造が頻繁に変わり、個人用 MVP の保守負荷が高すぎる。

## Acceptance Criteria for `P2-01`

- 初期候補から 3〜5 サイトが選ばれている。
- 選んだ各サイトについて、RSS の有無、公開ブログ一覧 URL、取得してよい項目、想定取得頻度、注意点が表に記録されている。
- 取得対象から外した候補がある場合、外した理由が記録されている。
- 実装へ進む前に解決すべき未決事項が記録されている。

## Acceptance Criteria for `P2-02`

- RSS 取得と公開ブログ一覧ページ取得のどちらを優先するかが決まっている。
- 重複判定に使うキーが決まっている。
- 既存記事の更新判定方法が決まっている。
- 取得失敗時の扱いが決まっている。
- 保存する項目と保存しない項目が、実装者が誤読しない粒度で確定している。
