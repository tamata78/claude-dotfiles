#!/usr/bin/env python3
"""Ring Meter status line for Claude Code - Pattern 3"""
import json
import sys
from datetime import datetime, timezone, timedelta
from typing import Optional

JST = timezone(timedelta(hours=9))

def make_ring(pct: float, size: int = 6) -> str:
    """Create a ring/arc meter using block characters."""
    filled = round(pct / 100 * size)
    return "█" * filled + "░" * (size - filled)

def color(text: str, pct: float) -> str:
    """Color text based on percentage (green/yellow/red)."""
    if pct < 60:
        code = "32"  # green
    elif pct < 85:
        code = "33"  # yellow
    else:
        code = "31"  # red
    return f"\033[{code}m{text}\033[0m"

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

def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        data = {}

    line1_parts = []
    line2_parts = []

    # Current time (always shown)
    now_jst = datetime.now(JST)
    line1_parts.append(now_jst.strftime("%H:%M"))

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

    # Context window usage → line2
    ctx = data.get("context_window", {})
    if ctx:
        used = ctx.get("used_percentage")
        if used is not None:
            ring = make_ring(used)
            line2_parts.append(color(f"CTX {ring} {used:.0f}%", used))

    # Rate limits → line2
    rl = data.get("rate_limits", {})

    five_hour = rl.get("five_hour", {})
    if five_hour:
        pct = five_hour.get("used_percentage", 0)
        ring = make_ring(pct, 4)
        reset_str = fmt_reset(five_hour.get("resets_at"), "hour")
        line2_parts.append(color(f"5h {ring} {pct:.0f}%{reset_str}", pct))

    seven_day = rl.get("seven_day", {})
    if seven_day:
        pct = seven_day.get("used_percentage", 0)
        ring = make_ring(pct, 4)
        reset_str = fmt_reset(seven_day.get("resets_at"), "day")
        line2_parts.append(color(f"7d {ring} {pct:.0f}%{reset_str}", pct))

    output = "  ".join(line1_parts)
    if line2_parts:
        output += "\n" + "  ".join(line2_parts)
    print(output)

if __name__ == "__main__":
    main()
