#!/usr/bin/env python3
"""Ring Meter status line for Claude Code - Pattern 3"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from typing import Optional

JST = timezone(timedelta(hours=9))

def make_emoji_ring(pct: float, size: int = 6) -> str:
    """Create a colored ASCII block meter based on percentage."""
    filled = round(pct / 100 * size)
    if pct < 60:
        color = "\033[32m"  # green
    elif pct < 85:
        color = "\033[33m"  # yellow
    else:
        color = "\033[31m"  # red
    reset = "\033[0m"
    bar = "\u2588" * filled + "\u2591" * (size - filled)
    return f"{color}{bar}{reset}"

def fmt_reset(resets_at: Optional[object], mode: str) -> str:
    """Parse resets_at (Unix epoch number or ISO 8601 string) and return JST formatted string."""
    if not resets_at:
        return ""
    try:
        if isinstance(resets_at, (int, float)):
            dt = datetime.fromtimestamp(resets_at, tz=timezone.utc)
        else:
            dt = datetime.fromisoformat(str(resets_at).replace("Z", "+00:00"))
        dt_jst = dt.astimezone(JST)
        if mode == "hour":
            return dt_jst.strftime("→%H:%M")
        else:
            return dt_jst.strftime(f"→{dt_jst.month}/{dt_jst.day:02d} %H:%M")
    except Exception:
        return ""

def get_git_info() -> str:
    """Get current git branch and dirty status."""
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL, timeout=1
        ).decode().strip()
        if branch == "HEAD":
            return ""
        # Check for uncommitted changes
        dirty = subprocess.call(
            ["git", "diff", "--quiet"],
            stderr=subprocess.DEVNULL, timeout=1
        ) != 0
        staged = subprocess.call(
            ["git", "diff", "--cached", "--quiet"],
            stderr=subprocess.DEVNULL, timeout=1
        ) != 0
        marker = "*" if (dirty or staged) else ""
        return f"\ue0a0 {branch}{marker}"
    except Exception:
        return ""

def get_project_name() -> str:
    """Get current project name from CWD."""
    cwd = os.getcwd()
    home = os.path.expanduser("~")
    if cwd == home or cwd.startswith(home + "/work") and cwd.count("/") <= home.count("/") + 2:
        parts = cwd.split("/")
        return parts[-1] if parts[-1] else ""
    parts = cwd.split("/")
    return parts[-1] if parts[-1] else ""

def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        data = {}

    line1_parts = []
    line2_parts = []

    # Project name
    project = get_project_name()
    if project and project not in ("work", "tamata78", ""):
        line1_parts.append(f"📁 {project}")

    # Model name
    model_obj = data.get("model", {})
    if isinstance(model_obj, dict):
        model_name = model_obj.get("display_name", model_obj.get("id", ""))
    else:
        model_name = str(model_obj) if model_obj else ""
    if model_name:
        short = model_name.replace("Claude ", "").replace("claude-", "")
        line1_parts.append(f"\U0001f916 {short}")
    else:
        line1_parts.append("\U0001f916 Claude Code")

    # Git branch info → line1
    git_info = get_git_info()
    if git_info:
        line1_parts.append(git_info)

    # Context window usage → line2
    ctx = data.get("context_window", {})
    if ctx:
        used = ctx.get("used_percentage")
        if used is not None:
            ring = make_emoji_ring(used)
            line2_parts.append(f"CTX {ring} {used:.0f}%")

    # Rate limits → line2
    rl = data.get("rate_limits", {})

    five_hour = rl.get("five_hour", {})
    if five_hour:
        pct = five_hour.get("used_percentage", 0)
        ring = make_emoji_ring(pct, 4)
        reset_str = fmt_reset(five_hour.get("resets_at"), "hour")
        line2_parts.append(f"5h {ring} {pct:.0f}%{reset_str}")

    seven_day = rl.get("seven_day", {})
    if seven_day:
        pct = seven_day.get("used_percentage", 0)
        ring = make_emoji_ring(pct, 4)
        reset_str = fmt_reset(seven_day.get("resets_at"), "day")
        line2_parts.append(f"7d {ring} {pct:.0f}%{reset_str}")

    # Session elapsed time
    session_start_file = os.path.expanduser("~/.claude/session-env/current-start")
    try:
        if os.path.exists(session_start_file):
            with open(session_start_file) as f:
                start_ts = float(f.read().strip())
            elapsed_sec = (datetime.now().timestamp() - start_ts)
            elapsed_min = int(elapsed_sec / 60)
            if elapsed_min >= 60:
                elapsed_str = f"{elapsed_min // 60}h{elapsed_min % 60:02d}m"
            else:
                elapsed_str = f"{elapsed_min}m"
            line2_parts.append(f"⏱ {elapsed_str}")
    except Exception:
        pass

    output = "  ".join(line1_parts)
    if line2_parts:
        output += "\n" + "  ".join(line2_parts)
    print(output)

if __name__ == "__main__":
    main()
