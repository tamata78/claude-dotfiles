#!/usr/bin/env python3
"""PostToolUse フック: Write/Edit/Bash(git commit)等の操作をログに記録する"""
import json
import sys
import os
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))

# 記録対象のツールと操作
LOGGED_TOOLS = {
    "Write": lambda inp: f"Write: {inp.get('file_path', '?')}",
    "Edit": lambda inp: f"Edit: {inp.get('file_path', '?')} ({inp.get('old_string', '')[:30].strip()!r} → ...)",
    "Bash": lambda inp: _bash_label(inp.get("command", "")),
}

BASH_PATTERNS = [
    ("git commit", "git commit"),
    ("git push", "git push"),
    ("git tag", "git tag"),
    ("git reset", "git reset"),
    ("git checkout", "git checkout"),
    ("rm -rf", "rm -rf"),
    ("npm install", "npm install"),
    ("pip install", "pip install"),
]

def _bash_label(cmd: str) -> str:
    for pattern, label in BASH_PATTERNS:
        if pattern in cmd:
            return f"Bash: {label}: {cmd[:80].strip()}"
    return None  # None = 記録しない

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name not in LOGGED_TOOLS:
        sys.exit(0)

    label_fn = LOGGED_TOOLS[tool_name]
    label = label_fn(tool_input)
    if label is None:
        sys.exit(0)

    # ログファイルに追記
    log_dir = os.path.expanduser("~/.claude/session-env")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "operation-log.jsonl")

    now = datetime.now(JST)
    entry = {
        "ts": now.isoformat(),
        "tool": tool_name,
        "label": label,
        "cwd": os.getcwd(),
    }

    with open(log_file, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    sys.exit(0)

if __name__ == "__main__":
    main()
