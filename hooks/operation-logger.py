#!/usr/bin/env python3
"""PostToolUse フック: Bash/Edit/Write 操作を operation-log.jsonl に記録する

トークン分析ポータルの operationTokens 集計に使用する。
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))

TRACKED_TOOLS = {"Bash", "Edit", "Write"}


def build_label(tool_name: str, tool_input: dict) -> str:
    if tool_name == "Bash":
        cmd = tool_input.get("command", "")
        short = cmd.replace("\n", " ").strip()[:80]
        return f"Bash: {short}"
    elif tool_name == "Edit":
        path = tool_input.get("file_path", "")
        old = tool_input.get("old_string", "")[:30].replace("\n", "\\n")
        new = tool_input.get("new_string", "")[:20].replace("\n", "\\n")
        return f"Edit: {path} ('{old}' → '{new[:20]}...')" if old else f"Edit: {path}"
    elif tool_name == "Write":
        path = tool_input.get("file_path", "")
        return f"Write: {path}"
    return f"{tool_name}: unknown"


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception:
        print(json.dumps({}))
        return

    tool_name = data.get("tool_name", "")
    if tool_name not in TRACKED_TOOLS:
        print(json.dumps({}))
        return

    tool_input = data.get("tool_input", {})
    log_dir = os.path.expanduser("~/.claude/session-env")
    os.makedirs(log_dir, exist_ok=True)

    entry = {
        "ts": datetime.now(JST).isoformat(),
        "tool": tool_name,
        "label": build_label(tool_name, tool_input),
        "cwd": os.getcwd(),
    }

    try:
        with open(os.path.join(log_dir, "operation-log.jsonl"), "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

    print(json.dumps({}))


if __name__ == "__main__":
    main()
