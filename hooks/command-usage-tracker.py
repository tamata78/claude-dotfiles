#!/usr/bin/env python3
"""UserPromptSubmit フック: /xxx コマンド入力を skill-usage.jsonl に記録する

ユーザーが /commit などのスラッシュコマンドを入力したとき、
Skill ツール呼び出しではなくプロンプト注入で処理されるため
skill-usage-tracker.py では検知できない。
このフックで UserPromptSubmit 時に /xxx パターンを検知して記録する。
"""
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    # UserPromptSubmit の入力から prompt テキストを取得
    # Claude Code は "prompt" または "message" フィールドで渡す場合がある
    prompt = data.get("prompt") or data.get("message") or ""
    if not prompt:
        sys.exit(0)

    # /xxx パターンを検知（行頭または空白後の /word）
    match = re.match(r"^\s*/([a-zA-Z0-9_-]+)", prompt.strip())
    if not match:
        sys.exit(0)

    command_name = match.group(1)

    log_dir = os.path.expanduser("~/.claude/session-env")
    os.makedirs(log_dir, exist_ok=True)
    entry = {
        "ts": datetime.now(JST).isoformat(),
        "tool": "Command",
        "target": command_name,
        "label": f"Command(/{command_name})",
        "cwd": os.getcwd(),
    }
    try:
        with open(os.path.join(log_dir, "skill-usage.jsonl"), "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
