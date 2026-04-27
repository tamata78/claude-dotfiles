# /vault-query — Obsidian Wiki 検索・質問

トリガー: `/vault-query <質問>` または「vault で調べて」「wiki 見て」「〜について wiki で」

## 手順

1. **作業前**: `~/work/MyVault/CLAUDE.md` を Read tool で読む（規約確認）

2. **index.md 読込**: `~/work/MyVault/index.md` を Read して候補ページを特定

3. **ページ読込**: 関連する `wiki/*.md` を Read
   - 必要なら出典 `raw/` まで辿る
   - 不足があれば `Notion/` も参照可

4. **合成・回答**:
   - 回答末尾に必ず `出典: [[wiki/xxx]], [[raw/yyy]]` を付与
   - **出力形式は質問に応じて選択**:
     - 通常質問 → markdown 本文
     - 比較・一覧 → テーブル
     - プレゼン用 → Marp スライド（`---` で区切る）
     - 数値・傾向 → matplotlib コード（ユーザーが実行）
     - 関係図 → mermaid または canvas JSON

5. **file-back 判定**: 以下の条件のいずれかを満たすなら wiki/ 保存を提案する
   - 複数ページを横断する合成回答
   - 新規の比較表・関係図・分析
   - 有意な発見・決定（後で参照する価値がある）
   
   提案文例: 「この回答を `wiki/concepts/xxx.md` として保存しますか？」

6. **保存する場合**:
   - `mcp__obsidian__create-note` で `wiki/{category}/{title}.md` を作成（frontmatter 必須）
   - `index.md` にエントリ追加
   - `log.md` に `## [日付] query | 質問概要 → wiki/xxx 新規` を追記

## 注意

- log.md は **append-only**。既存行を絶対に編集・削除しない
- 合成回答は LLM の推論結果。wiki 既存ページの内容と矛盾する場合は矛盾を明示する
- file-back は **提案**。ユーザーが不要と言えばスキップ
- query だけなら log.md 追記は不要（保存する場合のみ追記）
