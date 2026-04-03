#!/usr/bin/env python3
"""
Claude Code PermissionRequest hook - リスクレベルと説明を表示する
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))


def get_risk_info(tool_name, tool_input):
    """ツール呼び出しのリスクレベルと説明を返す"""
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        return analyze_bash_risk(command)
    elif tool_name == "Edit":
        file_path = tool_input.get("file_path", "")
        return analyze_file_risk("編集", file_path)
    elif tool_name == "Write":
        file_path = tool_input.get("file_path", "")
        return analyze_file_risk("作成/上書き", file_path)
    elif tool_name == "WebFetch":
        url = tool_input.get("url", "")
        return "🟢 低リスク", f"URLを取得: {url[:80]}"
    elif tool_name == "WebSearch":
        query = tool_input.get("query", "")
        return "🟢 低リスク", f"Web検索: {query[:60]}"
    elif tool_name == "Agent":
        agent_type = tool_input.get("subagent_type", "unknown")
        return "🟡 中リスク", f"サブエージェントを起動: {agent_type}"
    elif tool_name in ("Read", "Glob", "Grep", "ToolSearch", "TaskGet", "TaskList", "TaskOutput"):
        return "🟢 低リスク", f"ツール実行: {tool_name}"
    elif tool_name in ("ExitPlanMode", "ExitWorktree", "AskUserQuestion"):
        return "🟢 低リスク", f"ツール実行: {tool_name}"
    else:
        return "🟡 中リスク", f"ツール実行: {tool_name}"


def analyze_bash_risk(command):
    cmd = command.strip()

    # 高リスクパターン
    high_risk = [
        (r"\brm\s+(-[rf]+\s+|--recursive|--force)", "ファイル/ディレクトリを削除"),
        (r"\bgit\s+push\s+--force\b|\bgit\s+push\s+-f\b|\bgit\s+force-push\b", "強制プッシュ"),
        (r"\bgit\s+push\b(?!.*--dry-run)", "リモートリポジトリにプッシュ"),
        (r"\bgit\s+push\s+.*--delete\b|\bgit\s+push\s+.*:(?!\s)", "リモートブランチを削除"),
        (r"\bgit\s+reset\s+--hard\b", "コミット履歴を強制リセット"),
        (r"\bgit\s+rebase\b", "ブランチをリベース"),
        (r"\bkill\b|\bpkill\b|\bkillall\b", "プロセスを強制終了"),
        (r"\bchmod\s+-R\s+777\b", "全ファイルのパーミッションを777に変更（危険）"),
        (r"\bsudo\b", "管理者権限でコマンドを実行"),
        (r"\bdropdb\b|\bDROP\s+TABLE\b|\bDROP\s+DATABASE\b", "データベースを削除"),
        (r"\bmkfs\b|\bnewfs\b|\bdiskutil\s+erase", "ディスクをフォーマット"),
        (r"\bdd\s+if=", "ディスクイメージを直接書き込み"),
    ]
    for pattern, desc in high_risk:
        if re.search(pattern, cmd, re.IGNORECASE):
            return "🔴 高リスク", desc

    # 中リスクパターン
    medium_risk = [
        (r"\bgit\s+(add|commit)\b", "Gitで変更をステージ/コミット"),
        (r"\bgit\s+(merge|checkout\s+-b|branch\s+-[dD])\b", "Gitブランチ操作"),
        (r"\bgit\s+stash\b", "Gitスタッシュ操作"),
        (r"\bnpm\s+(install|uninstall|update|ci)\b", "npmパッケージを管理"),
        (r"\bpip\s+(install|uninstall)\b", "Pythonパッケージを管理"),
        (r"\bbrew\s+(install|uninstall|upgrade)\b", "Homebrewパッケージを管理"),
        (r"\bnpm\s+run\b|\bnpm\s+(test|build|start|publish)\b", "npmスクリプトを実行"),
        (r"\bpython3?\s+\S+\.py\b", "Pythonスクリプトを実行"),
        (r"\bmkdir\b", "ディレクトリを作成"),
        (r"\bcp\b|\bmv\b", "ファイルをコピー/移動"),
        (r"\bcurl\b|\bwget\b", "HTTPリクエストを送信"),
        (r"\bchmod\b|\bchown\b", "ファイルのパーミッション/所有者を変更"),
        (r"\btouch\b", "ファイルを作成"),
        (r"\bdocker\b", "Dockerコマンドを実行"),
    ]
    for pattern, desc in medium_risk:
        if re.search(pattern, cmd, re.IGNORECASE):
            return "🟡 中リスク", desc

    # 低リスクパターン
    low_risk = [
        (r"\bgit\s+(status|diff|log|show|branch|stash\s+list|remote|config)\b", "Gitの状態を確認"),
        (r"\b(ls|ll|pwd|echo|cat|head|tail|wc|file)\b", "ファイル/ディレクトリを参照"),
        (r"\b(grep|rg|find|fzf|awk|sed)\b", "ファイルを検索/フィルタ"),
        (r"\bnpm\s+(list|audit|outdated|info)\b", "npmパッケージ情報を確認"),
        (r"\b(which|type|env|printenv|whoami|id)\b", "環境情報を確認"),
        (r"\b\S+\s+--version\b|\b\S+\s+-v\b", "バージョンを確認"),
        (r"\bvv\b", "音声通知を送信"),
        (r"\bopen\b", "ファイル/URLを開く"),
    ]
    for pattern, desc in low_risk:
        if re.search(pattern, cmd, re.IGNORECASE):
            return "🟢 低リスク", desc

    return "🟡 中リスク", "コマンドを実行"


def analyze_file_risk(action, file_path):
    name = file_path.split("/")[-1] if "/" in file_path else file_path

    high_risk_files = [".env", "secrets", "credentials", "id_rsa", "private_key", "token"]
    if any(p in file_path.lower() for p in high_risk_files):
        return "🔴 高リスク", f"機密ファイルを{action}: {name}"

    config_files = [
        "package.json", "Dockerfile", ".github", "settings.json",
        "config", ".bashrc", ".zshrc", ".gitconfig", "webpack", "tsconfig",
    ]
    if any(p in file_path.lower() for p in config_files):
        return "🟡 中リスク", f"設定ファイルを{action}: {name}"

    return "🟢 低リスク", f"ファイルを{action}: {name}"


def format_command_preview(tool_name, tool_input):
    """コマンドの概要を短く表示する"""
    if tool_name == "Bash":
        cmd = tool_input.get("command", "")
        # 長すぎる場合は省略
        if len(cmd) > 100:
            cmd = cmd[:97] + "..."
        return cmd
    elif tool_name in ("Edit", "Write"):
        return tool_input.get("file_path", "")
    elif tool_name == "WebFetch":
        return tool_input.get("url", "")
    return ""


def log_permission_request(tool_name, tool_input, risk_level, description, decision):
    """PermissionRequest の発生をログに記録する"""
    log_dir = os.path.expanduser("~/.claude/session-env")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "permission-requests.jsonl")

    entry = {
        "ts": datetime.now(JST).isoformat(),
        "tool": tool_name,
        "risk": risk_level,
        "description": description,
        "decision": decision,
    }

    if tool_name == "Bash":
        entry["command"] = tool_input.get("command", "")[:200]
    elif tool_name in ("Edit", "Write"):
        entry["file_path"] = tool_input.get("file_path", "")
    elif tool_name == "Agent":
        entry["subagent_type"] = tool_input.get("subagent_type", "")

    try:
        with open(log_file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)

        tool_name = data.get("tool_name", "Unknown")
        tool_input = data.get("tool_input", {})

        risk_level, description = get_risk_info(tool_name, tool_input)
        preview = format_command_preview(tool_name, tool_input)

        # stderrにリスク情報を出力 → 承認ダイアログにコメントとして表示される
        lines = [f"{risk_level}  {description}"]
        if preview:
            lines.append(f"$ {preview}" if tool_name == "Bash" else f"  {preview}")

        reason = "\n".join(lines)
        print(reason, file=sys.stderr)

        decision = "allow" if risk_level.startswith("🟢") else "ask"
        result = {
            "permissionDecision": decision,
            "reason": reason,
        }
        print(json.dumps(result, ensure_ascii=False))

        # ログ記録: PermissionRequest が発生したコマンドを保存
        log_permission_request(tool_name, tool_input, risk_level, description, decision)

    except Exception:
        # エラー時はそのまま通常の承認フローへ
        sys.exit(0)
    finally:
        # Hook使用ログ記録（非同期）
        try:
            subprocess.Popen(
                ["python3", os.path.expanduser("~/.claude/hooks/usage-log.py"), "Hook", os.path.basename(__file__)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass


if __name__ == "__main__":
    main()
