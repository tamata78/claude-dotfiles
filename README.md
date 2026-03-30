# claude-dotfiles

Claude Code の設定（`~/.claude/`）を集中管理するdotfilesリポジトリ。スキル・コマンド・フック・設定を共有するための基盤。

## セットアップ

```bash
bash install.sh  # シンボリックリンクを作成（冪等）
```

## 内容

| ディレクトリ | 内容 |
|---|---|
| `skills/` | カスタムスキル（feature-dev, token-audit, project-snapshot 等） |
| `commands/` | カスタムスラッシュコマンド |
| `hooks/` | PreCompact・PermissionRequest フック |
| `CLAUDE.md` | 全プロジェクト共通のグローバルルール |

## ルール

- ハードコードパス禁止（`$HOME` を使用）
- push前に `/Users/` が含まれていないか自動チェック（pre-pushフック）
- `.bak` ファイル作成禁止
