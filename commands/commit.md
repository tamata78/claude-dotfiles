---
description: "git差分を確認してコミットメッセージを生成し、ユーザー確認後にコミットするワークフロー"
---

# /commit - インテリジェントコミットワークフロー

## 手順

### 1. 変更状態の確認

まず現在の変更を把握する:

```bash
git status
git diff --staged
git diff
```

ステージング済みの変更がなければ、変更ファイル一覧を表示して「どのファイルをステージングしますか？」と確認する。

### 2. 変更内容の分析

変更されたファイルを読んで、以下を把握する:
- 変更の種類（新機能・バグ修正・リファクタリング・設定変更など）
- 変更の意図と影響範囲
- 関連する課題番号（READMEやコメントから推測）

### 3. 秘匿情報・ローカルパスの混入チェック（必須）

コミット予定の差分に以下が含まれていないか必ず確認する。**1件でも検出したらコミットを中断し、ユーザーに報告して指示を仰ぐ**。

**秘匿情報の検出パターン**:
- APIキー / トークン: `api[_-]?key`, `secret`, `token`, `bearer`, `password`, `passwd`, `pwd`
- AWS: `AKIA[0-9A-Z]{16}`, `aws_secret_access_key`
- 一般的なシークレット形式: `-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----`, `sk-[a-zA-Z0-9]{20,}`, `ghp_[a-zA-Z0-9]{36}`, `xox[baprs]-[a-zA-Z0-9-]+`
- 環境ファイル: `.env`, `.env.local`, `credentials.json`, `*.pem`, `*.key` の新規追加

**ローカルパスの検出パターン**:
- ユーザーホーム配下: `/Users/<username>/`, `/home/<username>/`, `C:\\Users\\<username>\\`
- 環境変数で表現すべきもの: 自分のワークスペース絶対パス（例: `/Users/shuta.tezuka/workspace/...`）
- 他人と共有できない端末固有のパス

**チェックコマンド例**:

```bash
# 秘匿情報の簡易スキャン
git diff --staged | grep -iE "(api[_-]?key|secret|token|password|bearer|AKIA[0-9A-Z]{16}|-----BEGIN.*PRIVATE KEY-----|sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36})"

# ローカルパスのスキャン
git diff --staged | grep -E "(/Users/|/home/[a-z]+/|C:\\\\Users\\\\)"

# 危険ファイルの新規追加チェック
git diff --staged --name-only --diff-filter=A | grep -E "(\.env(\.|$)|credentials\.json|\.pem$|\.key$|id_rsa|id_ed25519)"
```

検出時は以下を提示:
- 該当ファイル名・行番号・該当文字列（マスクして表示）
- 想定される対処（`.gitignore` に追加 / 環境変数化 / 該当行削除など）

問題がなければ次のステップへ。

### 4. コミットメッセージの生成

以下のフォーマットでコミットメッセージを提案する:

```
<type>: <概要（50文字以内）>

<詳細説明（任意）>
```

typeの例: feat, fix, refactor, docs, chore, test, style

**日本語・英語はプロジェクトの既存コミット履歴に合わせること**。

`git log --oneline -5` で確認してから提案する。

### 5. ユーザー確認

提案したコミットメッセージを表示し、以下を確認:
- 「このメッセージでコミットしますか？」
- 「修正が必要な場合は修正内容を教えてください」

### 6. コミット実行

承認されたら実行:

```bash
git add -p  # または指定されたファイルを git add
git commit -m "<承認されたメッセージ>"
```

コミット完了後に `git log --oneline -3` で確認して報告する。

### 7. 完了通知

```bash
vv "コミット完了なのだ！"
```
