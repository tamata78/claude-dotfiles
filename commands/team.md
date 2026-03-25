# /team - Claude Code Agent Teams ヘルプ

`claude-team` コマンドで複数のClaude Codeインスタンスをtmux分割ペインで同時起動します。

## プリセット一覧

| プリセット | 構成 | 用途 |
|:---|:---|:---|
| `simple` | 設計・実装 + Devil's Advocate | 日常開発（デフォルト） |
| `plan` | リーダー + 設計 + 設計レビュー | 設計フェーズ |
| `build` | リーダー + 実装 + テスト + コードレビュー | 実装フェーズ |
| `full-plan` | リーダー + 設計 + 設計レビュー + UIレビュー | 大規模設計 |
| `full-build` | リーダー + フロント + バック + テスト + レビュー | 大規模実装 |

## 使い方

```bash
claude-team                    # fzfメニューで選択
claude-team simple             # simpleプリセットを現在のディレクトリで起動
claude-team build ~/projects/myapp
```

## チーム必須役割

全チームに以下を必ず含めること：
- **Architect** - 全体設計・アーキテクチャの観点からレビューし、設計の整合性を担保する
- **Devil's Advocate** - 採用しようとしているアプローチの問題点・リスク・代替案を積極的に指摘する

## 設定ファイル

`~/.claude/agent-teams/presets.json` でプリセット追加、`prompts/` 配下でプロンプトカスタマイズ可能。

## 必要ツール

`tmux`, `fzf`, `python3`, `claude`（`brew install tmux fzf`）
