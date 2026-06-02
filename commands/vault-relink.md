# /vault-relink — Obsidian Wiki 自動リリンク

トリガー: `/vault-relink` または「再リンク」「リンク張り直し」「relink」

## 概要

`wiki/` 配下の全ページを走査し、本文中に他のwikiページ名と一致する文字列があれば `[[]]` で自動リンクする。
新規ページが増えたとき、または既存ページのリンク密度が低いと感じたときに実行する。

## 引数

- `--since Nd` (例: `--since 7d`) — 直近 N 日以内に変更されたファイルのみ対象（**省略時は 7d がデフォルト**）
- `--full` — 全ページ対象（1,700+ ファイル。大量トークン消費に注意）

## 手順

1. **作業前**: `~/work/MyVault/CLAUDE.md` を Read tool で読む（規約確認）

2. **対象ファイルの特定**:
   - `--full` でなければ `Bash: find ~/work/MyVault/wiki -name "*.md" -mtime -N` で絞り込む（N はデフォルト 7）
   - `--full` の場合のみ `index.md` から全ページ取得
   - 対象ファイル数を報告し、50件を超える場合はユーザーに確認を取る
   - リンク候補名（`[[]]` に変換する語句）は `index.md` から全ページ名を参照するが、**書き換えるのは対象ファイルのみ**

3. **TF-IDF候補補強（オプション）**: `~/work/MyVault/_tools/embeddings.pkl` が存在すれば、
   対象ページに意味的に近い上位5件も `related:` 推薦候補に追加

4. **dry-run**: 以下を提示してユーザー確認を得る
   - 変更予定ページ数
   - サンプル10件（ページ名 + 挿入されるリンク）
   - 除外ルール確認（コードブロック内・URL内・既存`[[]]`は置換しない）

5. **ユーザー承認後に適用**: `mcp__obsidian__edit-note` の `find_and_replace` モードで実行
   - 置換ルール:
     - 対象: 本文テキスト（frontmatter除外、コードブロック除外、URLの中を除外）
     - `候補名` → `[[候補名]]`（すでに `[[]]` で囲まれているものはスキップ）
   - frontmatter `related:` にも対応ページを追記（重複排除、上限10件）

6. **log.md 追記**: `mcp__obsidian__edit-note` (prepend)
   ```
   ## [YYYY-MM-DD] relink | wiki/ N pages updated (since Xd)
   ```

7. 完了報告: 「Obsidian graph view でリンク密度の変化を確認してください」と伝える

## 注意

- dry-run必須。ユーザー確認なしの一括書き換え禁止
- コードブロック（``` ``` ```）内は置換しない
- URLの中（`https://...` など）に含まれるテキストは置換しない
- ファイル名が短すぎる（3文字以下）候補は誤置換リスクが高いため除外を検討
- MCP が使えない場合は `_tools/` に relink スクリプトを作成して実行
- 全1,700+件に対して一括適用する場合は先にカテゴリ単位で試すことを推奨

## TF-IDF更新

`_tools/build_embeddings.py` の対象ディレクトリを `wiki/` に変更して実行するとリンク品質が向上:
```bash
cd ~/work/MyVault/_tools && source venv/bin/activate && python build_embeddings.py
```
