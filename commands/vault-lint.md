# /vault-lint — Obsidian Wiki 健康診断

トリガー: `/vault-lint` または「lint して」「vault の健康診断」「矛盾チェック」

## 手順

1. **作業前**: `~/work/MyVault/CLAUDE.md` を Read tool で読む（規約確認）

2. **機械 lint 実行**:
   ```bash
   cd ~/work/MyVault/_tools && source venv/bin/activate && python lint_wiki.py
   ```
   出力を読んで issue 一覧を取得。

3. **意味 lint（LLM チェック）**:
   以下を実行:

   a. **矛盾検出**: wiki/ からランダム 5 ページを Read して本文を比較。相互矛盾する記述を探す。

   b. **概念欠落検出**: `index.md` + wiki/ 全ページ本文に登場する人物名・概念・用語を抽出し、独立したページが存在しないものをリストアップ（言及はあるがページ無し）。

   c. **陳腐化検出**: 30 日以上更新の無い非 session ページを `find` で特定し、「古い可能性あり」としてフラグ立て。

   d. **リンク密度チェック**: wiki/ で outbound wikilink（本文中の `[[]]`）が 1 個以下のページを抽出。HIGH: 0個（orphan）、MEDIUM: 1個（低密度）。MEDIUM以上なら `/vault-relink` 実行を推奨。

4. **レポート出力**: 優先度別に整理して報告

   ```
   ## Wiki Lint Report YYYY-MM-DD

   ### HIGH（要修正）
   - [矛盾] wiki/xxx と wiki/yyy の主張が矛盾: ...

   ### MEDIUM（改善推奨）
   - [概念欠落] 「時間単価」への言及が 3 ページにあるが独立ページ無し → wiki/concepts/時間単価.md の作成を推奨
   - [orphan] wiki/yyy はどのページからもリンクされていない

   ### LOW（参考）
   - [陳腐化候補] wiki/zzz は 45 日更新無し

   機械 lint: X issues
   意味 lint: Y issues
   合計: Z issues
   ```

5. **月次ローテ提案**: 今月が前回 rotate から 30 日以上経過していれば提案
   ```
   月次 log ローテを実行しますか？
   → 承認後: python lint_wiki.py --rotate
   ```

## 注意

- 意味 lint はランダムサンプリング（5 ページ）。全文走査は行わない
- lint report はユーザーへの提案のみ。自動修正は行わない
- ユーザーが修正を依頼した場合のみ該当ページを編集する
