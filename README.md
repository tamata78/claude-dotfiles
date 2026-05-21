# claude-dotfiles

Claude Code の設定（`~/.claude/`）を集中管理するdotfilesリポジトリ。スキル・コマンド・フック・設定を共有するための基盤。

## セットアップ

```bash
bash install.sh  # シンボリックリンクを作成（冪等）
```

## 内容

| ディレクトリ | 内容 |
|---|---|
| `skills/` | カスタムスキル（caveman, config-audit, dotfiles-sync, feature-dev, project-snapshot） |
| `commands/` | カスタムスラッシュコマンド（back-merge, cleanup, commit, create-github-release, debug, dependency-audit, morning, pr-review, project-init, quick-review, release, rpi, security-audit, team, vault-compress, vault-daily-brief, vault-ingest, vault-lint, vault-query, vault-weekly-synthesis） |
| `hooks/` | PreCompact・PermissionRequest フック |
| `CLAUDE.md` | 全プロジェクト共通のグローバルルール |

## ルール

- ハードコードパス禁止（`$HOME` を使用）
- push前に `/Users/` が含まれていないか自動チェック（pre-pushフック）
- `.bak` ファイル作成禁止
