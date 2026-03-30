---
description: "Claude Code・スキル開発に関する品質向上のヒント集（ルールではなく推奨事項）"
---

# 品質向上のヒント

- 重要なプランやコードレビューは別モデル（Codex, GPT等）でクロスレビューするとバイアスが減る
- GitHub PRで `@claude` タグを付けると Claude Code が自動レビュー・lint提案を行う
- スキルを書く際は `references/` や `scripts/` サブフォルダを活用してプログレッシブ・ディスクロージャーを実現する
