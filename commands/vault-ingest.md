# /vault-ingest — Obsidian Wiki 取り込み

トリガー: `/vault-ingest` または「これ取り込んで」「ingest して」「これ追加して」「wiki を作って」「wiki に書いて」「wiki に追加して」「ページを作って」「rawを一括処理して」

## モード判定

**引数なし** → **一括モード**: `raw/clipper/` と `raw/paste/` に残っている未処理ファイルを全件 wiki 化し、完了後に raw を自動削除する

**引数あり**（URL / ファイルパス / 貼付テキスト） → **単体モード**: 指定ソースを 1 件処理する

---

## 一括モード（引数なし）

### 手順

1. **作業前**: `~/work/MyVault/CLAUDE.md` を Read tool で読む（規約確認）

2. **未処理 raw を列挙**: `mcp__obsidian__search-vault` で `raw/clipper/` と `raw/paste/` を検索し、ファイル一覧を取得する
   - `wkhis-extract/` は除外（自動生成・別管理）
   - `.bak` ファイルは除外

3. **件数を報告してから処理開始**: 「○件のrawファイルを処理します」と伝える

4. **各ファイルをループ処理**（以下を 1 件ずつ繰り返す）:

   a. `mcp__obsidian__read-note` でファイル内容を読む

   b. **wiki 書込**（確認なしで即実行）:
      - 既存ページがあれば merge（`mcp__obsidian__edit-note` で append または find_and_replace）
      - 新規の場合は `mcp__obsidian__create-note` で `wiki/{category}/{title}.md` を作成
      - frontmatter 必須（tags / summary / related）
      - 本文に `出典: [[raw/xxx]]` を付与
      - **自動リンク**: 関連する wiki ページ名を `[[ページ名]]` 形式でリンク

   c. **カテゴリ別 `_index.md` 更新**: `wiki/{カテゴリ}/_index.md` に追記
      - 形式: `- [[wiki/category/title]] — 一行説明`
      - 重複チェックしてから追記

   d. **raw を即削除**: `mcp__obsidian__delete-note` で raw ファイルを削除（確認不要）

   e. **log.md に追記**: `mcp__obsidian__edit-note` (prepend)
      ```
      ## [YYYY-MM-DD] ingest | raw/xxx → wiki/yyy（新規 or merge）
      ```

5. **完了報告**: 処理件数・作成/更新した wiki ページ一覧を表示する

---

## 単体モード（引数あり）

### 手順

1. **作業前**: `~/work/MyVault/CLAUDE.md` を Read tool で読む（規約確認）

2. **ソース受取**: 入力の形式を判定
   - URL → 本文を raw テキストとして受け取る
   - ファイルパス → そのまま参照
   - 貼付テキスト → そのまま使用
   - raw/ 内の既存ファイル名 → そのファイルを読む

3. **raw に保存**（新規入力の場合のみ）: `mcp__obsidian__create-note` で以下に保存
   - URL/Web クリップ → `raw/clipper/YYYY-MM-DD-{slug}.md`
   - 貼付テキスト → `raw/paste/YYYY-MM-DD-{slug}.md`
   - PDF 参照 → `raw/pdf/YYYY-MM-DD-{slug}.md`
   
   slug: 内容を表す英数字 kebab-case（例: `llm-wiki-pattern`）

4. **wiki 書込**（確認なしで即実行）:
   - 既存ページがあれば merge（`mcp__obsidian__edit-note` で append または find_and_replace）
   - 新規の場合は `mcp__obsidian__create-note` で `wiki/{category}/{title}.md` を作成
   - frontmatter 必須（tags / summary / related）
   - 本文に `出典: [[raw/xxx]]` を付与
   - **自動リンク挿入**: 関連するwikiページ名を `[[ページ名]]` に置換（コードブロック内・既存`[[]]`はスキップ）。frontmatter の `related:` にも追記

5. **カテゴリ別 `_index.md` 更新**: `wiki/{カテゴリ}/_index.md` に追記
   - 形式: `- [[wiki/category/title]] — 一行説明`
   - 重複チェックしてから追記

6. **log.md 追記**: `mcp__obsidian__edit-note` (prepend)
   ```
   ## [YYYY-MM-DD] ingest | raw/xxx → wiki/yyy（新規 or merge）
   ```

7. **raw を削除**: `mcp__obsidian__delete-note` で raw ファイルを削除（確認不要・自動削除）

8. **wiki 内容表示**: `mcp__obsidian__read-note` で作成・更新した wiki ページを読み込み、内容をそのままユーザーに表示する

9. **完了報告**:
   - 作成・更新したページのカテゴリとパス（例: `wiki/学び/成功の法則/ページ名.md`）
   - 「Obsidian graph view で上記ページのリンクを確認してください」

---

## 注意

- log.md は **prepend（先頭追記）**。既存行を絶対に編集・削除しない
- MCP が使えない場合は Write/Edit tool で直接書く
- もくじノート（ファイル名に「もくじ」含む）は wiki/ 作成対象外（existing raw として扱う）
- `raw/wkhis-extract/` は自動生成のため処理対象外
- 一括モードでは **raw 削除は自動**。ユーザーへの確認は不要

---

## ⚠️ Ingest 時の自動矛盾チェック（破綻防止）

wiki 書込（単体モード step 4 / 一括モード step 4-b）と**並行で必ず実行**:

1. 新ソースから抽出した主要主張（claim）をリスト化
2. 各 claim について `Bash: grep -r "{キーワード}" $OBSIDIAN_VAULT/wiki/` で関連既存ページを検索
3. 既存ページの主張と **矛盾**または **更新**関係にあれば、ユーザーに以下の形式で提示:
   ```
   ⚠️ 矛盾候補: {既存ページ名} の「{既存記述}」と新ソースの「{新記述}」が食い違っています。
     - 既存: confidence={値}, last_verified={日付}
     - 新ソース: {出典}（{今日の日付}）
     どちらを採用しますか？ a) 新ソースで上書き b) 両論併記 c) 既存維持
   ```
4. ユーザー承認後に wiki を更新し、log.md に `conflict-resolved` 種別で記録:
   ```
   ## [YYYY-MM-DD] conflict-resolved | wiki/xxx ← raw/yyy（a/b/c の選択）
   ```
5. confidence は `medium` → 一致するソースが 2 件以上で `high` に昇格

一括モードでも各ファイルごとに矛盾チェックを実施（バッチでまとめずファイル単位で逐次確認）。
