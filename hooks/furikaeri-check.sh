#!/bin/bash
TODAY=$(TZ=Asia/Tokyo date +%Y-%m-%d)
LAST=$(cat ~/.claude/furikaeri-last-date 2>/dev/null || echo "")
HOUR=$(TZ=Asia/Tokyo date +%-H)

[ "$TODAY" = "$LAST" ] && exit 0
[ "$HOUR" -lt 7 ] && exit 0

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "⚠️ 昨日分のふりかえりが未送信です（last=${LAST}, today=${TODAY}）。最初のユーザー応答に入る前に /furikaeri を実行して #日々のふりかえり に投稿してください。"
  }
}
EOF
