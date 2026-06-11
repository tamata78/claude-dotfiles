#!/bin/bash
# review-rules-reminder.sh  (SessionStart hook)
# launchd トリガーが立てた「月次レビュー規約フラグ」を検知し、未実行の月次更新があれば
# additionalContext で Claude に提示する。フラグが無ければ何も出力しない（ノイズ抑止）。
# 実際の収集・幹の抽出・書き込み・フラグ削除は /review-rules-update コマンド側で行う。

FLAG="$HOME/.claude/state/review-rules-due"

# 使用ログ（存在する場合のみ。既存 hook と同じ作法）
[ -f "$HOME/.claude/hooks/usage-log.py" ] && python3 "$HOME/.claude/hooks/usage-log.py" Hook review-rules-reminder.sh >/dev/null 2>&1 &

[ -f "$FLAG" ] || exit 0

TRIGGERED=$(cat "$FLAG" 2>/dev/null)

CONTEXT="## 🗓️ 月次レビュー規約の更新が未実行です（対象月: ${TRIGGERED}）

毎月1日の定期トリガーが立っています。手が空いたタイミングで **\`/review-rules-update\`** を実行し、
直近1ヶ月の PR レビュー指摘から幹を抽出し、shiva / odin(payment) / billing の共有レビュー規約へ反映してください。

- 緊急の作業中であれば無理に今やる必要はありません。ユーザーに「今 /review-rules-update を実行してよいか」を一度確認してから進めてください。
- 単純追記ではなく、重複・冗長を整理して幹となる本質的な指摘を抽出するのが目的です。各リポの差分は承認後にのみ書き込み、完了時にこのフラグは自動で消えます。"

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
