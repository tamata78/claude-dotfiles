# claude-dotfiles

Claude Code (`~/.claude/`) の設定を管理する dotfiles リポジトリ。
シンボリックリンク方式で各マシンに展開し、設定を一元管理する。

## 管理対象の設定

| カテゴリ | パス | 説明 |
|---------|------|------|
| グローバルルール | `CLAUDE.md` | 全プロジェクト共通の Claude 動作ルール |
| 設定 | `settings.json` | Claude Code のベース設定（hooks・MCP 等） |
| 音声通知 | `voicevox-scripts.md` | VOICEVOX 通知スクリプト集 |
| コマンド | `commands/` | スラッシュコマンド定義 |
| フック | `hooks/` | PreCompact・PermissionRequest 等のフックスクリプト |
| スクリプト | `scripts/` | ユーティリティスクリプト |
| スキル | `skills/` | Claude Code スキル定義 |
| エージェントチーム | `agent-teams/` | マルチエージェント設定 |
| Git フック | `git-hooks/` | 全プロジェクト共通 Git フック |

### 収録スキル

| スキル | 説明 |
|--------|------|
| `claude-md-improver` | CLAUDE.md のレビュー・改善提案 |
| `dotfiles-sync` | `~/.claude/` の変更を本リポジトリに同期 |
| `feature-dev` | 設計→実装→ビルド→テストのワークフロー |
| `project-snapshot` | プロジェクトの開発知見・状態をファイルに保存 |
| `prompt-review` | プロンプトのレビュー |
| `token-audit` | Claude Code のトークン消費を監査・削減提案 |

### 収録コマンド

| コマンド | 説明 |
|---------|------|
| `review-rules` | ルール・スキル棚卸し |
| `team` | Claude Code Agent Teams ヘルプ |

## 利用する際の注意点

### セキュリティ

- **APIキー・トークンは含めない** — `settings.local.json` はこのリポジトリに含まれないため、シークレット類はそちらに記載する
- **ローカルパスは含めない** — `/Users/username` 等のハードコードパスは `$HOME` で表現する（`dotfiles-sync` スキルが自動チェック）
- **個人・業務情報は含めない** — `memory/`・`projects/`・個人用コマンドは管理対象外
- **公開リポジトリで管理する場合** — 業務固有の情報（社内サービス名・プロジェクト名等）が含まれていないか確認する

### マシン固有の設定

`~/.claude/settings.local.json` にマシン固有の設定（パス・権限等）を記述する。このファイルは本リポジトリで管理しない。

## 導入手順

### 1. リポジトリをクローン

```bash
git clone <このリポジトリのURL> ~/work/claude-dotfiles
```

### 2. インストールスクリプトを実行

```bash
cd ~/work/claude-dotfiles
bash install.sh
```

`~/.claude/` 配下に各ファイルへのシンボリックリンクが作成される。
既存ファイルは `.bak` にバックアップされる。

### 3. マシン固有設定を作成（必要に応じて）

```bash
# 例: パス固有の権限設定など
touch ~/.claude/settings.local.json
```

### 4. VOICEVOX を使う場合

デフォルトスピーカーを設定する：

```bash
echo '{"speaker": 3}' > ~/.vv_speaker  # 3=ずんだもん
```

## 設定の同期方法

`~/.claude/` に新しいファイルを追加した際は、Claude Code 上で以下のように依頼する：

```
dotfilesに反映して
```

`dotfiles-sync` スキルが自動的に：
1. 新規・未管理ファイルを検出
2. 共通／プライベートに分類
3. ポータビリティチェック（ローカルパス・秘匿情報）
4. dotfiles にコピー → シンボリックリンク化
5. `install.sh` を更新
6. git コミット
7. Dev Portal のデータを更新（`npm run sync`）

## ファイル構成

```
claude-dotfiles/
├── install.sh              # セットアップスクリプト（冪等）
├── README.md               # このファイル
├── CLAUDE.md               # グローバルルール
├── settings.json           # Claude Code ベース設定
├── voicevox-scripts.md     # VOICEVOX 通知スクリプト集
├── commands/               # スラッシュコマンド
├── hooks/                  # フックスクリプト
├── scripts/                # ユーティリティスクリプト
├── skills/                 # スキル定義
├── agent-teams/            # エージェントチーム設定
└── git-hooks/              # 全プロジェクト共通 Git フック
```
