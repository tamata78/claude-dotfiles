#!/usr/bin/env python3
"""Stop フック: ファイル編集後のビルド・テスト未確認を検出してナッジ

operation-log.jsonl を参照し、直近5分以内に：
- Write/Edit があった AND
- ビルド/テストコマンドが実行されていない

場合のみ、セッションごとに1回だけブロックして確認を促す。
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))

TEST_KEYWORDS = [
    "npm test",
    "npm run test",
    "npm run build",
    "npx tsc",
    "pytest",
    "go test",
    "cargo test",
    "make test",
    "make build",
    "yarn test",
    "yarn build",
]


def approve():
    print(json.dumps({"decision": "approve"}))


def nudge(reason: str):
    print(json.dumps({"decision": "block", "reason": reason}))


def main():
    try:
        json.load(sys.stdin)
    except Exception:
        approve()
        return

    # セッションごとに1回だけナッジ（CLAUDE_SESSION_ID があれば利用）
    session_id = os.environ.get("CLAUDE_SESSION_ID", "")
    flag_file = os.path.expanduser(
        f"$HOME/.claude/session-env/.stop-nudge-{session_id or 'default'}"
    ).replace("$HOME", os.path.expanduser("~"))

    if os.path.exists(flag_file):
        approve()
        return

    # 直近5分のログを確認
    log_file = os.path.expanduser("~/.claude/session-env/operation-log.jsonl")
    now = datetime.now(JST)
    cutoff = now - timedelta(minutes=5)

    recent_edits = 0
    has_test = False

    try:
        with open(log_file) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    op = json.loads(line)
                    ts = op.get("ts", "")
                    op_time = datetime.fromisoformat(ts)
                    if op_time.tzinfo is None:
                        op_time = op_time.replace(tzinfo=JST)
                    if op_time < cutoff:
                        continue

                    if op.get("tool") in ("Write", "Edit"):
                        recent_edits += 1
                    elif op.get("tool") == "Bash":
                        label = op.get("label", "")
                        if any(kw in label for kw in TEST_KEYWORDS):
                            has_test = True
                except Exception:
                    continue
    except FileNotFoundError:
        approve()
        return
    except Exception:
        approve()
        return

    # 2ファイル以上編集 & テスト未実行の場合にナッジ（フラグを立てて1回限り）
    if recent_edits >= 2 and not has_test:
        try:
            os.makedirs(os.path.dirname(flag_file), exist_ok=True)
            with open(flag_file, "w") as f:
                f.write(now.isoformat())
        except Exception:
            pass
        nudge(
            "ファイルを編集しましたがビルド・テストの確認が済んでいません。"
            "ビルドとテストを実行して結果を確認してください。"
            "確認不要な場合はそのまま終了してください。"
        )
    else:
        approve()


if __name__ == "__main__":
    try:
        main()
    finally:
        # Hook使用ログ記録（非同期）
        try:
            subprocess.Popen(
                ["python3", os.path.expanduser("~/.claude/hooks/usage-log.py"), "Hook", os.path.basename(__file__)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass
