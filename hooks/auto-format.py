#!/usr/bin/env python3
"""PostToolUse フック: Write/Edit後にファイルを自動フォーマット（非同期）

対応フォーマッター:
- prettier (JS/TS/CSS/JSON/YAML)
- black (Python)
- gofmt (Go)
- rustfmt (Rust)
"""
import json
import sys
import os
import subprocess


def command_exists(cmd: str) -> bool:
    return subprocess.run(["which", cmd], capture_output=True).returncode == 0


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name not in ("Write", "Edit"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path or not os.path.isfile(file_path):
        sys.exit(0)

    ext = os.path.splitext(file_path)[1].lstrip(".")

    try:
        if ext in ("js", "jsx", "ts", "tsx", "css", "json", "yaml", "yml", "md"):
            # プロジェクトローカルの prettier を優先
            local_prettier = os.path.join(os.getcwd(), "node_modules", ".bin", "prettier")
            if os.path.exists(local_prettier):
                subprocess.run(
                    [local_prettier, "--write", "--log-level", "silent", file_path],
                    capture_output=True,
                    timeout=15,
                )
            elif command_exists("prettier"):
                subprocess.run(
                    ["prettier", "--write", "--log-level", "silent", file_path],
                    capture_output=True,
                    timeout=15,
                )

        elif ext == "py":
            if command_exists("black"):
                subprocess.run(
                    ["black", "--quiet", file_path],
                    capture_output=True,
                    timeout=15,
                )

        elif ext == "go":
            if command_exists("gofmt"):
                subprocess.run(
                    ["gofmt", "-w", file_path],
                    capture_output=True,
                    timeout=10,
                )

        elif ext == "rs":
            if command_exists("rustfmt"):
                subprocess.run(
                    ["rustfmt", file_path],
                    capture_output=True,
                    timeout=10,
                )

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
