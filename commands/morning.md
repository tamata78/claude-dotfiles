---
description: "朝のルーティン自動化。自分オーナーの作業（進行中の実装・自分のPR・担当チケット）を優先課題TOP3に、他人PRレビュー依頼は別枠で表示。学習トピックは復習・深掘り・メモ化のみ。引数: --ratio 80:20。"
---

# /morning - 朝の優先課題＋学習タスク提案

起動時に引数を確認する。`--ratio` が指定されていれば `仕事:学習 = 指定値` を使い、なければデフォルト `70:30` を使う。

---

## Step 1. 引き継ぎ・コンテキスト復元

`~/.claude/context/last-session.md` を Read する。ファイルが存在しない場合はスキップ。

---

## Step 2. データ収集（並列実行）

以下を **すべて同時に** Bash で実行し、結果を保持する。

### 2-A. 全リポジトリの git 状態

```bash
for d in ~/workspace/*/; do
  if [ -d "$d/.git" ]; then
    (cd "$d" && echo "=== $(basename $d) ===" && git status -sb 2>/dev/null && git log --oneline -3 2>/dev/null)
  fi
done
```

### 2-B. GitHub PR 一覧（自分の open PR + 自分宛レビュー依頼）

GitHub ホスト（github.com）のリポジトリだけを対象にする。Bitbucket は除外。

```bash
# 自分のオープン PR
gh pr list --author @me --state open \
  --json number,title,url,updatedAt,reviewDecision,repository \
  --limit 20 2>/dev/null

# 自分宛レビュー依頼（review-requested）
gh search prs --review-requested @me --state open \
  --json number,title,url,updatedAt,repository \
  --limit 10 2>/dev/null
```

### 2-C. アクティブチケット

`~/.claude/projects/-Users-shuta-tezuka-workspace/memory/project_active_tickets.md` を Read する。

### 2-D. プロジェクトスナップショット

```bash
find ~/workspace -maxdepth 3 -path '*/.claude/snapshot.md' -mtime -14 -type f 2>/dev/null
```

見つかったファイルを Read し、各プロジェクトの「次のTODO」「現在の状態」セクションを抽出する。

### 2-E. Obsidian Vault — 最近ログ

```bash
head -50 "$OBSIDIAN_VAULT/log.md" 2>/dev/null
```

最近の ingest / query / daily-brief 操作を把握する（CLAUDE.md ルール: 全文 Read 禁止、先頭50行のみ）。

### 2-F. Obsidian Vault — 直近ブリーフの PATTERN / QUESTION

```bash
LATEST=$(ls -t "$OBSIDIAN_VAULT/reports/daily/"*.html 2>/dev/null | head -1)
[ -n "$LATEST" ] && grep -m5 -E "(PATTERN|QUESTION|<h2)" "$LATEST" 2>/dev/null
```

全文 Read 禁止。見出し行と PATTERN/QUESTION 行のみ抽出。

### 2-G. Obsidian Vault — 関心トピック（直近7日）

```bash
find "$OBSIDIAN_VAULT/ideas" "$OBSIDIAN_VAULT/wiki" -name '*.md' -mtime -7 -type f 2>/dev/null | head -20
```

ファイル名一覧のみ取得。中身の Read は不要。

### 2-H. 学習復習候補

```bash
# confidence: low のページ
grep -rl "confidence: low" "$OBSIDIAN_VAULT/wiki/" 2>/dev/null | head -5

# last_verified が 2024-2025 年のページ（60日以上前相当）
grep -rl "last_verified:" "$OBSIDIAN_VAULT/wiki/" 2>/dev/null \
  | xargs grep -l "last_verified: 202[45]" 2>/dev/null | head -5
```

### 2-I. 現在進行中の作業検出（P0 候補）

各リポジトリで「feature/bugfix/fix/hotfix ブランチ + 直近7日コミットあり」のものを抽出する。
これが **TOP3 の最優先候補（P0）** になる。

```bash
for d in ~/workspace/*/; do
  if [ -d "$d/.git" ]; then
    (cd "$d" && \
      BRANCH=$(git branch --show-current 2>/dev/null) && \
      if echo "$BRANCH" | grep -qE '^(feature|bugfix|fix|hotfix)/'; then
        RECENT=$(git log --since='7 days ago' --oneline -5 2>/dev/null)
        if [ -n "$RECENT" ]; then
          echo "=== ACTIVE: $(basename $d) | $BRANCH ==="
          echo "$RECENT"
          # チケット番号抽出
          echo "$BRANCH" | grep -oE 'DEMAE-[0-9]+' | head -1
          # レビュー指摘反映フラグ
          echo "$RECENT" | grep -qE 'fix|Fix|refactor|Refactor|review|レビュー' \
            && echo "FLAG: review-iteration"
        fi
      fi
    )
  fi
done
```

---

## Step 3. 統合・優先度付け

収集結果を統合して以下を構築する。

### 除外フィルタ（最初に適用）

以下は TOP3 / 学習トピックの **両方** から除外する:

| 除外対象 | 検出方法 |
|---|---|
| **他人がオーナーの PR** | `gh search prs --review-requested @me` の結果は自分が author でないので TOP3 候補から外す（別枠「📋 参考: 自分宛レビュー依頼」で件数のみ表示） |
| **`[保留]` `[後回し]` `[BLOCKED]` マークの TODO** | `.claude/snapshot.md` の TODO 行に上記文字列が含まれるもの。別枠「🔧 保留中」で一覧表示 |
| **自発的に立ち上げた改善タスク** | チケット・PR・snapshot のいずれにも紐付かない CI改善・依存更新・リファクタ・ドキュメント整備等。**仕事 / 学習どちらにも入れない** |
| **期限切れの古いチケットメモ** | `project_active_tickets.md` の mtime が 30 日以上前で、かつ記載日付も過去 → 警告のみ、優先度には反映しない |

### 優先課題スコアリング（高い順 = TOP3 候補）

| Pri | 種類 | 検出方法 | スコア |
|---|---|---|---|
| **P0 最優先** | 現在進行中の自分の実装・レビュー指摘反映 | 2-I で `=== ACTIVE: ===` が出たリポジトリ。`FLAG: review-iteration` ならさらにブースト | 100 |
| **P1 高** | 自分が author の open PR でレビュー待ち | 2-B の `gh pr list --author @me` で `reviewDecision == REVIEW_REQUIRED` | 80 |
| **P2 高** | 自分担当チケットで期限が近い（残30日以内） | 2-C のチケット日付 + 残日数。ブランチ名のチケット番号と一致すれば 2-I で既に P0 化されているはず | 70 |
| **P3 中** | 自分の open PR で 7日以上放置 | 2-B の `gh pr list --author @me` で `updatedAt` が7日以上前 | 50 |
| **P4 低** | snapshot.md の「次のアクション」（保留マーク無し） | 2-D の `## 🎯 次のアクション` セクション、`[保留]` 等が無いもの | 30 |

**重要なルール:**
- 自分が author でない PR（= 単なる reviewer）は **絶対に TOP3 に入れない**
- 他人 PR のレビュー依頼は緊急度に関わらず別枠表示
- 同スコアの場合: P0 内では「`FLAG: review-iteration` あり」を優先 → 直近コミットが新しいものを優先

### 学習トピック選出（1〜2件）

候補は以下の **3カテゴリのみ**:

1. **[復習]** `wiki/dev/` で `confidence: low` または `last_verified` が 60日以上前のページ
2. **[深掘り]** `ideas/` 直近7日の自分のメモ
3. **[メモ化]** 過去の Daily Brief / Weekly Synthesis で生成された QUESTION への自分なりの回答を `ideas/` に書く

**学習に含めないもの（重要）:**
- 自発的な改善タスク（CI改善・依存更新・リファクタ等）
- 「30分でできる」「未適用」など完了寄りのチケット風タスク
- → これらは学習ではなく「保留中の改善案」。本人が必要と判断したときに別途チケット化する

候補がなければ「今日 `ideas/` に新しいメモを書く」を提案する。

### 時間ブロック割り当て

`--ratio` 引数を解析する（例: `80:20` → 仕事80%, 学習20%）。デフォルトは `70:30`。
標準作業時間 09:30〜18:00（実質7時間）で比率に応じてブロックを割り当てる。

**70:30 デフォルト（仕事5h、学習2h）:**
```
09:30-10:30  ⚙️  優先課題1
10:30-11:00  📚  学習1
11:00-12:00  ⚙️  優先課題2
13:00-14:00  📚  学習2（または深掘り）
14:00-17:00  ⚙️  優先課題3
17:00-17:30  📝  振り返り・snapshot 更新
```

**80:20 の場合（仕事5.5h、学習1.5h）:**
```
09:30-10:30  ⚙️  優先課題1
10:30-12:00  ⚙️  優先課題2
13:00-14:30  📚  学習（まとめて）
14:30-17:30  ⚙️  優先課題3
17:30-18:00  📝  振り返り
```

---

## Step 4. 出力（Markdown で表示）

```
☀️ おはようございます — YYYY-MM-DD (曜日)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 優先課題 TOP3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. [P0 進行中] [DEMAE-XXXXX] タイトル
     → ブランチ feature/DEMAE-XXXXX_xxx でレビュー指摘反映中（直近コミット: N時間前）
     → リポジトリ: xxx

  2. [P1 自分PR] PR #123 (demae-api-odin) タイトル
     → 自分がauthor、reviewDecision = REVIEW_REQUIRED (更新: N日前)

  3. [P2 チケット期限] [DEMAE-XXXXX] タイトル
     → リリースまで残N日

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 学習トピック
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  - [復習]   wiki/dev/.../ページ名.md (last_verified 2025-XX-XX)
  - [深掘り] ideas/最近の気づきファイル.md
  - [メモ化] 昨日のQUESTIONへの回答を ideas/ に書く

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 今日のスケジュール（仕事 70 / 学習 30）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  09:30-12:00  ⚙️  優先課題1（P0 進行中の実装）
  13:00-14:00  📚  学習1
  14:00-17:00  ⚙️  優先課題2 / 3
  17:00-17:30  📝  振り返り・snapshot 更新

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 参考: 自分宛レビュー依頼（N件）  ※TOP3 とは独立、手が空いたら確認
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  - #598 (demae-api-odin) MySQL Repository for Apple Pay (33日前)
  - #612 (demae-api-odin) PayPay CancelUseCase (5日前)
  - ... 全件リンクのみ列挙

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 保留中（M件）  ※snapshot で [保留] マーク
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  - [保留] buf BSR レート制限対策 CI 適用
  - ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 引き継ぎメモ（last-session.md）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ※ファイルがあれば要点のみ3行以内で要約。なければ「（なし）」。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 リポジトリ状態サマリー
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  変更あり: リポジトリ名（未コミットN件）、...
  クリーン:  リポジトリ名、...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💭 Phase 2 連動（第二の脳 振り返りループ）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  デイリーブリーフ → 過去 wiki との CONNECTIONS / PATTERN / QUESTION を生成
  → 「デイリーブリーフを実行して」と入力
  ※ 月曜日の場合: 「週次シンセシスを実行して」も推奨
```

---

## Step 4.5. HTML 出力（ブラウザ表示）

ターミナル Markdown 出力に加えて、HTML レポートを生成して **ブラウザで自動 open** する。Daily Brief の体裁を踏襲しつつ、朝のルーティンを示すため **オレンジ系グラデーション**（`linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)`）で差別化する。

### 出力先

```
$OBSIDIAN_VAULT/reports/morning/YYYY-MM-DD.html
```

ディレクトリが無ければ `mkdir -p` で作成。同日に既存ファイルがあれば **上書き**（Daily Brief は同日スキップだが morning は同日複数回実行ありうる）。

### 必須要素（参考: `$OBSIDIAN_VAULT/reports/daily/2026-05-21.html` のスタイル骨格を流用）

- ヘッダー（オレンジグラデーション）+ 日付 + 曜日 + 🎯 今日の比率（仕事:学習）
- セクション（カード型・白背景・角丸 10px・薄い shadow）:
  - 🎯 優先課題 TOP3 — 各課題を `<details>` 折りたたみ。番号丸チップ（オレンジ #f59e0b）+ タイトル + サブタイトル + 詳細 body（リポジトリ / ブランチ / 直近コミット / plan ファイル / コマンド）
  - 📚 学習トピック — 緑系の section-label。[復習] / [深掘り] / [メモ化] をバッジ表示
  - 📅 今日のスケジュール — タイムテーブル（時間ブロックを左カラム、内容を右カラム）。仕事ブロックはオレンジ、学習は緑、振り返りは紫の左ボーダー
  - 📋 自分宛レビュー依頼 — リンク付きリスト。★関連性高 マークは赤バッジ
  - 🔧 保留中 — グレーアウト表示
  - 📝 引き継ぎメモ — 灰色 blockquote
  - 🌐 リポジトリ状態サマリー — 「変更あり / クリーン」を 2 カラム
  - 💭 Phase 2 連動 — 紫系の section、リンク（Daily Brief HTML）
- フッター: `Generated by /morning — YYYY-MM-DD HH:MM`

### リンクの形式

ファイル参照は `obsidian://open?vault=t-valt&file=<encoded-path>` 形式。PR は GitHub URL 直リンク。プランファイルは `file://` プロトコルでローカル展開。

### スタイル参考

- 基本骨格（カード / details / blockquote / tag）: `$OBSIDIAN_VAULT/reports/daily/2026-05-21.html`
- 配色のみ変更:
  - グラデーション: `#f59e0b → #ef4444`
  - section-label 優先課題: `background: #fff3e0; color: #e65100;`
  - section-label 学習: `background: #e8f5e9; color: #2e7d32;`
  - section-label スケジュール: `background: #fef3c7; color: #b45309;`
  - 番号丸チップ: `background: #f59e0b;`

### log.md への prepend

`$OBSIDIAN_VAULT/log.md` の先頭（ヘッダー直後）に以下を prepend:

```
## [YYYY-MM-DD HH:MM] morning | reports/morning/YYYY-MM-DD.html
P0: {優先課題1の見出し}。学習: {1〜2件の見出し}。比率 70:30。
```

### ブラウザ起動

```bash
open "$OBSIDIAN_VAULT/reports/morning/$(date +%Y-%m-%d).html"
```

---

## Step 5. 完了通知

優先課題数 N、学習トピック数 M を集計して通知する（100文字以内・ずんだもん口調）。

```bash
~/.local/bin/vv "おはようなのだ。今日の優先タスクは${N}件、学習は${M}件なのだ"
```
