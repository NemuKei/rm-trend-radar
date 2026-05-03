# spec_002_review_workflow

## Purpose

この仕様は、取得済み記事を人間が確認し、日本語要約、タグ、重要度、レベニューマネジメント担当者向けの示唆、手動メモを確定するワークフローを定義する。

この仕様は、AI 要約や AI タグ付けの実装仕様ではない。初期 MVP では、AI API を呼び出さず、保存済みデータを人間が確認して蓄積する画面と保存処理を扱う。

## Scope

### In scope

- 取得済み記事の確認状態を保存する。
- 取得済み記事の日本語タイトル、日本語要約、タグ、重要度、レベニューマネジメント担当者向けの示唆、手動メモを画面から編集する。
- 未確認記事、確認済み記事、すべての記事を画面で切り替える。
- タイトルを見て気になった記事を、原文確認前の精査候補として保存する。
- 確認済み記事だけを、要約と示唆を読みやすい形式で確認する。
- 副業リポ側 LP に掲載する候補かどうかを保存する。
- 記事を表形式で俯瞰し、取得元、気になるフラグ、確認状態、重要度、タグ、公開候補を比較する。
- 記事タイトルだけから、読む順番を決めるための仮重要度を機械的に表示する。
- 確認済み記事だけを使って週次ダイジェストを Markdown として表示する。

### Out of scope

- AI API 呼び出し
- 記事本文の取得
- RSS の `description` の保存
- 記事本文全文または原文記事の代替になる長文の保存
- 週次ダイジェストの定期実行
- 週次ダイジェストの外部送信
- Cloudflare、独自ドメイン、認証、公開アプリ化
- 副業リポ側 LP への自動反映
- 副業リポ側 LP への直接書き込み
- X への投稿または予約投稿

## AI Scope for Initial MVP

初期 MVP では、AI 要約、AI タグ付け、AI 重要度付け、AI 示唆生成を実装しない。

理由は、現在の保存データが RSS の `link`, `title`, `pubDate`, `category` を中心にした記事メタデータであり、記事本文または RSS `description` を保存していないためである。この状態で AI に要約や示唆を生成させると、原文内容に基づかない推測が混ざる可能性がある。

将来 AI を使う場合は、実装前に次の項目を別途仕様化する。

- AI に渡す入力データ
- AI へ一時送信してよいが保存しないデータ
- AI の出力として保存してよい項目
- AI 出力を自動保存するか、候補として表示して人間が確定するか
- 原文記事の全文保存、全文転載、原文代替公開を避けるための制約

## Review Data Model

`articles` テーブルに次の確認状態を持たせる。

| Column | Meaning |
| --- | --- |
| `review_status` | 記事の確認状態。`unreviewed` または `confirmed` を保存する。 |
| `reviewed_at` | `review_status` を `confirmed` として保存した日時。未確認に戻した場合は空にする。 |
| `interest_candidate` | タイトルを見て気になった記事、あとで原文を読む候補かどうか。候補の場合は `1`、候補でない場合は `0` を保存する。 |
| `public_candidate` | 副業リポ側 LP に掲載する候補かどうか。候補の場合は `1`、候補でない場合は `0` を保存する。 |
| `personal_summary` | 自分用の詳細要約または読解メモ。公開候補 export、週次ダイジェスト、副業リポ側 LP、X 投稿には含めない。 |
| `public_tip_ja` | 日本施設向けTips本文。元記事の翻訳要約ではなく、日本の宿泊施設向けの独自解説として保存する。 |
| `sns_post_draft` | SNS 投稿用の短文下書き。 |
| `newsletter_lead_draft` | メルマガ冒頭文の下書き。 |
| `internal_share_summary` | 社内共有用の短い要約。 |
| `manager_checklist` | 支配人または現場担当者向けの確認項目。 |
| `source_credit` | 参考元記事の出典表記。 |
| `title_priority` | `title_en` に含まれるキーワードだけから機械的に付ける仮重要度。`high`, `medium`, `low` のいずれかを保存する。 |
| `title_priority_reason` | `title_priority` の判定に使ったタイトル内キーワード、または既定値にした理由を保存する。 |

確認状態の意味は次の通りである。

| Value | Meaning |
| --- | --- |
| `unreviewed` | RSS 取得直後、または人間が内容を確認していない記事。 |
| `confirmed` | 人間が原文または必要な周辺情報を確認し、日本語要約、タグ、重要度、示唆、メモを保存してよい状態にした記事。 |

既存 DB に `review_status`、`reviewed_at`、`interest_candidate`、`public_candidate`、`personal_summary`、`public_tip_ja`、`sns_post_draft`、`newsletter_lead_draft`、`internal_share_summary`、`manager_checklist`、`source_credit`、`title_priority`、`title_priority_reason` が存在しない場合、起動時に不足 column を追加する。既存記事は `unreviewed`、気になる候補ではない記事、公開候補ではない記事、自分用要約と公開用項目が空の記事として扱い、`title_en` から仮重要度と理由を再計算する。

## Title-based Provisional Priority

`title_priority` は、人間が原文を読む順番を決めるための補助情報である。人間が確認して保存する `importance` とは別の項目として扱う。

`title_priority` は、記事本文、RSS `description`、AI API の出力を使わない。`title_en` に含まれるキーワードだけを使って次のように判定する。

| Value | Meaning |
| --- | --- |
| `high` | レベニューマネジメント、価格、料金、需要予測、RevPAR、ADR、流通、在庫、予約ペースなど、レベニューマネジメント担当者が先に読む可能性が高い語を含む。 |
| `medium` | ホテル運営、マーケティング、ゲスト体験、テクノロジー、自動化、ガイドなど、関連領域だが価格判断や需要判断に直結するとは限らない語を含む。該当ルールがない場合も初期値として `medium` にする。 |
| `low` | 受賞、イベント、ウェビナー、ポッドキャスト、提携、プレスリリース、ブランド告知など、読む順番を後にしてよい可能性がある語を含む。 |

複数の種類の語が含まれる場合は、`high` を優先する。`high` が該当しない場合に `medium`、`medium` も該当しない場合に `low` を判定する。どのルールにも該当しない場合は `medium` とする。

この判定は仮分類であり、記事内容の正確な重要度を保証しない。原文を読む候補の選定では `interest_candidate` を使い、公開候補選定、週次ダイジェスト掲載、副業リポ側 LP への掲載判断では、人間が保存した `importance`、`review_status`、`public_candidate` を使う。

## Review UI

記事確認画面は、次の操作を提供する。

- 確認状態で `すべて`, `未確認`, `確認済み` を切り替える。
- 表形式で、公開日、取得元、気になるフラグ、確認状態、タイトル仮重要度、重要度、公開候補、タイトル、タグを俯瞰する。
- 一覧上で、表示中の記事の気になるフラグを付け外しして保存できる。
- 取得元、確認状態、気になるフラグ、公開候補、タイトル仮重要度、最低重要度、タグ、検索語で絞り込む。
- 表で選択した 1 件について、詳細情報と編集フォームを表示する。
- 各記事で次の項目を編集する。
  - 日本語タイトル
  - 日本語要約
  - タグ
  - 重要度
  - レベニューマネジメント担当者向けの示唆
  - 自分用要約
  - 日本施設向けTips
  - SNS投稿案
  - メルマガ用リード文
  - 社内共有用3行要約
  - 支配人・現場向けチェックリスト
  - 出典表記
  - 手動メモ
  - 確認状態
  - 気になる記事かどうか
  - 副業リポ側 LP の公開候補

タグは、当面は slug 形式で保存する。画面入力ではカンマ区切りを受け取り、保存時に小文字化し、空白や記号を `-` に寄せ、重複を除去する。

RSS 再取得では、手動確認項目である `title_ja`, `summary_ja`, `tags_json`, `importance`, `rm_implication`, `personal_summary`, `public_tip_ja`, `sns_post_draft`, `newsletter_lead_draft`, `internal_share_summary`, `manager_checklist`, `source_credit`, `note`, `review_status`, `reviewed_at`, `interest_candidate`, `public_candidate` を上書きしない。`title_priority` と `title_priority_reason` は、`title_en` から再計算できる機械的な仮分類であるため、RSS 再取得で `title_en` が変わった場合は更新してよい。

## Manual Summary Level

`summary_ja` と `rm_implication` は、確認済みレビュー画面で記事内容を見極めるための内部確認用テキストである。公開 LP や X にそのまま掲載する文章ではない。

`summary_ja` は、原則として 250 から 350 文字程度にする。記事本文の代替になる長文ではなく、原文を読むかどうか、公開候補にするかどうかを判断するために必要な範囲に限定する。

`summary_ja` には、次の内容を含める。

- 記事の主題または中心となる主張。
- 対象読者または対象業務。
- 記事で扱われている施策、論点、判断軸、または実務上の問題。
- 読む前に把握しておくべき前提条件または注意点。

`summary_ja` には、次の内容を含めない。

- 原文記事の本文構成をなぞった詳細な再構成。
- 原文を読まなくても記事内容の大部分が分かる長文説明。
- 長い引用または原文の連続した翻訳。
- 原文で確認できない推測。

`rm_implication` は、原則として 150 から 250 文字程度にする。レベニューマネジメント担当者が、その記事を自分の業務に照らして読むべきかを判断できる内容にする。

`rm_implication` には、次の内容を含める。

- レベニューマネジメント担当者が確認すべき判断。
- 価格設定、需要予測、販売制限、チャネル管理、競合比較、組織運用など、どの業務領域に関係するか。
- 実務で使う場合の注意点、確認条件、または導入前に見るべきデータ。

`rm_implication` には、次の内容を含めない。

- 原文記事の内容と対応しない一般論。
- 具体的な根拠がない売上改善効果の断定。
- 公開 LP や X にそのまま使う宣伝文。

## Personal Summary Policy

`personal_summary` は、利用者が自分で読むための詳細要約、ChatGPT などの大規模言語モデルで作成した読解メモ、原文確認時の詳しい論点整理を保存する内部項目である。

`personal_summary` は、`summary_ja` より長くてよい。原文確認、公開候補選定、後日の再読に使うための項目であり、公開 LP、X、公開候補 export preview、週次ダイジェストには含めない。

`personal_summary` に保存してよい内容は次の通りである。

- 原文記事の主題、全体要約、読むときの注意点。
- レベニューマネジメント担当者としての詳しい読解メモ。
- 大規模言語モデルで作成した自分用の要約または解説。
- 公開用文面にする前の下書き、論点整理、確認メモ。

`personal_summary` は非公開の内部項目である。第三者へ配布する要約リンク、公開 LP に掲載する本文、X 投稿文として扱わない。公開に使う場合は、原文記事の代替にならない短い紹介文と独自コメントへ別途圧縮する。

## ChatGPT Output Sorting Policy

ChatGPT Pro などの大規模言語モデルから、海外記事の解説と日本施設向け発信内容をまとめて受け取る場合、`rm-trend-radar` では保存先を分ける。

保存先は次の通りである。

| ChatGPT output section | Stored column | Rule |
| --- | --- | --- |
| 元記事の解説全体 | `personal_summary` | 内部読解メモとして保存する。公開候補 export preview には含めない。 |
| 記事の一言要約または短い紹介 | `summary_ja` | 原文を読むかどうか判断するための短い紹介として保存する。 |
| RM視点での解説の要点 | `rm_implication` | レベニューマネジメント担当者向けの判断ポイントとして保存する。 |
| 日本施設向け発信内容 | `public_tip_ja` | 公開 LP で使う主文候補として保存する。原文記事の構成を再現する要約ではなく、日本施設向けの独自解説にする。 |
| SNS投稿用ショート版 | `sns_post_draft` | X などの投稿下書きとして保存する。 |
| メルマガ用リード文 | `newsletter_lead_draft` | メルマガ冒頭文の下書きとして保存する。 |
| 社内共有用3行要約 | `internal_share_summary` | 社内共有用の短い要約として保存する。 |
| 支配人・現場向けチェックリスト | `manager_checklist` | 現場確認用の項目として保存する。 |
| 参考または Source 表記 | `source_credit` | 原文記事への出典表記として保存する。 |

公開用項目に保存する文章では、元記事の専門家コメント、見出し構成、論点順序を長く再現しない。元記事の紹介は短くし、日本の宿泊施設にとっての判断、確認すべき KPI、施設タイプ別の注意点、実務アクションを中心にする。

## Interest Candidate Policy

`interest_candidate` は、記事タイトルを見て原文確認の候補にするための内部フラグである。

`interest_candidate` は、次の状態とは別に扱う。

- `review_status`: 原文または必要な周辺情報を確認し、保存内容を確定したかどうか。
- `importance`: 原文確認後に人間が保存する重要度。
- `public_candidate`: 副業リポ側 LP に掲載する候補かどうか。

初期運用では、記事確認タブの一覧で日本語タイトルを見ながら `interest_candidate` を付ける。その後、`気になるのみ` で絞り込み、原文確認、要約、重要度、レベニューマネジメント担当者向けの示唆、公開候補の判断を行う。

## Reviewed Article UI

確認済みレビュー画面は、`review_status = confirmed` の記事だけを対象にする。

確認済みレビュー画面は、次の操作を提供する。

- 確認済み記事の件数、重要度 5 の件数、公開候補の件数、気になる記事の件数を表示する。
- 取得元、公開候補、最低重要度、検索語で絞り込む。
- 表形式で、公開日、取得元、重要度、公開候補、タイトル、タグを俯瞰する。
- 選択した記事について、日本語タイトル、英語タイトル、タグ、要約、レベニューマネジメント担当者向けの示唆、原文 URL を読みやすく表示する。
- 選択した記事について、公開候補フラグ、要約、示唆、自分用要約、公開用コンテンツ、メモを編集できる。

確認済みレビュー画面は、公開前の確認を効率化するための画面である。公開 LP や X にそのまま転記する長文を作る画面ではない。

## Public Candidate Policy

`public_candidate` は、副業リポ側 LP に載せる可能性がある記事を選別するための内部フラグである。

`rm-trend-radar` は、公開前の収集、確認、編集、選別を行う非公開の管理アプリとして扱う。副業リポ側 LP は、公開してよい記事だけを材料に、原文記事の代替にならない短い紹介、独自の見解、業務上の示唆を掲載する公開面として扱う。

公開 LP と X は、記事の存在、論点、読む理由を知らせる導線として扱う。詳細な内容理解は、原文サイトで行う。利用者は必要に応じてブラウザの翻訳機能を使って原文サイトを読む。

初期実装では、`public_candidate` を保存し、画面で絞り込めるところまでを扱う。副業リポ側 LP へ直接書き込む処理、X 投稿文の作成、X への投稿または予約投稿は後続タスクとする。

## Side Business LP Initial Listing Contract

副業リポ側 LP の初期実装では、公開候補記事を「記事を読むための一覧」として掲載する。初期掲載は、公開候補記事ごとに日本語タイトル、短い要約、取得元、公開日、原文リンクだけを表示する。日本施設向けの長い解説、SNS 投稿案、メルマガ用リード文、社内共有用 3 行要約、支配人・現場向けチェックリストは、初期一覧には表示しない。

この初期一覧の目的は、海外のホテル Revenue Management 関連記事を見つけやすくし、利用者を原文サイトへ送ることである。原文記事の内容を公開 LP 上で代替することではない。

副業リポ側で実装するページまたはセクションは、次の性質を持つ。

- 配置先: 副業リポ側の既存 LP に、海外ホテル Revenue Management 記事の紹介一覧セクションとして追加する。初期実装では新規ルートや個別記事ページを作らない。
- セクション ID: `overseas-rm-articles`。既存 LP の ID 命名規則がある場合は、その規則に合わせてよいが、役割が分かる名前にする。
- セクション見出し: `海外ホテル Revenue Management 記事`。
- セクションの役割: 海外ホテル Revenue Management 記事の紹介一覧。
- 対象記事: `rm-trend-radar` の公開候補 export に含まれる記事。条件は `review_status = confirmed` かつ `public_candidate = 1` である。
- 初期表示項目: `title_ja`, `summary_ja`, `source_name`, `published_date`, `url`。
- 任意表示項目: `tags`, `importance`。ただし、重要度は内部選別用の目安であるため、公開画面に出す場合は「重要度」という評価語ではなく、「注目度」など公開読者が誤解しにくい表現にする。
- 初期表示しない項目: `rm_implication`, `public_tip_ja`, `sns_post_draft`, `newsletter_lead_draft`, `internal_share_summary`, `manager_checklist`, `source_credit`, `personal_summary`, `note`。
- 並び順: `published_date` の新しい順を初期値とする。同じ公開日の記事は、`importance` が高い順、次に `title_ja` の昇順とする。
- 原文リンク: 外部リンクとして開く。リンクテキストは「原文を読む」または「Source」を使う。リンク先が原文サイトであることを明示する。
- 出典表記: 初期一覧では `source_name` と原文リンクを表示する。`source_credit` の長い表記は、詳細記事や個別紹介ページを作る場合に使う。
- 公開前チェック: `summary_ja` が原文記事の代替になるほど長くないこと、専門家コメントや記事構成を詳細に再現していないこと、原文 URL が表示されていることを確認する。

副業リポ側の実装スレッドに渡す最小入力は、公開候補タブの JSON preview である。副業リポ側では、JSON 配列の各要素から `title_ja`, `summary_ja`, `source_name`, `published_date`, `url` だけを初期表示に使う。

副業リポ側で扱うデータ構造は、次の型に相当する。

```ts
type OverseasRmArticle = {
  title_ja: string;
  summary_ja: string;
  source_name: string;
  published_date: string;
  url: string;
};
```

副業リポ側の初期実装では、上記のデータを静的配列として LP のコード内または LP が既に使っているローカルデータファイルに置いてよい。`rm-trend-radar` からの自動同期、API 化、定期更新、GitHub Actions 連携は初期実装の対象外とする。

副業リポ側の初期実装例は、次の Markdown 構造に相当する。

```md
## 海外ホテル Revenue Management 記事

海外のホテル Revenue Management、Pricing、Distribution、Hotel Tech に関する公開記事を紹介します。詳細は各原文サイトで確認してください。

### ホテルは直前料金を大幅に下げずに競争力を保てるのか

周辺ホテルが直前に値下げする市場で、自施設も追随すべきかを扱うRevfineの専門家パネル記事。直前値下げ自体を単純に否定するのではなく、初期価格、PACE、Booking Window、セグメント、ブランド価値を見ながら、到着直前に慌てて下げなくてもよい販売設計を早い段階から作るべきだと整理している。

- Source: Revfine
- Published: 2026-04-28
- [原文を読む](https://www.revfine.com/hotel-pricing-strategy-last-minute-rate-drops/)
```

この例は実装時の構造を示すためのものである。実際の公開日は、公開候補 export の `published_date` を使う。

初期一覧実装では、`public_tip_ja` を使った長い個別解説ページは作らない。個別解説ページを作る場合は、別タスクとして、原文の代替にならない独自解説の基準、ページ URL、見出し構成、引用量、公開前確認手順を改めて仕様化する。

## Side Business LP Source Introduction Contract

副業リポ側 LP には、海外記事一覧だけでなく、参照している海外 RM サイトの紹介も掲載してよい。初期実装では、記事一覧の直前または直後に、情報源紹介セクションを追加する。

このセクションの目的は、利用者が「どのような性格の海外情報源を見ているのか」を理解できるようにすることである。各サイトの記事内容を要約することや、各サイトの公式説明文を転載することではない。

副業リポ側で実装する情報源紹介セクションは、次の性質を持つ。

- 配置先: 副業リポ側の既存 LP に、海外記事一覧と近い位置で追加する。
- セクション ID: `overseas-rm-sources`。既存 LP の ID 命名規則がある場合は、その規則に合わせてよいが、役割が分かる名前にする。
- セクション見出し: `参照している海外 RM メディア・サービス`。
- セクションの役割: 海外ホテル Revenue Management 関連情報を確認するための情報源を紹介する。
- 初期表示項目: サイト名、短い紹介、主に確認するテーマ、公式サイトまたは記事一覧へのリンク。
- 初期表示対象: `IDeaS`, `SiteMinder`, `RoomPriceGenie`, `Revfine`, `Hotel Speak`。
- 初期表示しない対象: `Mews`, `Lighthouse`, `Hospitality Net`。これらは初期 MVP の取得対象ではないため、LP の情報源紹介には出さない。
- リンク: 外部リンクとして開く。リンクテキストは「公式サイトを見る」または「記事一覧を見る」を使う。
- 紹介文の粒度: 各サイト 1 から 2 文に留める。公式説明文の転載ではなく、このプロジェクトで確認する情報源としての役割を自分の言葉で説明する。

副業リポ側で扱うデータ構造は、次の型に相当する。

```ts
type OverseasRmSource = {
  name: string;
  description_ja: string;
  topics_ja: string[];
  url: string;
};
```

初期データは次の内容にする。

```ts
const overseasRmSources: OverseasRmSource[] = [
  {
    name: "IDeaS",
    description_ja:
      "ホテル向け Revenue Management System と収益最適化に関する知見を発信しているサービス。価格、需要予測、マーケティング投資、収益管理の考え方を確認する情報源として扱う。",
    topics_ja: ["Revenue Management System", "需要予測", "価格最適化", "ホテル収益管理"],
    url: "https://ideas.com/blog/",
  },
  {
    name: "SiteMinder",
    description_ja:
      "ホテルの販売チャネル、直販、予約行動、AI 活用に関する記事を多く扱うサービス。Revenue Management と Distribution の接点を確認する情報源として扱う。",
    topics_ja: ["Distribution", "直販", "OTA", "AI と予約行動"],
    url: "https://www.siteminder.com/r/",
  },
  {
    name: "RoomPriceGenie",
    description_ja:
      "中小規模ホテル向けの価格設定、動的料金、RevPAR、ADR などを実務寄りに扱うサービス。日々の料金判断や基本指標を確認する情報源として扱う。",
    topics_ja: ["動的料金", "ADR", "RevPAR", "料金最適化"],
    url: "https://roompricegenie.com/category/blog/",
  },
  {
    name: "Revfine",
    description_ja:
      "ホテル Revenue Management、価格戦略、収益指標、業界専門家の見解を扱うメディア。海外の RM 論点や専門家コメントを確認する情報源として扱う。",
    topics_ja: ["Revenue Management", "価格戦略", "収益指標", "専門家パネル"],
    url: "https://www.revfine.com/category/hotel-blog/revenue-management/",
  },
  {
    name: "Hotel Speak",
    description_ja:
      "ホテル業界の運営、マーケティング、収益管理に関する寄稿記事を扱うメディア。Revenue Management と経営、マーケティング、オーナー視点の接点を確認する情報源として扱う。",
    topics_ja: ["ホテル経営", "マーケティング", "Revenue Management", "オーナー視点"],
    url: "https://www.hotelspeak.com/category/hotel-revenue-management/",
  },
];
```

副業リポ側の初期実装では、上記のデータを静的配列として LP のコード内または LP が既に使っているローカルデータファイルに置いてよい。`rm-trend-radar` から情報源紹介データを export する処理は初期実装の対象外とする。

公開前チェックでは、各紹介文が公式サイトの文言を転載していないこと、サイト名とリンク先が一致していること、取得対象ではないサイトを初期情報源として表示していないことを確認する。

## Public Candidate Export Preview

公開候補タブは、`review_status = confirmed` かつ `public_candidate = 1` の記事だけを対象にする。

未確認記事は、`public_candidate = 1` であっても公開候補タブの Markdown と JSON には含めない。これは、公開 LP へ渡す前の最低条件として、人間が内容を確認済みにしていることを要求するためである。

公開候補タブの Markdown と JSON に含める項目は次の通りである。

- 取得元
- 原文 URL
- 公開日
- 日本語タイトル
- 英語タイトル
- 日本語要約
- タグ
- 重要度
- レベニューマネジメント担当者向けの示唆
- 出典表記
- 日本施設向けTips
- SNS投稿案
- メルマガ用リード文
- 社内共有用3行要約
- 支配人・現場向けチェックリスト

自分用要約 `personal_summary` と手動メモ `note` は、内部作業用の記録を含む可能性があるため公開候補 export preview には含めない。

公開候補 export preview は、副業リポ側 LP の実ファイルを更新しない。公開ページへ反映する前に、人間が Markdown または JSON の内容を確認し、原文記事の代替になる長文転載になっていないことを確認する。

## Weekly Digest

週次ダイジェストは、保存済みの確認済み記事データから Markdown を組み立てる。

初期条件は次の通りである。

- `review_status` が `confirmed` である。
- 公開日が画面で指定した対象期間内である。
- 重要度が画面で指定した最低重要度以上である。初期値は `4` とする。

週次ダイジェストに含める項目は次の通りである。

- 日本語タイトル
- 取得元
- 公開日
- 重要度
- 原文 URL
- 日本語要約
- レベニューマネジメント担当者向けの示唆

週次ダイジェストは、AI による新規文章生成を行わない。保存済みの確認済み記事データを、確認とコピーのために Markdown 形式へ整形する。

## Acceptance Criteria

- 既存 DB でも `review_status` と `reviewed_at` が追加され、起動できる。
- 既存 DB でも `interest_candidate` が追加され、起動できる。
- 既存 DB でも `public_candidate` が追加され、起動できる。
- 既存 DB でも `personal_summary` が追加され、起動できる。
- 既存 DB でも公開用コンテンツ項目が追加され、起動できる。
- 既存 DB でも `title_priority` と `title_priority_reason` が追加され、既存記事の `title_en` から再計算される。
- RSS 取得直後の記事は `unreviewed` になる。
- RSS 取得直後の記事は `title_en` から `title_priority` と `title_priority_reason` が保存される。
- 画面から確認項目を保存できる。
- 画面の一覧から、表示中の記事の気になるフラグを保存できる。
- 気になるフラグで、`すべて`, `気になるのみ`, `未指定` を切り替えられる。
- 画面から公開候補フラグを保存できる。
- 画面から自分用要約を保存できる。
- 画面から公開用コンテンツを保存できる。
- 記事確認画面で、タイトル仮重要度を列、詳細、絞り込み条件として確認できる。
- `confirmed` にした記事は `reviewed_at` が保存される。
- RSS 再取得で確認済み項目、自分用要約、公開用コンテンツ、気になるフラグ、公開候補フラグが上書きされない。
- RSS 再取得で `title_en` が変わった場合、タイトル仮重要度は新しい `title_en` から再計算される。
- 週次ダイジェストには、確認済み、対象期間内、重要度条件を満たす記事だけが含まれる。
- 週次ダイジェストは AI API を呼び出さず、保存済みデータだけから生成される。
- 公開候補タブには、確認済みかつ公開候補の記事だけが含まれる。
- 公開候補 export preview に手動メモは含まれない。
- 公開候補 export preview に自分用要約は含まれない。
- 確認済みレビュー画面には、確認済み記事だけが表示される。
- 確認済みレビュー画面で、要約、レベニューマネジメント担当者向けの示唆、原文 URL を同じ画面で確認できる。
