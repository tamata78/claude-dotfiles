#!/usr/bin/env python3
"""PreToolUse フック: スキル・エージェント呼び出しを記録してスキル使用率を計測

Skill / Agent ツールの呼び出しを ~/ .claude/session-env/skill-usage.jsonl に記録する。
使われていないスキルの整理や、よく使うスキルの最適化に活用する。
"""
import json
import sys
import os
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))

TRACKED_TOOLS = {"Skill", "Agent"}


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in TRACKED_TOOLS:
        sys.exit(0)

    tool_input = data.get("tool_input", {})

    # スキル名またはエージェント種別を取得
    if tool_name == "Skill":
        target = tool_input.get("skill", tool_input.get("name", "unknown"))
        args = tool_input.get("args", "")
        label = f"Skill({target})" + (f" args={args[:40]}" if args else "")
    else:  # Agent
        target = tool_input.get("subagent_type", "general-purpose")
        desc = tool_input.get("description", "")
        label = f"Agent({target})" + (f" - {desc[:40]}" if desc else "")

    log_dir = os.path.expanduser("~/.claude/session-env")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "skill-usage.jsonl")

    entry = {
        "ts": datetime.now(JST).isoformat(),
        "tool": tool_name,
        "target": target,
        "label": label,
        "cwd": os.getcwd(),
    }
    if tool_name == "Agent":
        entry["model"] = tool_input.get("model", "default")

    try:
        with open(log_file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
