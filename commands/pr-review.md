---
description: "PRのコードレビューを実行する。gh コマンドでPR差分を取得し、共有フラグメント (shared/review-rules.md) の規約・観点に従ってレビューしてコメントを投稿する"
---

# /pr-review - PRレビューワークフロー

`$ARGUMENTS` にPR番号を渡す（省略時はリスト表示して選択）。

## 手順

### 1. PRの情報取得

```bash
gh pr list                           # PR一覧（引数なし時）
gh pr view {PR番号}                  # PR詳細
gh pr diff {PR番号}                  # 差分
```

### 2. レビュー規約と観点の読み込み（共有フラグメント）

`~/.claude/shared/review-rules.md` を Read し、その指示に従って:

- Step A-0: git remote から **プロジェクトキー**（例: shiva / odin）を判定
- Step A-1: `~/workspace/reviews/guidelines/review-bot-<key>.yml` を読み込む（無ければ無印 `review-bot.yml` を fallback）
- Step A-2a: `~/workspace/reviews/guidelines/pr-review-insights-common.md` を読み込む（プロジェクト横断の汎用観点）
- Step A-2b: `~/workspace/reviews/guidelines/pr-review-insights-<key>.md` を読み込む（プロジェクト固有の過去指摘事例）
- Step B: レビュー観点（プロジェクト固有規約 / 共通汎用観点 / プロジェクト固有過去パターン / セキュリティ / 品質 / パフォーマンス）を理解する
- Step D: 文体ルールを理解する

本コマンドでは **GitHub 風ラベル**（must / should / nit / question / praise）を採用する。

### 3. コードレビュー実行

Step 2 の観点に従って PR 差分をレビューする。差分が 200 行を超える場合は `claude-team code-reviewer` への委任を提案する。

### 4. レビューコメントの作成

レビュー結果を構造化:

```
## PR #{番号} レビュー: {タイトル}

AppliedRules: <review-bot.yml の絶対パス、または "none">

### 総評
{全体的な評価}

### must（必須対応）
- {問題点}: {ファイル:行番号}
  - 理由: ...
  - 修正案: ...

### should（推奨対応）
- {改善点}: {ファイル:行番号}

### nit（軽微）
- {提案内容}

### question
- {意図確認}

### praise（良かった点）
- {良かった点}
```

### 5. GitHubへのコメント投稿（確認後）

ユーザーに確認してから:

```bash
gh pr review {PR番号} --comment --body "{レビューコメント}"
# または承認
gh pr review {PR番号} --approve --body "LGTM"
# または変更要求
gh pr review {PR番号} --request-changes --body "{コメント}"
```

### 6. 完了通知

```bash
vv "レビュー完了なのだ！"
```
