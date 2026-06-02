---
description: "ふりかえりルーティンを手動実行。#日々のふりかえり に昨日分の振り返りを投稿する（1日1回のみ）"
---

# /furikaeri - ふりかえり手動実行

以下の手順を実行してください。

## 手順

### 1. 送信済みチェック

```bash
TODAY=$(TZ=Asia/Tokyo date +%Y-%m-%d)
LAST=$(cat ~/.claude/furikaeri-last-date 2>/dev/null || echo "")
echo "today=$TODAY last=$LAST"
```

`today == last` の場合は「本日分は送信済みです」と伝えて終了。

### 2. 対象日を計算

```bash
YESTERDAY=$(TZ=Asia/Tokyo date -v-1d +%Y-%m-%d)
MONTH=$(TZ=Asia/Tokyo date -v-1d +%-m)
DAY=$(TZ=Asia/Tokyo date -v-1d +%-d)
echo "target=$YESTERDAY  month/day=${MONTH}/${DAY}"
```

### 3. Slack #daily-log で昨日分のデータを検索

`mcp__claude_ai_Slack__slack_search_public_and_private` ツールを使い、以下の 2 件を検索する:

- **TIME-TRACKER**: query = `TIME-TRACKER ${YESTERDAY}` で検索（in:#daily-log）
- **wkhis**: query = `wkhis` で検索し、結果に `${MONTH}/${DAY}(` または `${YESTERDAY}` が含まれるメッセージを探す

### 4. TIME-TRACKER データが Slack にない場合 → 補完投稿

TIME-TRACKER のメッセージが見つからなかった場合:

```bash
python3 ~/.local/bin/time-tracker-post.py --date ${YESTERDAY} --force
```

失敗した場合（例: snapshot.json が存在しない・権限なし）は以下を伝えて中断:
> 「TIME-TRACKER データの補完投稿に失敗しました。time-tracker アプリを開いて設定 → スナップショット書出先 を設定してください。」

### 5. wkhis データが Slack にない場合 → 補完投稿

wkhis のメッセージが見つからなかった場合:

まずローカルファイルを確認:
```bash
ls ~/work/MyVault/raw/wkhis-extract/${YESTERDAY}.md
```

ファイルが存在しない場合は再抽出を試みる:
```bash
python3 ~/.local/bin/wkhis-extract.py
```

その後、Slack に補完投稿:
```bash
~/.local/bin/wkhis-post-from-extract.sh ${YESTERDAY}
```

### 6. データを取得してふりかえり本文を生成

補完投稿した場合は 2-3 秒待ち、以下のデータを元にふりかえり本文を生成する:

**データ取得優先順位（Slack → ローカルの順）:**
- Slack #daily-log の TIME-TRACKER メッセージ（ステップ 3 か 4 で入手）
- Slack #daily-log の wkhis メッセージ（ステップ 3 か 5 で入手）
- 上記が取れなければ: `~/work/MyVault/raw/wkhis-extract/${YESTERDAY}.md` を Read ツールで読む

**生成フォーマット:**
```
📅 ${YESTERDAY} ふりかえり

【今日やったこと】
- （TIME-TRACKER の実績・wkhis の主要な作業から箇条書き 3〜5 個）

【気づき・学び】
- （作業から得られた気づきや学び）

【明日の問い】
- （明日意識したいこと or 試したいこと）
```

### 7. Slack #日々のふりかえり に投稿

`mcp__claude_ai_Slack__slack_send_message` で以下に投稿する:
- channel: `#日々のふりかえり`
- text: 上記で生成したテキスト

### 8. 送信済みフラグを記録

```bash
TZ=Asia/Tokyo date +%Y-%m-%d > ~/.claude/furikaeri-last-date
```

### 9. 結果を1行で報告

補完投稿の有無を含めて報告する。例:
> 「✅ ふりかえりを #日々のふりかえり に投稿しました（TIME-TRACKER・wkhis ともに Slack 済み）」
> 「✅ ふりかえりを投稿しました（TIME-TRACKER・wkhis を #daily-log に補完投稿してから実行）」
