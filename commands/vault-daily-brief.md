# /vault-daily-brief — Obsidian Daily Brief

トリガー: `/vault-daily-brief` または「daily brief」「朝のブリーフィング」「今日の繋がりを教えて」「今日の問い」

## 概要

raw/ 直近 24h の新規ファイル + wiki/ 直近 7d の編集ファイルを横断し、3 種類のフィードバックを生成して `reports/daily/YYYY-MM-DD.md` に保存する。

## 手順

1. **作業前**: `~/work/MyVault/CLAUDE.md` を Read tool で読む（規約確認）

2. **直近 raw を特定**:
   ```bash
   find $OBSIDIAN_VAULT/raw -name "*.md" -newer "$( date -v-1d +%Y-%m-%d ).md" -not -name ".gitkeep" 2>/dev/null | head -20
   ```
   または Bash で `find $OBSIDIAN_VAULT/raw -name "*.md" -mtime -1`

3. **直近 wiki を特定**:
   ```bash
   find $OBSIDIAN_VAULT/wiki -name "*.md" -mtime -7 -not -name ".gitkeep" | head -30
   ```

4. **ファイル内容を読む**: 特定したファイルを Read tool で読む（raw は全文、wiki は先頭 100 行）

5. **3 つのフィードバックを生成**:

   **CONNECTIONS** (繋がり 3 件):
   - 直近 raw と過去 wiki ノートとの、あなたが気づいていない繋がりを 3 件
   - 各件: 原文引用（50 字以内）+ 繋がり先の wiki ページ名 + なぜ繋がるかの一文
   - 形式: `1. [[wiki/xxx]] ← "引用" → 繋がりの説明`

   **PATTERN** (テーマ 1 つ):
   - この 1 週間、ノート群から浮かび上がる暗黙のテーマを 1 つ
   - 50 字以内で言語化

   **QUESTION** (問い 1 つ):
   - PATTERN を受けて、今日 1 日抱えるべき問い 1 つ
   - タスクではなく問いの形で（「〜とは何か」「〜すべき理由は」等）

6. **reports/daily/ に保存**:
   - パス: `$OBSIDIAN_VAULT/reports/daily/YYYY-MM-DD.md`
   - Write tool で作成
   - frontmatter 付き:
     ```yaml
     ---
     tags:
       - reports/daily
     summary: YYYY-MM-DD Daily Brief
     related: []
     ---
     ```

7. **log.md に追記** (先頭に):
   ```
   ## [YYYY-MM-DD] daily-brief | reports/daily/YYYY-MM-DD.md
   ```

8. **ユーザーに提示**: 生成した 3 つのフィードバックをそのままテキストで出力する

## 出力フォーマット

```markdown
---
tags:
  - reports/daily
summary: YYYY-MM-DD Daily Brief
related: []
---

# Daily Brief — YYYY-MM-DD

## CONNECTIONS

1. [[wiki/xxx]] ← "引用文" → 繋がりの説明
2. [[wiki/yyy]] ← "引用文" → 繋がりの説明
3. [[wiki/zzz]] ← "引用文" → 繋がりの説明

## PATTERN

（この 1 週間のテーマ）

## QUESTION

（今日抱える問い）
```

## 注意

- raw/ は read-only。このスキルでは読むだけで書き込まない
- wiki/ も読むだけ（編集しない）
- reports/daily/ のみ書き込む
- 直近 raw が 0 件の場合は wiki/ 直近 7d だけで分析する
