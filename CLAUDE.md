# Global Rules

## VOICEVOX通知
- 全タスク完了・開始・エラー時に `~/.local/bin/vv "テキスト"` で音声通知（自動許可済み）
- ずんだもん口調（〜なのだ）、100文字以内、英単語はカタカナ変換

## エラー行き詰まり時
<important if="同じエラーに2回以上遭遇、またはコード修正を繰り返しても未解決の場合">
修正を中断し: 1.状況整理→報告 2.WebSearchで類似事例検索 3.公式ドキュメント確認 4.ユーザーに質問。「少し変えて再試行」は禁止。
</important>

## 実装完了時
<important if="コードの実装・修正・リファクタリング完了時">
必ずビルド＋テスト実行して成功を確認。失敗時は修正してから完了報告。
</important>

## コミットメッセージ
`Co-Authored-By: Claude` 行は含めない。

## トークン最適化
@~/.claude/docs/token-optimization.md

## タスク管理
- **3ステップ以上の作業は `TaskCreate` でチェックボックス管理**（Markdown タスクリスト表示で再説明コスト削減）
- 単発・自明なタスクには使わない

## コンテキスト管理
- 50%到達で `/compact` 実行。`/sandbox` で権限プロンプト削減。
- CLAUDE.md は 200 行 / 25KB 以下に保つ。超過分は `docs/` に分離し、必要時のみ `@docs/xxx.md` で読込。

## Mac 運用ルール（Intel 8GB / MacBook Air 2015）
- 常駐アプリは 4本まで（Obsidian・Chrome・Claude Code・Slack）。Zoom/通話時は Chrome を閉じる
- 重い探索・検索は Explore サブエージェント（Haiku）に委譲してメインを軽く保つ
- 就寝前は毎日再起動（swap/compressor リセット）

## プラン完了後
計画をユーザーに提示・承認後、必ず「`/clear` を実行してから実装へ」と促す。

## Obsidian Wiki 連携
- Vault 作業時は必ず `$OBSIDIAN_VAULT/CLAUDE.md` を Read してから着手（スキル・規約・ログ扱い記載）

## 出力モード（caveman 常時 ON）
全セッションで caveman モード（full intensity）。「通常モード」「normal mode」「stop caveman」で解除。
