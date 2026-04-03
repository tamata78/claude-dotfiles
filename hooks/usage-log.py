#!/usr/bin/env python3
"""ユーティリティ: skill-usage.jsonl に1エントリを追記する

使い方:
  python3 usage-log.py <tool_type> <target_name>

例:
  python3 usage-log.py Hook session-start-snapshot.sh
  python3 usage-log.py Command commit
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))


def log_usage(tool: str, target: str) -> None:
    log_dir = os.path.expanduser("~/.claude/session-env")
    os.makedirs(log_dir, exist_ok=True)
    entry = {
        "ts": datetime.now(JST).isoformat(),
        "tool": tool,
        "target": target,
        "label": f"{tool}({target})",
        "cwd": os.getcwd(),
    }
    try:
        with open(os.path.join(log_dir, "skill-usage.jsonl"), "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(0)
    log_usage(sys.argv[1], sys.argv[2])
