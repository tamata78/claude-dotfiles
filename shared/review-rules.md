# レビュー規約フラグメント（共有）

> このファイルは複数のレビューコマンド（`/pr-review` / `/quick-review` 等）から Read される共通フラグメントです。
> 各コマンドのレビュー手順内で「このファイルを Read し、以下を実施する」と指示されたら、本ファイルの内容に従ってください。
> 直接スラッシュコマンドとしては起動しません。

---

## Step A: レビュー観点ファイルの探索と読み込み

レビュー観点は **2系統** あり、両方を **プロジェクト（リポジトリ）ごとに切り替えて** 読み込む。

### A-0: プロジェクトキーの判定（git remote から導出）

git remote URL から末尾のリポジトリ名を取り出し、プロジェクトキー（`PROJECT_KEY`）として使う。例: `demae-api-shiva` → `shiva`、`demae-api-odin` → `odin`。

```bash
TOPLEVEL=$(git rev-parse --show-toplevel 2>/dev/null)
REMOTE_URL=$(git -C "${TOPLEVEL:-.}" remote get-url origin 2>/dev/null)
# 末尾のリポ名（.git 除去）
REPO_BASENAME=$(basename -s .git "${REMOTE_URL:-}")
# プレフィックス除去（demae-api-shiva → shiva, demae-api-odin → odin など）
PROJECT_KEY=$(echo "$REPO_BASENAME" | sed -E 's/^(demae-api-|demae-)//')
# 空なら toplevel ディレクトリ名を fallback として使う
[ -z "$PROJECT_KEY" ] && PROJECT_KEY=$(basename "${TOPLEVEL:-.}" | sed -E 's/^(demae-api-|demae-)//')
echo "project_key: $PROJECT_KEY"
```

以降、`review-bot-<PROJECT_KEY>.yml` と `pr-review-insights-<PROJECT_KEY>.md` を **プロジェクト専用ファイル** として優先採用する。見つからない場合は無印ファイルを fallback として使う。

### A-1: `review-bot-<key>.yml`（プロジェクト固有のコーディング規約）

以下の優先順で探索し、最初に見つかったものを Read で読み込む。

```bash
GUIDELINES="$HOME/workspace/reviews/guidelines"
for candidate in \
  "$GUIDELINES/review-bot-$PROJECT_KEY.yml" \
  "$GUIDELINES/review-bot.yml" \
  "$TOPLEVEL/review-bot.yml" \
  "$(dirname "$TOPLEVEL")/review-bot.yml"; do
  if [ -f "$candidate" ]; then RULES="$candidate"; break; fi
done
```

- `RULES` が非空 → Read で内容取得、プロジェクト固有のコーディング規約として **Step B の最優先** で適用。
- 空 → 規約ファイル無しとして続行。レビュー結果の冒頭に「プロジェクト固有規約なし（review-bot 未検出）」と明記。

### A-2: レビュー観点 md (共通 + プロジェクト別の 2 段構成)

レビュー観点は **「共通の汎用観点」+「プロジェクト固有の過去事例」** を順に読み込む。

#### A-2a: 共通観点（最初に読む）

```bash
COMMON_INSIGHTS="$GUIDELINES/pr-review-insights-common.md"
[ -f "$COMMON_INSIGHTS" ] && echo "common: $COMMON_INSIGHTS"
```

- 全プロジェクト共通の **カテゴリ別汎用観点**（Null 安全 / エラー処理 / セキュリティ / パフォーマンス 等）
- `dev_portal/scripts/generate-review-guidelines.ts --common` で再生成

#### A-2b: プロジェクト固有の過去事例（次に読む）

```bash
PROJECT_INSIGHTS="$GUIDELINES/pr-review-insights-$PROJECT_KEY.md"
[ ! -f "$PROJECT_INSIGHTS" ] && PROJECT_INSIGHTS="$GUIDELINES/pr-review-insights.md"  # 旧パス fallback
[ -f "$PROJECT_INSIGHTS" ] && echo "project: $PROJECT_INSIGHTS"
```

- 対象プロジェクトの **過去 PR レビューで実際に出た指摘事例** を集約したもの
- `dev_portal/scripts/generate-review-guidelines.ts --repo=<key>` で再生成
- 共通観点とは重複させず、プロジェクト特有の繰り返しパターンを把握するために使う
- プロジェクト専用ファイルが無い場合（新規リポジトリ等）は共通観点のみで判定

### メタ情報

レビュー結果のメタ情報には以下を残す:
- `Project: <PROJECT_KEY>`
- `AppliedRules: <review-bot ファイルの絶対パス>` または `AppliedRules: none`
- `AppliedInsights: common=<共通ファイル絶対パス>; project=<プロジェクトファイル絶対パス>`（読めなかった側は `none`）

---

## Step B: レビュー観点

`review-bot-<key>.yml` が読み込めた場合は **その内容を最優先** で適用しつつ、`pr-review-insights-<key>.md` のカテゴリ別観点と下記の汎用観点も併せてレビュー。読み込めなかった場合は汎用観点のみ。

### B.1 プロジェクト固有規約（`review-bot.yml` 由来 — 主に Cart 規約）

- **設計・アーキテクチャ**: レイヤリング違反、一方通行原則（Controller → UseCase → Service → Repository）、責務の分離、継承より移譲
- **命名・スタイル**: 命名規則、不変性（`val` / `List` 優先）、スコープ（不要 public を private に）、NULL 安全性、`!!` 禁止、暗黙の型変換禁止
- **データオブジェクト**: Entity / DTO / Request / Response の適切な使用、重複定義の禁止、`nonNull` はバリデーションで処理
- **DB 型マッピング**: `number(スケール無)` → `Long`、`number(スケール有)` → `Double`、`BigDecimal` は極力回避

> `review-bot.yml` 由来の指摘には、可能な範囲で **出典セクション名**（例: 「3.1 一方通行の原則」）を併記する。

### B.2 セキュリティ観点

- ハードコードされた秘密鍵・パスワード・API キー
- SQL インジェクション・XSS・コマンドインジェクションの可能性
- 認証・認可の不備
- 入力値検証の欠如
- 秘匿情報のログ出力・マスク漏れ

### B.3 品質観点

- エラーハンドリングの漏れ
- 非同期処理の適切な待機（async/await 漏れ、`suspend` / `runBlocking` の使い分け）
- 型安全性
- 重複コード・単純化できる処理
- テストの網羅性、適切なモック化

### B.4 パフォーマンス観点

- N+1 クエリの可能性
- 不必要なループ・重複処理
- メモリリーク要因
- キャッシュ活用の余地

---

## Step C: ラベル語彙の対応表

呼び出し元コマンドが指定する形式でラベルを採用してください。対応関係は下表のとおり。

| pr-review（GitHub 風） | quick-review（severity 風） | 意味 |
|---|---|---|
| `must`     | 🔴 Critical   | 必ず修正（バグ・セキュリティ・規約違反） |
| `should`   | 🟡 Warning    | 強く推奨（可読性・保守性の大幅改善） |
| `nit`      | 💡 Suggestion | 軽微（命名・フォーマット） |
| `question` | （該当なし — 本文中で確認） | 意図の確認 |
| `praise`   | （該当なし） | 良い実装への称賛 |

---

## Step D: 文体ルール（共通）

- 日本語で記述する
- 指摘には必ず **理由** を添える
- 可能な場合は **修正案** をコード例で示す
- 既存のレビューコメント（取得できる場合）と重複する指摘は避ける
- 指摘がない場合は、その旨を明記する
