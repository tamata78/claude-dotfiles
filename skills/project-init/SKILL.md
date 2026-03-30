---
name: project-init
description: "新規プロジェクトに .claude/ ディレクトリ・CLAUDE.md・snapshot.md を一括セットアップするスキル。「project-init」「プロジェクトを初期化して」「.claudeを作って」などのキーワードで起動。"
---

# project-init スキル

新規プロジェクトまたは既存プロジェクトに Claude Code の設定一式を自動セットアップする。

## 実行手順

### 1. プロジェクト情報の収集

`$ARGUMENTS` にプロジェクトパスが渡されなければ、現在のディレクトリ（CWD）を対象にする。

以下を自動検出する:
- **技術スタック**: `package.json`, `requirements.txt`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml` の存在確認
- **ビルドコマンド**: `package.json` の `scripts.build` / `scripts.test` / `scripts.dev`
- **フレームワーク**: Next.js, Vite, FastAPI, Gin, Rails など
- **ポート**: `package.json` の dev/start コマンドから推測

### 2. .claude/ ディレクトリの作成

```bash
mkdir -p {プロジェクトパス}/.claude/commands
```

### 3. CLAUDE.md の生成

以下テンプレートを元に、検出情報で埋めてプロジェクト CLAUDE.md を作成:

```markdown
# {プロジェクト名}

## 技術スタック
- {検出したフレームワーク/言語}
- {主要な依存関係}

## ディレクトリ構成
```
{主要ディレクトリを ls して記載}
```

## コマンド

### 開発サーバー起動
```bash
{dev コマンド}
```

### ビルド
```bash
{build コマンド}
```

### テスト
```bash
{test コマンド}
```

### デプロイ
{デプロイ手順（わかる場合）}

## 注意事項
- {.env ファイルの有無}
- {その他プロジェクト固有の注意点}
```

### 4. snapshot.md の初期化

```markdown
# {プロジェクト名} - 開発スナップショット

## プロジェクト概要
{package.json の description または README.md の冒頭から抽出}

## 現在の状態
初期セットアップ完了。

## 最終更新
{現在日時}
```

### 5. 完了報告

作成したファイルの一覧を報告し、ユーザーに内容の確認・修正を促す。

```bash
vv "プロジェクトのセットアップが完了したのだ！"
```

### 6. dotfiles への同期確認

```
作成したファイルは claude-dotfiles には同期しません（プロジェクト固有の設定のため）。
```
