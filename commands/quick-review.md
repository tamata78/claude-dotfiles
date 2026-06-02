---
use: work
description: "ローカル変更（unstaged + staged + 未push commit）をコードレビューする（共有フラグメント shared/review-rules.md を参照）"
---

# /quick-review - クイックコードレビュー

`$ARGUMENTS` にファイルパスやPR番号を指定できる。省略時は **ローカル変更すべて**（unstaged + staged + 未push commit）をレビュー対象とする。

## 手順

### 1. レビュー対象の取得

`$ARGUMENTS` の値で対象を切り替える:

#### 引数なし（デフォルト）— ローカル変更すべて

`git add` していない変更も含めて、push 前のローカル変更を網羅的にレビューする。

```bash
# 変更概要を把握
git status --porcelain

# 1) Untracked ファイル（git add 前の新規ファイル）— 一覧表示
git ls-files --others --exclude-standard

# 2) Unstaged 差分（変更したがまだ git add していない既存ファイル）
git diff

# 3) Staged 差分（git add 済みでまだ commit していない変更）
git diff --staged

# 4) Local commit（commit 済みでまだ push していない変更）
#    upstream がある場合のみ
git log @{upstream}..HEAD --oneline 2>/dev/null
git diff @{upstream}..HEAD 2>/dev/null
```

- Untracked ファイルは `Read` ツールで個別に内容を読んでレビューする（`git diff` には現れないため見落としやすい）
- 3 つの diff と Untracked を **同じレビュー観点で一括評価** し、出力時にそれぞれどの状態か明示する

#### 引数: ファイルパス

`$ARGUMENTS` が既存ファイルパスを指す場合、そのファイル全体をレビューする（`Read` で読む）。

#### 引数: PR 番号

`$ARGUMENTS` が PR 番号の場合は **`/pr-review` の使用を促す**（quick-review は手元のローカル変更を対象とする想定のため）。

### 2. レビュー規約と観点の読み込み（共有フラグメント）

`~/.claude/shared/review-rules.md` を Read し、その指示に従って:

- Step A-0: git remote から **プロジェクトキー**（例: shiva / odin）を判定
- Step A-1: `~/workspace/reviews/guidelines/review-bot-<key>.yml` を読み込む（無ければ無印 `review-bot.yml` を fallback）
- Step A-2a: `~/workspace/reviews/guidelines/pr-review-insights-common.md` を読み込む（プロジェクト横断の汎用観点）
- Step A-2b: `~/workspace/reviews/guidelines/pr-review-insights-<key>.md` を読み込む（プロジェクト固有の過去指摘事例）
- Step B: レビュー観点（プロジェクト固有規約 / 共通汎用観点 / プロジェクト固有過去パターン / セキュリティ / 品質 / パフォーマンス）を理解する
- Step D: 文体ルール（理由・修正案提示・既存指摘との重複回避）を理解する

### 3. レビュー実行

Step 1 のレビュー対象に対し、Step 2 で読み込んだ観点でレビューする。
本コマンドでは **severity 風ラベル**（🔴 Critical / 🟡 Warning / 💡 Suggestion）を採用する（共有フラグメント Step C の対応表を参照）。

### 4. レビュー結果の報告

以下のフォーマットで報告:

```
## コードレビュー結果

AppliedRules: <review-bot.yml の絶対パス、または "none">

### 🔴 Critical（必ず修正）
- [問題の説明] (ファイル:行番号)
  - 理由: ...
  - 修正案: ...

### 🟡 Warning（修正推奨）
- [問題の説明] (ファイル:行番号)

### 💡 Suggestion（改善提案）
- [提案内容] (ファイル:行番号)

### ✅ 問題なし
特に問題は見つかりませんでした。
```

- `review-bot.yml` 由来の指摘には、可能な範囲で出典セクション名（例: 「3.1 一方通行の原則」）を併記する。
- Critical がある場合は「修正しますか？」と確認し、承認されれば修正まで実施する。

### 5. 成果物の出力（必須・両方とも作成）

レビュー結果は **必ず 2 種類の成果物を作成** すること:

#### 5-A. Markdown（永続記録、`~/workspace/reviews/` に保存）

ファイル名規約: `<repo>-quick-review-<YYYY-MM-DD>-<branch-slug>.md`

- `<repo>`: git remote から取得（例: `demae-api-odin`）
- `<branch-slug>`: 現ブランチ名（`/` は `-` に置換不要、そのままでもよいが扱いやすければスラッシュ部のみ採用。例: `DEMAE-48733_au_pay_cancel`）
- 同名既存ファイルがあれば上書きで構わない（同じブランチの再レビューは履歴上書きで OK）
- 先頭に YAML 風メタヘッダ:
  ```
  ---
  Repo: <repo>
  Branch: <branch>
  Mode: quick-review (local changes)
  Reviewed: <YYYY-MM-DD>
  Project: <PROJECT_KEY>
  AppliedRules: <絶対パス | none>
  AppliedInsights:
    common: <絶対パス | none>
    project: <絶対パス | none>
  Targets:
    - modified (unstaged): [...]
    - staged: [...]
    - untracked: [...]
    - local commit: [...]
  ---
  ```
- 本文は Step 4 のフォーマット（Critical / Warning / Suggestion / 良い点）に従う。

#### 5-B. HTML（ブラウザ表示用、`/tmp/` に保存）

ファイル名: `/tmp/quick-review-<YYYYMMDD-HHMMSS>.html`

HTML 組み立て制約:
- **白基調固定**（メモリ `feedback_html_preview_background.md` 準拠）— ダークモード自動切替なし。`background: #ffffff; color: #1a1a1a;`
- メタ情報（Project / AppliedRules / AppliedInsights / 対象ファイル一覧 / Critical・Warning・Suggestion 件数）を先頭に表示
- 重要度別セクション（🔴 / 🟡 / 💡 / ✅）に分けて指摘を列挙
- 各指摘は ファイル:行番号 / 理由 / 修正案コード例 を含める
- 修正案は `<pre><code>` で整形（シンタックスハイライト用ライブラリは入れない）
- 末尾に対応する Markdown ファイル絶対パスを fine print で添える

最後に `open <html_path>` で macOS のデフォルトブラウザを起動。

#### 5-C. チャットへの出力

チャット側は **短いサマリのみ**:
- HTML ファイルパス
- Markdown ファイルパス
- 件数（例: 「Critical 0 / Warning 3 / Suggestion 5」）
- Critical があれば修正可否の確認

### 6. 完了通知

```bash
vv "レビュー完了なのだ！"
```
