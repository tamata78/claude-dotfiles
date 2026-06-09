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
    "additionalContext": "💬 昨日分のふりかえりが未投稿です（last=${LAST}, today=${TODAY}）。現在のタスク完了後に /furikaeri を実行してください。"
  }
}
EOF
