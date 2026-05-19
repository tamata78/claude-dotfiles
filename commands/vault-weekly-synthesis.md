# /vault-weekly-synthesis — Obsidian Weekly Synthesis

トリガー: `/vault-weekly-synthesis` または「weekly synthesis」「週次振り返り」「週次知識棚卸し」「矛盾整理して」「Be direct. Challenge me.」

## 概要

wiki/ 全体 + reports/daily/ 直近 7 件を横断して 4 種類の戦略的フィードバックを生成し、`reports/weekly/YYYY-WW.md` に保存する。矛盾が検出された場合は wiki/ への merge 提案まで行う。

**所要時間目安: 15 分（ユーザーのレビュー込み）**

## 手順

1. **作業前**: `~/work/MyVault/CLAUDE.md` を Read tool で読む（規約確認）

2. **直近の Daily Brief を収集**:
   - `reports/daily/` の最新 7 ファイルを Read（各 50 行）

3. **wiki/ の主要ページをサンプリング**:
   - `index.md` を Read（先頭 200 行）でカテゴリ全体を把握
   - 直近 14d 以内に編集されたページ: `find $OBSIDIAN_VAULT/wiki -name "*.md" -mtime -14 | head -20`
   - サンプリングした wiki ページを Read（各先頭 80 行）

4. **4 つのフィードバックを生成**:

   **EMERGING THESIS** (暫定主張):
   - この 1〜2 週間で形を取り始めているあなたの暫定的な主張・仮説
   - 「私は〜だと考え始めている」形式で 100 字以内
   - 根拠となる wiki ページを 2〜3 件引用

   **CONTRADICTIONS** (矛盾):
   - 過去の wiki 記述と最近の記述で食い違っている点
   - 形式: `- [[wiki/xxx]] (旧) vs [[wiki/yyy]] (新): 食い違いの説明`
   - 矛盾なければ「矛盾検出なし」と明記

   **KNOWLEDGE GAPS** (知識の空白):
   - このまま行くと判断を誤る、知識の空白を 2〜3 件
   - 形式: `- 空白の説明 → 調べるべきキーワード/方向性`

   **ONE ACTION** (来週の 1 手):
   - 来週の自分が今この瞬間に取るべき 1 手
   - タスクではなく「問い + 行動」の形で

5. **矛盾解消の merge 提案**:
   - CONTRADICTIONS で矛盾が見つかった場合のみ実行
   - 「[[wiki/xxx]] と [[wiki/yyy]] を reconcile しますか？」とユーザーに確認
   - 承認されたら `/vault-ingest` のフローに準じて wiki/ を更新（merge & frontmatter 更新）

6. **reports/weekly/ に保存**:
   - パス: `$OBSIDIAN_VAULT/reports/weekly/YYYY-WW.md`
   - Write tool で作成（WW は ISO 週番号、例: `2026-W20`）
   - frontmatter 付き

7. **log.md に追記** (先頭に):
   ```
   ## [YYYY-MM-DD] weekly-synthesis | reports/weekly/YYYY-WW.md
   ```

8. **ユーザーに提示**: 4 つのフィードバックを提示し、矛盾解消が必要な場合は確認を取る

## 出力フォーマット

```markdown
---
tags:
  - reports/weekly
summary: YYYY-WW Weekly Synthesis
related:
  - "[[wiki/関連ページ]]"
---

# Weekly Synthesis — YYYY-WW

> Be direct. Challenge me. 私の意見にも反論してください。

## EMERGING THESIS

（暫定主張 100 字以内）

根拠: [[wiki/xxx]], [[wiki/yyy]]

## CONTRADICTIONS

- [[wiki/xxx]] (旧) vs [[wiki/yyy]] (新): 食い違いの説明

## KNOWLEDGE GAPS

1. 空白の説明 → 調べるべき方向性
2. ...

## ONE ACTION

（来週取るべき 1 手 — 問い + 行動）
```

## 重要な姿勢

- **Be direct. Challenge me.** — ユーザーの意見に同意する前に反論・別視点を提示する
- **Vault の文脈で答える** — 一般論ではなく、実際に読んだ wiki の内容を根拠にする
- **reports/ のみ書く** — wiki/ への変更はユーザー確認後のみ

## 注意

- raw/ は read-only（このスキルでは読まない）
- wiki/ は確認後のみ write
- reports/weekly/ は自動 write
