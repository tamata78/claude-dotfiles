# /vault-ingest — Obsidian Wiki 取り込み

トリガー: `/vault-ingest` または「これ取り込んで」「ingest して」「これ追加して」「wiki を作って」「wiki に書いて」「wiki に追加して」「ページを作って」

## 手順

1. **作業前**: `~/work/MyVault/CLAUDE.md` を Read tool で読む（規約確認）

2. **ソース受取**: 入力の形式を判定
   - URL → Web Clipper 未使用なら本文を raw テキストとして受け取る
   - ファイルパス → そのまま参照
   - 貼付テキスト → そのまま使用

3. **raw に保存**: `mcp__obsidian__create-note` で以下に保存
   - URL/Web クリップ → `raw/clipper/YYYY-MM-DD-{slug}.md`
   - 貼付テキスト → `raw/paste/YYYY-MM-DD-{slug}.md`
   - PDF 参照 → `raw/pdf/YYYY-MM-DD-{slug}.md`
   
   slug: 内容を表す英数字 kebab-case（例: `llm-wiki-pattern`）

4. **wiki 書込**: 確認なしで即実行
   - 既存ページがあれば merge（`mcp__obsidian__edit-note` で append または find_and_replace）
   - 新規の場合は `mcp__obsidian__create-note` で `wiki/{category}/{title}.md` を作成
   - frontmatter 必須（tags / summary / related）
   - 本文に `出典: [[raw/xxx]]` を付与
   - **自動リンク挿入**: `index.md` を Read してwikiページ名リストを取得し、本文中に出現するページ名を `[[ページ名]]` に置換（コードブロック内・既存`[[]]`はスキップ）。frontmatter の `related:` にも同リンクを追記

6. **index.md 更新**: `mcp__obsidian__edit-note` で該当カテゴリに追記
   - 既存エントリと重複しないか確認
   - 形式: `- [[wiki/category/title]] — 一行説明`

7. **log.md 追記**: `mcp__obsidian__edit-note` (append)
   ```
   ## [YYYY-MM-DD] ingest | raw/xxx → wiki/yyy（新規 or merge）
   ```

8. **raw 削除確認**: ユーザーに「raw/xxx を削除しますか？」と確認し、yes なら `mcp__obsidian__delete-note` で削除する
   - Obsidian Clipper 由来（`raw/clipper/`）の場合は削除を推奨
   - 手動貼付（`raw/paste/`）は念のため確認してから削除

9. **wiki 内容表示**: `mcp__obsidian__read-note` で作成・更新したメインの wiki ページ（raw/ や index.md ではなく `wiki/` 配下のページ）を読み込み、内容をそのままユーザーに表示する

10. 完了報告: 以下を伝える
    - 作成・更新したページのカテゴリとパス（例: `wiki/学び/成功の法則/ページ名.md`）
    - 「Obsidian graph view で上記ページのリンクを確認してください」

## 注意

- log.md は **append-only**。既存行を絶対に編集・削除しない
- MCP が使えない場合は Write/Edit tool で直接書く
- 要約を一方的に書かず、必ずユーザーと議論してから merge する
- もくじノート（ファイル名に「もくじ」含む）は wiki/ 作成対象外（existing raw として扱う）
