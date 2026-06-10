---
description: "個人用Mac向け朝ルーティン。time-tracker優先目標×wkhis直近7日レビューで「時間配分チャート→今週の輝き→目標別評価→TOP3→学習→スケジュール」を出力。平日/休日モード自動判定。"
---

# /morning-life — 個人生活OS 朝レポート

**本スキルは ~/work/MyVault + ~/work/time-tracker を軸とした個人用 Mac 専用。**

平日（月〜金）は 10:00〜19:30 が仕事拘束のため、フリー時間は **朝 05:00-07:00 / 08:00-10:00** と **夜 21:00-24:00** の計 7 時間。休日（土日）は終日フリー。スケジュールはこの時間枠に合わせて組む。

---

## Step 1. 引き継ぎ復元

`~/.claude/context/last-session.md` を Read する。存在しなければスキップ。

---

## Step 2. データ収集（すべて並列実行）

以下の 2-A〜2-F を **1つの応答内で同時** に実行する。

### 2-A. time-tracker 優先目標（固定リスト）

以下を前提とする（`~/work/time-tracker/src/App.tsx` の `seedPrioritiesOnce()` より）。
**月曜のみ** App.tsx を Read して差分があれば更新する。火〜日は固定リストをそのまま使う。

```
【緊急・重要 (priority)】
1. みゆ緘黙
2. たいの日常習慣改善
3. たいの自立勉強習慣
4. 住宅plan検討
5. 妻の仕事斡旋サポート
6. 投資検討
7. アプリ改善

【重要・非緊急 (priorityImportant)】
8. 修身・歴史・政治経済の勉強と発信活動
```

### 2-B. wkhis 直近7日ファイル読み込み + 翌日ゴール抽出

```bash
ls -t ~/work/MyVault/raw/wkhis-extract/*.md 2>/dev/null | head -7
```

取得したファイルパスをすべて Read してメモリに保持する。

**翌日ゴール抽出（LLM解釈）:**  
最新1件（リスト先頭）の wkhis ファイルの **冒頭部分**（先頭 30 行、または最初の `## ` 見出しが登場するまでのどちらか短い方）を対象に、「明日」「翌日」「next」「ゴール」「目標」などのキーワードを含む自然文を探す。見つかれば `NEXT_DAY_GOALS_RAW` として保持する（フォーマット不問・自然文のまま）。  
Step 3-6 でこのテキストから「タスク名 / 時間見積もり / タイミング（朝・夜・午前・午後の示唆）」を LLM が解釈してスケジュールに反映する。

### 2-C. 時間配分集計（Python3）

以下のスクリプトを Bash で実行する。

```bash
python3 - <<'PYEOF'
import re, json, os, glob

VAULT = os.path.expanduser("~/work/MyVault")
CAT_FILE = os.path.expanduser("~/.claude/commands/morning-life-categories.json")

# カテゴリ辞書ロード（フォールバック: デフォルトのみ）
try:
    with open(CAT_FILE) as f:
        cfg = json.load(f)
    cats = cfg["categories"]
    default_cat = cfg["default_category"]
except Exception:
    cats = []
    default_cat = {"name": "その他", "color_class": "bar-other"}

TIME_RANGE = re.compile(r'\b(\d{1,2}:\d{2}|\d{3,4})\s*[-–~～〜]\s*(\d{1,2}:\d{2}|\d{3,4})\b')

def parse_min(s):
    s = s.replace(':', '')
    try:
        n = int(s)
    except ValueError:
        return -1
    if len(s) <= 2:
        return n * 60
    return (n // 100) * 60 + (n % 100)

def classify(line):
    for c in cats:
        if any(kw in line for kw in c["keywords"]):
            return c["name"], c["color_class"]
    return default_cat["name"], default_cat["color_class"]

totals = {}   # name -> {"minutes": int, "entries": int, "days": set, "color_class": str}

files = sorted(glob.glob(f"{VAULT}/raw/wkhis-extract/*.md"), reverse=True)[:7]
for fpath in files:
    date_str = os.path.basename(fpath).replace(".md", "")
    try:
        with open(fpath) as f:
            for line in f:
                m = TIME_RANGE.search(line)
                if not m:
                    continue
                s = parse_min(m.group(1))
                e = parse_min(m.group(2))
                raw_end = m.group(2).replace(':', '')
                if raw_end in ('2400', '24'):
                    e = 1440
                if s < 0 or e < 0 or s >= e or e > 1440:
                    continue
                dur = e - s
                name, cc = classify(line)
                if name not in totals:
                    totals[name] = {"minutes": 0, "entries": 0, "days": set(), "color_class": cc}
                totals[name]["minutes"] += dur
                totals[name]["entries"] += 1
                totals[name]["days"].add(date_str)
    except Exception:
        continue

# TSV出力: name\tminutes\tentries\tdays\tcolor_class
for name, v in sorted(totals.items(), key=lambda x: -x[1]["minutes"]):
    if v["minutes"] > 0:
        print(f"{name}\t{v['minutes']}\t{v['entries']}\t{len(v['days'])}\t{v['color_class']}")
PYEOF
```

出力された TSV を保持する（HTMLチャート生成で使用）。

### 2-D. 直近 daily-brief の PATTERN / QUESTION / OPEN_THREADS（log.md は参照しない）

```bash
LATEST=$(ls -t ~/work/MyVault/reports/daily/*.md 2>/dev/null | head -1)
[ -n "$LATEST" ] && sed -n '/^## PATTERN/,$p' "$LATEST"
```

PATTERN / QUESTION / OPEN_THREADS の3節を保持する。OPEN_THREADS は Step 3-4 の TOP3 選定入力、PATTERN / QUESTION は Phase 2 節の表示に使う。

### 2-F. 関心トピック（直近7日）

```bash
find ~/work/MyVault/ideas ~/work/MyVault/wiki -name '*.md' -mtime -7 -type f 2>/dev/null | head -20
```

ファイル名一覧のみ取得。中身の Read は不要。

---

## Step 3. 統合・分析

収集結果を統合して以下を順番に構築する。

### 3-1. 時間配分集計の整理

2-C の TSV 出力を分析し:
- 合計記録時間を計算
- カテゴリを降順にソート
- 「動画・SNS」が上位に来た場合、何時間かを記録しておく（振り返りコメントで使用）

### 3-2. 今週の輝き（最大3件）抽出

以下のロジックで 2-B の wkhis データから成果を抽出する。

**検出条件（優先順）:**
1. **継続スコア**: 同一カテゴリ（緘黙チャレンジ・振り返り等）が **3日以上** wkhis に登場 → `「Nカテゴリ、X/7日 実施」`
2. **マイルストーン**: 「面談」「予約」「申込み」「決定」「設定」「OK」「完了」を含む行 → 単発でも実績として抽出
3. **時間規模**: 単日で2h以上のカテゴリ → 集中できた証拠

**表現テンプレ（事実 + 一言の前向きな解釈）:**
- `みゆ緘黙チャレンジ 7/7日 実施 — 継続の習慣化が根付いてきている`
- `中学校先生と6/14チャレンジ面談 — 具体的なゴールを合意できた`
- `振り返り 5日連続で記録 — ルーティンの質が上がっている`

### 3-3. 目標別レビュー（動いた目標のみ詳細）

2-A の 8目標それぞれについて、2-B の wkhis データから以下を評価:

| バッジ | 条件 |
|---|---|
| ✅ 前進中 | 出現3日以上 OR 累計2h以上 |
| ⚠️ 断片的 | 出現1〜2日 OR 累計1h未満 |
| ✗ 未記録 | 7日間で出現0回 |

**✗ 未記録の目標はカードを作らない。**「未記録: X, Y, Z」の1行に集約し、詳細は「保留中/積み残し」節に委ねる（毎朝の断罪羅列を避ける）。

**例外: 目標1「みゆ緘黙」は時間でなく回数・Lv で評価する**（主指標 = 回数・難易度感変化。2026-06-01 評価軸転換）:
- **チャレンジ回数**: wkhis 7日間のチャレンジ出現回数 + 連続日数（2日以上続いていれば「X日連続🔥」を表示）
- **Lv / 難易度変化**: wkhis 記述から難易度の上げ下げ・場面の変化を1行で
- **本人発の言葉**: 7日間で「みゆが自分から言った言葉」の記録が 0 件なら ⚠️「本人の言葉 未記録 — 親設計独走サイン（緘黙plan運用ルール §C）」を必ず付記

**カード記述の順番を厳守:**
1. **できたこと**（事実）: 「N日 / 累計Xh / 具体的にしたこと」（みゆ緘黙は「N回 / X日連続 / Lv変化」）
2. **残り課題**（次のアクション）: 「残N日 / 未着手の具体的な1アクション」

### 3-4. TOP3 抽出

以下の優先順で今日やる3件を選ぶ:

| 優先度 | 条件 |
|---|---|
| P0 最優先 | 日付が明示されている期限（例: 6/14 残N日） |
| P1 高 | 2-D の OPEN_THREADS にある未完了スレッド / 本人が wkhis・daily-brief で「やった方がいい」と認識済み |
| P2 中 | ⚠️ または ✗ のうち、放置すると連鎖影響が大きいもの |

各 TOP3 は「今日の具体的な1アクション」を箇条書きで 2〜3 個記載。

### 3-5. 学習トピック選出（1〜2件）

候補は以下の2カテゴリのみ:
1. **[深掘り]** 2-F 直近7日の ideas/ メモ
2. **[メモ化]** 2-D の QUESTION への自分なりの回答を `ideas/` に書く

候補がなければ「今日 ideas/ に気づきを1つ書く」を提案。

### 3-6. 時間ブロック割り当て

#### 3-6-1. モード判定

```bash
DOW=$(date +%u)   # 1=月 〜 5=金 → 平日 / 6=土,7=日 → 休日
```

#### 3-6-2. TOP3 の朝/夜スロット振り分け（優先順）

1. **NEXT_DAY_GOALS_RAW に明示タイミング**があればそれを最優先。例:「住宅plan 1h 朝にやる」→ 朝枠に配置。
2. **categories.json の `slot` フィールド**（`morning` / `evening` / `any`）を参照。スキル実行時に `~/.claude/commands/morning-life-categories.json` を Read して各目標に対応するカテゴリの slot を確認。
3. どちらも不明なら目標名から推定:
   - みゆ緘黙 / たい教育・習慣 / 住宅plan / 妻サポート → `morning`
   - 投資検討 / アプリ改善 / 修身・発信 → `evening`

#### 3-6-3. 平日テンプレート

| 時間帯 | 種別 | 内容 |
|---|---|---|
| 05:00-07:00 | 🌅 朝1（頭を使う系） | TOP3 のうち `slot=morning` のもの（優先度高） |
| 07:00-08:00 | 🍳 朝食・身支度 | （固定） |
| 08:00-10:00 | 🌅 朝2（頭を使う系） | TOP3 のうち `slot=morning` の残り |
| 10:00-19:30 | 💼 仕事（拘束） | （固定・編集不可） |
| 19:30-21:00 | 🍽️ 夕食・家族時間 | （固定） |
| 21:00-24:00 | 🌙 夜（事務・改善・読書） | `slot=evening` の TOP3 ＋ 学習トピック |

#### 3-6-4. 休日テンプレート（土日）

| 時間帯 | 種別 | 内容 |
|---|---|---|
| 05:00-08:00 | 🌅 朝（頭を使う系） | TOP3 のうち `slot=morning` のもの |
| 08:00-09:00 | 🍳 朝食 | （固定） |
| 09:00-12:00 | 🎯 午前（深い作業 or 家族） | TOP3 残り or 家族対応 |
| 12:00-13:00 | 🍽️ 昼食 | （固定） |
| 13:00-17:00 | 🎯 午後（フリー） | TOP3 残り ＋ 学習トピック |
| 17:00-19:00 | 👨‍👩‍👧 家族時間 | （固定） |
| 19:00-21:00 | 🍽️ 夕食・家事 | （固定） |
| 21:00-24:00 | 🌙 夜（事務・改善・読書） | `slot=evening` ＋ 積み残し |

#### 3-6-5. wkhis 翌日ゴール反映ルール

- NEXT_DAY_GOALS_RAW に**時間見積もり**（「1h」「30分」「2時間」など）があれば、該当ブロック内でその時間幅を確保する。
- **タイミング指示**（「朝」「夜」「午前」「午後」）があれば、対応する時間帯に配置する。
- ゴール文に TOP3 にない追加タスクが含まれている場合、対応ブロックに **「📝 wkhis翌日ゴール由来」** ラベル付きで差し込む。

---

## Step 4. ターミナル出力（Markdown）

以下の順序で出力する。

```
☀️ おはようございます — YYYY-MM-DD (曜日)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 時間配分（直近7日 / 記録Nh）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{カテゴリを分数降順で。最大値を16文字幅の█で表示。}
動画・SNS    ████████████████ 8h40m ← ※記録時間の大半を占めている
緘黙チャレンジ ████████ 4h20m
仕事        ████████████ 6h45m
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌟 今週の輝き
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • {事実} — {一言の前向きな解釈}
  • {事実} — {一言の前向きな解釈}
  • {事実} — {一言の前向きな解釈}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 wkhisレビュー — 目標別評価
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ※共通パターン（繰り返し課題があれば1行で）

  1. {バッジ} {目標名}
     できたこと: {具体}（みゆ緘黙は N回 / X日連続🔥 / Lv変化 / 本人の言葉 有無）
     残り課題: {具体 + 期限}
  ...（✅⚠️ のみ。✗ はカード化しない）

  ✗ 未記録: {目標名をカンマ区切りで1行}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 優先課題 TOP3 — 今日やること
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. [P0 期限] {目標名} — {今日の具体的1アクション}
     → {アクション詳細1}
     → {アクション詳細2}
  2. ...
  3. ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 学習トピック
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  - [{タイプ}] {ページ名 or テーマ}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 今日のスケジュール（{平日 | 休日}モード）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  05:00-07:00  🌅 朝1  {TOP3アイテム（朝向き）または 自由}
  07:00-08:00  🍳 朝食・身支度
  08:00-10:00  🌅 朝2  {TOP3アイテム（朝向き）残り}
  10:00-19:30  💼 仕事（拘束）               ← 平日のみ
  19:30-21:00  🍽️ 夕食・家族               ← 平日のみ
  21:00-24:00  🌙 夜    {TOP3（夜向き） / 学習 / 事務}

  ※ wkhis翌日ゴール由来: {あれば箇条書き、なければ省略}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 保留中 / 積み残し
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {TOP3に入らなかった ✗ または ⚠️ の目標を列挙}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 引き継ぎメモ（last-session.md）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {ファイルがあれば3行以内で要約。なければ（なし）}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 プロジェクト状態
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  time-tracker: {実装状況メモ}
  MyVault: {直近操作}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Claude Usage（月曜のみ）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚠️ 今日は月曜です。この出力の後に /usage を実行してください。
  Skills / Subagents / Plugins / MCP 別コストを確認し、
  異常値があれば wiki/テクノロジー/AI活用/Claude_Code_節約術.md に追記してください。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💭 Phase 2 連動
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  本日 daily-brief（launchd 自動生成済み）より:
  PATTERN: {2-D の PATTERN 要点}
  QUESTION: {2-D の QUESTION}
  ※ 月曜日の場合: 「週次シンセシスを実行して」も推奨
```

---

## Step 5. HTML 出力

### 出力先

```
~/work/MyVault/reports/morning/YYYY-MM-DD.html
```

ディレクトリが無ければ `mkdir -p` で作成。同日に既存ファイルがあれば **上書き**。

### HTML テンプレート

以下の完全な HTML を生成する。`{PLACEHOLDER}` 部分を実際のデータで差し替える。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Morning Life — {DATE}</title>
<style>
  :root {
    --bg: #fef9f0; --card: #ffffff; --border: #ffe0a0;
    --accent: #f59e0b; --accent2: #ef4444; --accent3: #22c55e;
    --text: #1c1917; --text-muted: #78716c; --tag: #fef3c7;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg); color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 15px; line-height: 1.7;
    padding: 0 1rem 3rem; max-width: 760px; margin: 0 auto;
  }
  header {
    background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
    color: #fff; padding: 2rem 1.5rem 1.5rem;
    margin: 0 -1rem 2rem; border-radius: 0 0 16px 16px;
  }
  header .label { font-size: 0.7rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; opacity: 0.8; }
  header .date { font-size: 2rem; font-weight: 700; margin-top: 0.2rem; }
  header .sub { font-size: 0.9rem; opacity: 0.85; margin-top: 0.3rem; }
  .section { margin-bottom: 2rem; }
  .section-label {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
    margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;
    padding: 0.4rem 0.8rem; border-radius: 6px;
  }
  .section-label::after { content: ''; flex: 1; height: 1px; background: var(--border); }
  .sl-chart    { background: #fef3c7; color: #b45309; }
  .sl-shine    { background: #fefce8; color: #a16207; }
  .sl-priority { background: #fff3e0; color: #e65100; }
  .sl-review   { background: #fef3c7; color: #b45309; }
  .sl-study    { background: #e8f5e9; color: #2e7d32; }
  .sl-schedule { background: #fef3c7; color: #b45309; }
  .sl-hold     { background: #f3f4f6; color: #6b7280; }
  .sl-session  { background: #ede9fe; color: #5b21b6; }
  .sl-repo     { background: #ecfdf5; color: #065f46; }
  .sl-phase2   { background: #ede9fe; color: #6d28d9; }

  /* ── チャート ── */
  .chart-row {
    display: grid; grid-template-columns: 130px 1fr 80px;
    align-items: center; gap: 0.8rem; padding: 0.45rem 0; font-size: 0.85rem;
  }
  .chart-label { color: var(--text); font-weight: 500; }
  .chart-bar-track { background: #f3f4f6; border-radius: 4px; height: 18px; overflow: hidden; }
  .chart-bar-fill { height: 100%; border-radius: 4px; }
  .chart-value { color: var(--text-muted); font-variant-numeric: tabular-nums; text-align: right; font-size: 0.82rem; }
  .chart-note { font-size: 0.75rem; color: #ef4444; margin-left: 0.3rem; }
  .bar-goal    { background: linear-gradient(90deg, #f59e0b, #f97316); }
  .bar-growth  { background: linear-gradient(90deg, #22c55e, #16a34a); }
  .bar-work    { background: linear-gradient(90deg, #3b82f6, #2563eb); }
  .bar-consume { background: linear-gradient(90deg, #ef4444, #dc2626); }
  .bar-life    { background: linear-gradient(90deg, #a78bfa, #8b5cf6); }
  .bar-other   { background: #9ca3af; }

  /* ── 輝きカード ── */
  .shine-card {
    background: linear-gradient(135deg, #fef3c7 0%, #fef9c3 100%);
    border: 1px solid #fcd34d; border-radius: 8px;
    padding: 0.75rem 1rem; margin-bottom: 0.5rem;
  }
  .shine-fact { font-size: 0.92rem; font-weight: 600; color: #92400e; }
  .shine-interp { font-size: 0.82rem; color: #b45309; margin-top: 0.15rem; }

  /* ── details ── */
  details {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; margin-bottom: 0.8rem; overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  }
  details:hover { border-color: var(--accent); }
  details[open] { border-color: var(--accent); }
  summary {
    padding: 1rem 1.2rem; cursor: pointer; list-style: none;
    display: flex; align-items: flex-start; gap: 0.8rem; user-select: none;
  }
  summary::-webkit-details-marker { display: none; }
  .num {
    flex-shrink: 0; width: 1.8rem; height: 1.8rem; border-radius: 50%;
    background: var(--accent); color: #fff; font-size: 0.8rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center; margin-top: 0.05rem;
  }
  .conn-title { font-weight: 600; color: var(--text); flex: 1; }
  .conn-sub { font-size: 0.82rem; color: var(--text-muted); margin-top: 0.1rem; }
  .conn-arrow { color: var(--text-muted); font-size: 0.8rem; margin-left: 0.3rem; }
  .conn-body { padding: 0 1.2rem 1rem 1.2rem; color: var(--text-muted); font-size: 0.88rem; line-height: 1.6; }
  .conn-body ul { padding-left: 1.2rem; }
  .conn-body li { margin-bottom: 0.3rem; }

  /* ── バッジ ── */
  .badge {
    display: inline-block; font-size: 0.68rem; font-weight: 700;
    padding: 0.15em 0.55em; border-radius: 4px; margin-right: 0.3rem; vertical-align: middle;
  }
  .badge-ok     { background: #dcfce7; color: #166534; }
  .badge-warn   { background: #fef3c7; color: #92400e; }
  .badge-ng     { background: #fee2e2; color: #991b1b; }
  .badge-study  { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }

  /* ── スケジュール ── */
  .schedule-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
  .schedule-table td { padding: 0.45rem 0.6rem; border-bottom: 1px solid var(--border); }
  .schedule-table tr:last-child td { border-bottom: none; }
  .td-time { color: var(--text-muted); white-space: nowrap; font-variant-numeric: tabular-nums; width: 130px; }
  .block-morning    { border-left: 3px solid #f59e0b; padding-left: 0.5rem; }
  .block-work-fixed { border-left: 3px solid #9ca3af; padding-left: 0.5rem; background: #f3f4f6; color: #6b7280; }
  .block-meal       { border-left: 3px solid #d1d5db; padding-left: 0.5rem; }
  .block-evening    { border-left: 3px solid #a855f7; padding-left: 0.5rem; }
  .block-free       { border-left: 3px solid #22c55e; padding-left: 0.5rem; }

  /* ── その他 ── */
  .hold-item { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 0.6rem 1rem; margin-bottom: 0.4rem; font-size: 0.85rem; color: var(--text-muted); }
  blockquote { background: #f9fafb; border-left: 3px solid #d1d5db; padding: 0.8rem 1rem; border-radius: 6px; font-size: 0.88rem; color: var(--text-muted); }
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
  .repo-group { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 0.8rem 1rem; font-size: 0.85rem; }
  .repo-group h4 { font-size: 0.78rem; color: var(--text-muted); font-weight: 700; margin-bottom: 0.4rem; }
  .pattern-box { background: var(--tag); border: 1px solid var(--border); border-radius: 8px; padding: 0.8rem 1rem; margin-bottom: 0.8rem; font-size: 0.88rem; }
  .pattern-box h4 { font-size: 0.78rem; font-weight: 700; color: #92400e; margin-bottom: 0.4rem; letter-spacing: 0.05em; }
  footer { text-align: center; font-size: 0.75rem; color: var(--text-muted); margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--border); }
</style>
</head>
<body>

<header>
  <div class="label">☀️ Morning Life</div>
  <div class="date">{DATE} ({DOW})</div>
  <div class="sub">{平日モード | 休日モード} ／ time-tracker目標 × wkhis直近7日</div>
</header>

<!-- ============ 時間配分チャート ============ -->
<div class="section">
  <div class="section-label sl-chart">📊 時間配分（直近7日 / 記録{TOTAL_H}h）</div>
  <!-- chart-row を 2-C の TSV データで生成。最大値カテゴリを width:100% として相対計算。0分は非表示。 -->
  <!-- 例: -->
  <!--
  <div class="chart-row">
    <div class="chart-label">動画・SNS</div>
    <div class="chart-bar-track"><div class="chart-bar-fill bar-consume" style="width:100%"></div></div>
    <div class="chart-value">8h40m <span class="chart-note">※注意</span></div>
  </div>
  -->
  {CHART_ROWS}
</div>

<!-- ============ 今週の輝き ============ -->
<div class="section">
  <div class="section-label sl-shine">🌟 今週の輝き</div>
  <!-- shine-card を 3-2 の成果から生成 -->
  {SHINE_CARDS}
</div>

<!-- ============ wkhisレビュー ============ -->
<div class="section">
  <div class="section-label sl-review">📊 wkhisレビュー（直近7日）— 目標別評価</div>
  {PATTERN_BOX}
  <!-- 8目標分の details を 3-3 の評価から生成 -->
  {REVIEW_DETAILS}
</div>

<!-- ============ 優先課題 TOP3 ============ -->
<div class="section">
  <div class="section-label sl-priority">🎯 優先課題 TOP3（今日やること）</div>
  {TOP3_DETAILS}
</div>

<!-- ============ 学習トピック ============ -->
<div class="section">
  <div class="section-label sl-study">📚 学習トピック</div>
  {STUDY_ITEMS}
</div>

<!-- ============ スケジュール ============ -->
<div class="section">
  <div class="section-label sl-schedule">📅 今日のスケジュール（{平日モード | 休日モード}）</div>
  <table class="schedule-table">
    {SCHEDULE_ROWS}
  </table>
  {NEXT_DAY_GOALS_BOX}
</div>

<!-- ============ 保留中 ============ -->
<div class="section">
  <div class="section-label sl-hold">🔧 保留中 / 積み残し</div>
  {HOLD_ITEMS}
</div>

<!-- ============ 引き継ぎメモ ============ -->
<div class="section">
  <div class="section-label sl-session">📝 引き継ぎメモ（last-session.md）</div>
  <blockquote>{LAST_SESSION}</blockquote>
</div>

<!-- ============ プロジェクト状態 ============ -->
<div class="section">
  <div class="section-label sl-repo">🌐 プロジェクト状態</div>
  <div class="two-col">
    <div class="repo-group">
      <h4>time-tracker</h4>
      {TIMETRACKER_STATUS}
    </div>
    <div class="repo-group">
      <h4>MyVault</h4>
      {VAULT_STATUS}
    </div>
  </div>
</div>

<!-- ============ Phase 2 ============ -->
<div class="section">
  <div class="section-label sl-phase2">💭 Phase 2 連動（第二の脳 振り返りループ）</div>
  <p style="font-size:0.88rem;color:var(--text-muted)">
    {PHASE2_CONTENT}
  </p>
</div>

<footer>Generated by /morning-life — {DATE} {TIME}</footer>
</body>
</html>
```

### チャート行生成ルール

2-C の TSV を読み、以下の変換を行う:
- `minutes` の最大値を 100% として各カテゴリのバー幅を計算: `width = round(minutes / max_minutes * 100)`
- `color_class` をそのまま `chart-bar-fill` の class に使用
- `h = minutes // 60`, `m = minutes % 60` でフォーマット
- 「動画・SNS」が1位の場合、`chart-note` スパンで `※注意` を追加
- 時間ゼロのカテゴリは行を生成しない

### 輝きカード生成ルール

3-2 で抽出した成果を `shine-card` として生成:
```html
<div class="shine-card">
  <div class="shine-fact">• {事実}</div>
  <div class="shine-interp">{一言の前向きな解釈}</div>
</div>
```

### レビュー details 生成ルール

3-3 の評価に基づき、**✅⚠️ の目標のみ** `details` で生成（✗ 未記録は details 群の末尾に `<div class="hold-item">✗ 未記録: X, Y, Z</div>` の1行で集約）。みゆ緘黙カードは「N回 / X日連続🔥 / Lv変化 / 本人の言葉 有無」を記載。`details` は **常に open** にして目立たせる:
```html
<details open>
  <summary>
    <span class="num">{N}</span>
    <div class="conn-title">
      {目標名}
      <span class="badge badge-{ok|warn|ng}">{✅ 前進中|⚠️ 断片的|✗ 未記録}</span>
      <div class="conn-sub">{サブタイトル（できたことの要約1行）}</div>
    </div>
    <span class="conn-arrow">▾</span>
  </summary>
  <div class="conn-body">
    <ul>
      <li><strong>できたこと</strong>: {具体}</li>
      <li>⚠️ <strong>残り課題</strong>: {具体 + 期限}</li>
    </ul>
  </div>
</details>
```

### TOP3 details 生成ルール

```html
<details open>
  <summary>
    <span class="num">{N}</span>
    <div class="conn-title">
      {目標名} — {今日の1行アクション}
      <div class="conn-sub">{背景説明（期限・認識済みの根拠）}</div>
    </div>
    <span class="conn-arrow">▾</span>
  </summary>
  <div class="conn-body">
    <ul>
      <li>{具体的アクション1}</li>
      <li>{具体的アクション2}</li>
    </ul>
  </div>
</details>
```

### スケジュール行（SCHEDULE_ROWS）生成ルール

3-6-1 のモード判定結果に基づき、対応テンプレートの各時間枠を `<tr>` として生成。クラスは以下:

| 時間帯 | クラス |
|---|---|
| 朝1 / 朝2 / 朝（休日） | `block-morning` |
| 仕事（10:00-19:30）| `block-work-fixed` |
| 朝食 / 夕食 / 昼食 / 家族時間 | `block-meal` |
| 夜（21:00-24:00）| `block-evening` |
| 午前 / 午後（休日フリー）| `block-free` |

各行の形式:
```html
<tr>
  <td class="td-time">05:00-07:00</td>
  <td class="block-morning">🌅 朝1 — {タスク名（slot=morning の TOP3 または「自由時間」）}</td>
</tr>
```

**NEXT_DAY_GOALS_BOX 生成ルール:**  
NEXT_DAY_GOALS_RAW から追加タスクが抽出された場合のみ出力:
```html
<div style="background:#fffbeb;border:1px solid #fde68a;border-radius:6px;padding:0.6rem 0.9rem;margin-top:0.5rem;font-size:0.82rem;color:#92400e">
  📝 wkhis翌日ゴール由来: <ul style="margin:0.3rem 0 0 1rem;padding:0">{追加タスク箇条書き}</ul>
</div>
```
該当なしの場合は `{NEXT_DAY_GOALS_BOX}` を空文字に置換（出力しない）。

---

## Step 6. ブラウザ起動

```bash
open ~/work/MyVault/reports/morning/$(date +%Y-%m-%d).html
```

---

## Step 7. 完了通知

M = 輝き件数、N = TOP3 件数（固定3）

```bash
~/.local/bin/vv "おはようなのだ。今週の輝きは${M}件、優先タスクは${N}件なのだ"
```
