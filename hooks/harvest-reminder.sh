#!/bin/bash
# harvest-reminder.sh  (SessionStart hook)
# launchd トリガーが立てた「収穫フラグ」を検知し、未実行の週次 harvest があれば
# additionalContext で Claude に提示する。フラグが無ければ何も出力しない（ノイズ抑止）。
# 実際の収穫・フラグ削除は /vault-harvest コマンド側で行う。

FLAG="$HOME/.claude/state/harvest-due"

# 使用ログ（存在する場合のみ。既存 hook と同じ作法）
[ -f "$HOME/.claude/hooks/usage-log.py" ] && python3 "$HOME/.claude/hooks/usage-log.py" Hook harvest-reminder.sh >/dev/null 2>&1 &

[ -f "$FLAG" ] || exit 0

TRIGGERED=$(cat "$FLAG" 2>/dev/null)

CONTEXT="## ⏰ 週次 harvest が未実行です（${TRIGGERED} にトリガー）

水/金 17:03 の定期トリガーが立っています。手が空いたタイミングで **\`/vault-harvest\`**（提案レビュー方式）を実行し、直近の開発活動から耐久知見を vault に収穫してください。

- 緊急の作業中であれば無理に今やる必要はありません。ユーザーに「今 harvest を実行してよいか」を一度確認してから進めてください。
- 実行すると候補が \`reports/harvest-pending-{日付}.md\` に書き出され、このフラグは自動で消えます。"

python3 - "$CONTEXT" <<'PY'
import json, sys
ctx = sys.argv[1]
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": ctx
    }
}))
PY

exit 0
