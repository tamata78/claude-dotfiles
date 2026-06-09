# /vault-weekly-synthesis — Obsidian Weekly Synthesis

トリガー: `/vault-weekly-synthesis` または「weekly synthesis」「週次シンセシス」「週次振り返り」「週次レビュー」「週次知識棚卸し」「棚卸し」「矛盾整理して」「Be direct. Challenge me.」

## 概要

wiki/ 全体 + reports/daily/ 直近 7 件 + ideas/ 全件 + log.md 直近 7 日分を横断して 5 種類の戦略的フィードバックを生成し、MD + HTML で保存する。矛盾が検出された場合は wiki/ への merge 提案まで行う。HTML はブラウザで自動 open する。

**所要時間目安: 15 分（ユーザーのレビュー込み）**

## 手順

1. **作業前**: `$OBSIDIAN_VAULT/CLAUDE.md` を Read tool で読む（規約 + 「現在のプロジェクト」「今読んでいるもの」確認）

2. **同日スキップ判定**:
   ```bash
   WEEK=$(date +%Y-W%V)
   EXISTING="$OBSIDIAN_VAULT/reports/weekly/${WEEK}.html"
   [ -f "$EXISTING" ] && open "$EXISTING" && echo "既存の Weekly Synthesis を開きました" && exit 0
   ```

3. **緘黙テーマ必読フック**:
   - 直近 daily brief / wiki の読み込み内容に「緘黙・みゆ・コンビニ・Zoom・講座」のいずれかが含まれる場合、**必ず先に** `$OBSIDIAN_VAULT/wiki/家族/子供について/場面緘黙/緘黙plan運用ルール_2026-06.md` を Read してから 5 節を書く。読まずに緘黙について書かない。
   - このファイルで答え済みの事項は KNOWLEDGE GAPS に出さない。
   - §F の二次障害サインが入力テキスト中に 1 つでも検出された場合、他の節を生成する前に ALERT 枠を最上位に出す。

4. **直近の Daily Brief を収集**:
   - `$OBSIDIAN_VAULT/reports/daily/` の最新 7 ファイルを Read（各 50 行）

5. **wiki / ideas / log の主要箇所をサンプリング**:
   - `$OBSIDIAN_VAULT/index.md` を Read（先頭 200 行）でカテゴリ全体を把握
   - `head -200 "$OBSIDIAN_VAULT/log.md"` で直近 7 日分のアクティビティ取得
   - 直近 14d 以内に編集された wiki: `find $OBSIDIAN_VAULT/wiki -name "*.md" -mtime -14 | head -20`
   - `$OBSIDIAN_VAULT/ideas/` 全件: `ls $OBSIDIAN_VAULT/ideas/*.md 2>/dev/null`
   - 主要ページを Read（最大 15 ページ、各先頭 80 行）

6. **5 つのフィードバックを生成**:

   **ALERT（§F 検出時のみ最上位に表示。該当なければ節ごと省略）**:
   - 二次障害サイン・親消耗度急上昇が入力に含まれる場合のみ記述。他の節より前に出す。

   **EMERGING THESIS（観察された傾向）**:
   - この 1〜2 週間で形を取り始めているユーザーの暫定的な傾向・気づき（1〜3 個）
   - 「今週 〜 が観察された」形式で各 100 字以内
   - 根拠となる wiki ページを 2〜3 件引用
   - OBJECTION（反論）は「運用ルールや事実と矛盾する場合のみ」生成。矛盾しない場合は省略。

   **CONTRADICTIONS（設計と実行のズレ）**:
   - 設計（plan/daily 記録）と実行記録の食い違いを 2〜3 件
   - **「達成判断保留 ≠ 失敗」を明示**。「未達」「2週連続GAP」「取れなかった」型の断罪表現は使わない。
   - 前週 ONE ACTION の未達は「まだ実施していない（理由: 〜）」として 1 行記録のみ。責めない。繰越は「同じ plan が今週も focus の場合のみ」行う。
   - 形式: `- [[wiki/xxx]] 設計: 〜 / 実行: 〜（判断保留中）`
   - 矛盾なければ「設計と実行のズレ検出なし」と明記

   **KNOWLEDGE GAPS（次に答えが分かるとよい問い）**:
   - 今後の判断に影響しうる未確認の問いを 2〜3 件
   - 運用ルールファイルで答え済みのものは出さない
   - 形式: `- 問いの説明 → 調べるべき方向性`
   - 緘黙テーマの場合: §B ステップ設計・§C モチベに基づき、「実行前に確認すべき 1 点」レベルに絞る

   **ONE ACTION（来週の小さな 1 手）**:
   - 来週の自分が今この瞬間に取るべき 1 手（**1 つだけ**、複数提示禁止）
   - 緘黙テーマの場合: §B「1要素のみ動かす」原則に従い、行動ステップ分解 1 段レベルで具体化（台詞・回数・条件まで記載）。「みゆに聞く」より「〜という状況で親が〜をする」まで落とす。

   **CHALLENGE（現状前提の再確認）**:
   - 新規の挑戦テーマを毎週生成しない
   - 緘黙テーマの場合: 運用ルール §A の前提から 1 つピックし「今週もこれで OK か？」を問うのみ
   - 他テーマの場合: CLAUDE.md 「現在のプロジェクト」との整合を確認する 1 問のみ
   - 反論は「事実または運用ルールと矛盾する場合のみ」。整合する場合は「前提は今週も有効。CHALLENGE 終了」と明記

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
   - セクション 5 つ + リンクは `obsidian://open?vault=<vault-name>&file=<encoded-path>` 形式で
   - 完了後に `Bash: open "$OBSIDIAN_VAULT/reports/weekly/${WEEK}.html"` でブラウザ起動

10. **Vault CLAUDE.md 更新提案**:
    - 「現在のプロジェクト」「今読んでいるもの」セクションの古い記述があれば更新をユーザーに提案

11. **ユーザーに提示**: 5 つのフィードバックを提示し、矛盾解消が必要な場合は確認を取る

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

> 観察→気づき→次の小さな1手。事実と運用ルールに整合する範囲で反論する。

## ALERT
（§F 二次障害サイン検出時のみ表示。該当なければこの節ごと省略）

## EMERGING THESIS

（観察された傾向 100 字以内。OBJECTION は矛盾する場合のみ）

根拠: [[wiki/xxx]], [[wiki/yyy]]

## CONTRADICTIONS

- [[wiki/xxx]] 設計: 〜 / 実行: 〜（判断保留中）

## KNOWLEDGE GAPS

1. 問いの説明 → 調べるべき方向性
2. ...

## ONE ACTION

（来週の 1 手 — 行動ステップ分解 1 段、条件・台詞・回数まで具体化）

## CHALLENGE

（現状前提の再確認 1 問のみ。整合する場合は「前提は今週も有効。CHALLENGE 終了」）
```

## 重要な姿勢

- **観察→気づき→次の小さな1手** — 反論は事実・運用ルールと矛盾する場合のみ。整合するなら同意して前に進む
- **Vault の文脈で答える** — 一般論ではなく、実際に読んだ wiki の内容を根拠にする
- **達成判断保留 ≠ 失敗** — 「未達」「取れなかった」型の断罪表現は使わない
- **reports/ のみ書く** — wiki/ への変更はユーザー確認後のみ
- **1 plan focus** — 緘黙テーマは最新 plan 1 本のみを主語にする

## 注意

- raw/ は read-only（このスキルでは読まない）
- wiki/ は確認後のみ write
- reports/weekly/ は自動 write
- 同日（同週）に既存 HTML があればスキップして既存ファイルを open

## 完了通知

```bash
~/.local/bin/vv "週次シンセシスが完成したのだ"
```
