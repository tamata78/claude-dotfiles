# /vault-compress — DEPRECATED 2026-06-04

> **廃止済み**。sessions 層は reports/daily/ の OPEN_THREADS / DECISIONS / INSIGHTS セクションに吸収された。
> `/clear` 前に手動操作は不要。daily-brief が毎朝自動生成する際に前日のスレッドを引き継ぐ。

~~Vault の LLM Wiki にセッション要約を書き出し、コンテキストをクリアする準備をする。~~

## 手順

1. `~/work/MyVault/CLAUDE.md` を Read tool で読む（規約確認）
2. 現セッションから以下を抽出:
   - **決定事項**: セッション中に確定した方針・設計・選択
   - **未完了タスク**: 途中で止まっている作業・次回やること
   - **新規知見**: 発見したバグ・学んだパターン・重要情報
3. `wiki/sessions/YYYY-MM-DD-HHMM.md` を MCP (`mcp__obsidian__create-note` または `mcp__obsidian__edit-note`) で作成:

```yaml
---
tags:
  - sessions
summary: YYYY-MM-DD HH:MM セッション要約（40字以内）
related:
  - "[[関連wikiページ]]"
---

## 決定事項
- ...

## 未完了タスク
- ...

## 新規知見
- ...
```

4. `~/work/MyVault/log.md` に追記（`mcp__obsidian__edit-note` で末尾 append）:
   ```
   ## [YYYY-MM-DD] compress | session HH:MM → wiki/sessions/YYYY-MM-DD-HHMM.md
   ```
5. 関連する wiki/ ページがあれば同時 merge（新知見を永続化）
6. ユーザーに伝える: 「保存完了。`/clear` を実行してから続きを依頼してください。」

## 注意

- log.md は **append-only**。既存行を絶対に編集・削除しない
- log.md を読む時は末尾 50 行のみ（`Read` の `offset` 指定）
- session snapshot は `wiki/sessions/` 配下のみ。他フォルダに置かない
- MCP が使えない場合は Write tool で `~/work/MyVault/wiki/sessions/` に直接書く
