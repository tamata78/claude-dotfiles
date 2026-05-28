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

## セッション引き継ぎ
ユーザーが「前回の続き」等と明示した場合のみ `~/.claude/context/last-session.md` を読み込む。

## スナップショット参照
実装タスク開始時、`{CWD}/.claude/snapshot.md` が存在すれば読み込み「スナップショットを読み込みました」と伝える。

## コミットメッセージ
`Co-Authored-By: Claude` 行は含めない。

## トークン最適化
- サブエージェント振り分け: haiku（検索）/ sonnet（実装）/ opus（大規模設計）
- **3クエリ以上の探索・ファイル位置特定は `Explore` サブエージェントに委任**（Haiku相当・Sonnet比0.33×）。1〜2 grep 程度は直接実行。
- ファイル検索はGrepツール優先、バックグラウンド実行は `run_in_background: true` 活用

## タスク管理
- **3ステップ以上の作業は `TaskCreate` でチェックボックス管理**（Markdown タスクリスト表示で再説明コスト削減）
- 単発・自明なタスクには使わない

## コンテキスト管理
- 50%到達で `/compact` 実行。`/sandbox` で権限プロンプト削減。
- CLAUDE.md は 200 行 / 25KB 以下に保つ。超過分は `docs/` に分離し、必要時のみ `@docs/xxx.md` で読込。

## プラン完了後
計画をユーザーに提示・承認後、必ず「`/clear` を実行してから実装へ」と促す。

## Obsidian Wiki 連携
- Vault 作業時は必ず `$OBSIDIAN_VAULT/CLAUDE.md` を Read してから着手（スキル・規約・ログ扱い記載）

## 出力モード（caveman 常時 ON）
全セッションで caveman モード（full intensity）。「通常モード」「normal mode」「stop caveman」で解除。
