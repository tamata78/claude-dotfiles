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
echo "target=$YESTERDAY"
```

### 3. wkhis-extract をローカルから準備

```bash
EXTRACT="/Users/tamata78/work/MyVault/raw/wkhis-extract/${YESTERDAY}.md"
ls "$EXTRACT" || python3 ~/.local/bin/wkhis-extract.py
```

再抽出後もファイルが存在しない場合は以下を伝えて中断:
> 「wkhis-extract ファイルが見つかりません（${EXTRACT}）。wkhis-extract.py の実行に失敗した可能性があります。」

### 4. TIME-TRACKER データ取得（オプション）

TIME-TRACKER の実績が欲しい場合は以下を実行する（失敗しても継続可）:

```bash
python3 ~/.local/bin/time-tracker-post.py --date ${YESTERDAY} --force 2>/dev/null || true
```

### 5. wkhis-extract を Read して本文を生成

`/Users/tamata78/work/MyVault/raw/wkhis-extract/${YESTERDAY}.md` を Read ツールで直読みし、以下のフォーマットで本文を生成する:

```
📅 ${YESTERDAY} ふりかえり

【今日やったこと】
- （wkhis の主要な作業から箇条書き 3〜5 個）

【気づき・学び】
- （作業から得られた気づきや学び）

【明日の問い】
- （明日意識したいこと or 試したいこと）
```

### 6. Slack #日々のふりかえり に curl で投稿

credentials から webhook URL を読み込んで投稿する。`$TEXT` には手順 5 で生成した本文を入れる。

```bash
CRED_FILE="$HOME/.config/wkhis-sync/credentials"
WEBHOOK=$(grep '^SLACK_WEBHOOK_FURIKAERI=' "$CRED_FILE" 2>/dev/null | cut -d= -f2-)
```

- **webhook 設定済みの場合**: JSON エスケープして curl で POST する
  ```bash
  ESCAPED=$(printf '%s' "$TEXT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")
  curl -s -X POST "$WEBHOOK" -H 'Content-Type: application/json' -d "{\"text\": $ESCAPED}"
  ```
- **webhook 未設定の場合**: 本文をテキストで出力し、以下を伝えて終了:
  > 「`~/.config/wkhis-sync/credentials` の `SLACK_WEBHOOK_FURIKAERI=` に URL を設定してください（Slack App管理 > Incoming Webhooks から #日々のふりかえり 向けに発行）」

### 7. 送信済みフラグを記録

```bash
TZ=Asia/Tokyo date +%Y-%m-%d > ~/.claude/furikaeri-last-date
```

### 8. 結果を1行で報告

webhook 設定済みの場合:
```
✅ ふりかえりを #日々のふりかえり に投稿しました
```

webhook 未設定の場合:
```
⚠️ webhook 未設定のため手動投稿が必要です。以下の本文をコピーしてください:
（本文）
```

## 完了通知

```bash
~/.local/bin/vv "ふりかえりが完成したのだ"
```
