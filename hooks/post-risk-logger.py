#!/usr/bin/env python3
"""
PostToolUse フック: risk-analyzer (PreToolUse) で ask 判定されたツールの
実行結果（ユーザーが approve/deny したか）を記録する。

permission-requests ログの decision フィールドを補完し、
ユーザーの実際の判断パターンを分析可能にする。
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)

        tool_name = data.get("tool_name", "Unknown")
        tool_input = data.get("tool_input", {})
        tool_result = data.get("tool_result", {})

        # tool_result から実行結果を判定
        # PostToolUse は実行されたツールに対して呼ばれるため、
        # ここに到達 = ユーザーが approve した（or 自動承認された）
        # deny された場合は PostToolUse 自体が呼ばれない

        log_dir = os.path.expanduser("~/.claude/session-env")
        os.makedirs(log_dir, exist_ok=True)
        now = datetime.now(JST)
        log_file = os.path.join(log_dir, f"permission-outcomes-{now.strftime('%Y-%m')}.jsonl")

        entry = {
            "ts": now.isoformat(),
            "tool": tool_name,
            "outcome": "executed",
            "session_id": os.environ.get("CLAUDE_SESSION_ID", "unknown"),
        }

        if tool_name == "Bash":
            entry["command"] = tool_input.get("command", "")[:200]
        elif tool_name in ("Edit", "Write"):
            entry["file_path"] = tool_input.get("file_path", "")

        with open(log_file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    except Exception:
        pass

    # PostToolUseフックは結果に影響しない
    print(json.dumps({}))


if __name__ == "__main__":
    main()
