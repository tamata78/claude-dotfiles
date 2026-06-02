# /vault-weekly-synthesis — Obsidian Weekly Synthesis

トリガー: `/vault-weekly-synthesis` または「weekly synthesis」「週次シンセシス」「週次振り返り」「週次レビュー」「週次知識棚卸し」「棚卸し」「矛盾整理して」「Be direct. Challenge me.」

## 概要

wiki/ 全体 + reports/daily/ 直近 7 件 + ideas/ 全件 + log.md 直近 7 日分を横断して 4 種類の戦略的フィードバックを生成し、MD + HTML で保存する。矛盾が検出された場合は wiki/ への merge 提案まで行う。HTML はブラウザで自動 open する。

**所要時間目安: 15 分（ユーザーのレビュー込み）**

## 手順

1. **作業前**: `$OBSIDIAN_VAULT/CLAUDE.md` を Read tool で読む（規約 + 「現在のプロジェクト」「今読んでいるもの」確認）

2. **同日スキップ判定**:
   ```bash
   WEEK=$(date +%Y-W%V)
   EXISTING="$OBSIDIAN_VAULT/reports/weekly/${WEEK}.html"
   [ -f "$EXISTING" ] && open "$EXISTING" && echo "既存の Weekly Synthesis を開きました" && exit 0
   ```

3. **直近の Daily Brief を収集**:
   - `$OBSIDIAN_VAULT/reports/daily/` の最新 7 ファイルを Read（各 50 行）

4. **wiki / ideas / log の主要箇所をサンプリング**:
   - `$OBSIDIAN_VAULT/index.md` を Read（先頭 200 行）でカテゴリ全体を把握
   - `head -200 "$OBSIDIAN_VAULT/log.md"` で直近 7 日分のアクティビティ取得
   - 直近 14d 以内に編集された wiki: `find $OBSIDIAN_VAULT/wiki -name "*.md" -mtime -14 | head -20`
   - `$OBSIDIAN_VAULT/ideas/` 全件: `ls $OBSIDIAN_VAULT/ideas/*.md 2>/dev/null`
   - 主要ページを Read（最大 15 ページ、各先頭 80 行）

5. **4 つのフィードバックを生成**:

   **EMERGING THESIS** (暫定主張):
   - この 1〜2 週間で形を取り始めているユーザーの暫定的な主張・仮説（1〜3 個）
   - 「私は〜だと考え始めている」形式で各 100 字以内
   - 根拠となる wiki ページを 2〜3 件引用

   **CONTRADICTIONS** (矛盾):
   - 過去 wiki 記述と最近の記述で食い違っている点
   - log.md と wiki/ の `confidence=low` 記述を中心に
   - 形式: `- [[wiki/xxx]] (旧) vs [[wiki/yyy]] (新): 食い違いの説明`
   - 矛盾なければ「矛盾検出なし」と明記
   - 「中断・再設計中」マークが付いた wiki ページを追跡し、矛盾する継続記述がないか確認する

   **KNOWLEDGE GAPS** (知識の空白):
   - このまま行くと判断を誤る、知識の空白を 2〜3 件
   - 特に開発中プロジェクトに対するもの
   - 形式: `- 空白の説明 → 調べるべきキーワード/方向性`

   **ONE ACTION** (来週の 1 手):
   - 来週の自分が今この瞬間に取るべき 1 手（**1 つだけ**、複数提示禁止）
   - タスクではなく「問い + 行動」の形で

6. **末尾に追加質問パート**:
   - 「率直に。私の意見にも反論してください」のスタンスでユーザーの暗黙の前提を 1 つ言語化して挑戦する

7. **矛盾解消の merge 提案**:
   - CONTRADICTIONS で矛盾が見つかった場合のみ実行
   - 「[[wiki/xxx]] と [[wiki/yyy]] を reconcile しますか？」とユーザーに確認
   - 承認されたら `/vault-ingest` のフローに準じて wiki/ を更新（merge & frontmatter 更新）

8. **MD を保存**:
   - パス: `$OBSIDIAN_VAULT/reports/weekly/YYYY-WW.md`（WW は ISO 週番号、例: `2026-W20`）
   - Write tool で作成、frontmatter 付き

9. **HTML を生成**:
   - パス: `$OBSIDIAN_VAULT/reports/weekly/YYYY-WW.html`
   - スタイル参考: `$OBSIDIAN_VAULT/wiki/claude/HTMLプレビュー生成ガイド.md` を Read
   - セクション 4 つ + 追加質問 + リンクは `obsidian://open?vault=<vault-name>&file=<encoded-path>` 形式で
   - 完了後に `Bash: open "$OBSIDIAN_VAULT/reports/weekly/${WEEK}.html"` でブラウザ起動

10. **Vault CLAUDE.md 更新提案**:
    - 「現在のプロジェクト」「今読んでいるもの」セクションの古い記述があれば更新をユーザーに提案（stale を生む元）

11. **ユーザーに提示**: 4 つのフィードバックを提示し、矛盾解消が必要な場合は確認を取る

## MD 出力フォーマット

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

## CHALLENGE

（ユーザーの暗黙の前提への挑戦 1 つ）
```

## 重要な姿勢

- **Be direct. Challenge me.** — ユーザーの意見に同意する前に反論・別視点を提示する
- **Vault の文脈で答える** — 一般論ではなく、実際に読んだ wiki の内容を根拠にする
- **reports/ のみ書く** — wiki/ への変更はユーザー確認後のみ
- **このセッションは長くなりがち** — ユーザーが「率直」を欲していることを意識して妥協しない

## 注意

- raw/ は read-only（このスキルでは読まない）
- wiki/ は確認後のみ write
- reports/weekly/ は自動 write
- 同日（同週）に既存 HTML があればスキップして既存ファイルを open

## 完了通知

```bash
~/.local/bin/vv "週次シンセシスが完成したのだ"
```
