#!/bin/bash
# PreCompact Hook: compact前に直近の作業コンテキストを保全する

INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path // ""')
TRIGGER=$(echo "$INPUT" | jq -r '.trigger // "unknown"')
CWD=$(echo "$INPUT" | jq -r '.cwd // ""')
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
OUTPUT_FILE="$HOME/.claude/context/last-session.md"

# トランスクリプトのファイル操作ツール呼び出しから最も多く参照されたプロジェクトを検出
DETECTED_PROJECT=""
if [ -f "$TRANSCRIPT" ]; then
  DETECTED_PROJECT=$(jq -r '
    select(type == "object") |
    select(.type == "assistant") |
    .message.content[]? |
    select(.type == "tool_use") |
    select(.name | test("Read|Edit|Write|Glob|Grep")) |
    (.input.file_path // .input.path // .input.pattern // "") |
    select(length > 0) |
    select(startswith("/"))
  ' "$TRANSCRIPT" 2>/dev/null | \
    grep -oE '/[^/]+/[^/]+/work/[^/ ]+' | \
    grep -oE '/[^/]+/[^/]+/work/[^/]+' | \
    sort | uniq -c | sort -rn | awk 'NR==1{print $2}')
fi

# 検出できなかった場合は CWD をフォールバックとして使用
ACTIVE_PROJECT="${DETECTED_PROJECT:-$CWD}"

# トランスクリプトが存在しない場合はスキップ
if [ -z "$TRANSCRIPT" ] || [ ! -f "$TRANSCRIPT" ]; then
  exit 0
fi

# 直近のユーザーメッセージを最大3件・100文字に簡潔化
RECENT_USER=$(jq -r '
  select(type == "object") |
  select(.type == "user") |
  .message.content |
  if type == "array" then
    map(select(.type == "text") | .text) | join(" ")
  elif type == "string" then .
  else ""
  end |
  select(. != "") |
  gsub("\\n"; " ") |
  .[0:100]
' "$TRANSCRIPT" 2>/dev/null | tail -3)

# 直近のアシスタント応答を最大2件・100文字に簡潔化
RECENT_ASSISTANT=$(jq -r '
  select(type == "object") |
  select(.type == "assistant") |
  .message.content |
  if type == "array" then
    map(select(.type == "text") | .text) | join(" ")
  elif type == "string" then .
  else ""
  end |
  select(. != "") |
  gsub("\\n"; " ") |
  .[0:100]
' "$TRANSCRIPT" 2>/dev/null | tail -2)

# コンテキストファイルに書き出し
cat > "$OUTPUT_FILE" << EOF
# Last Session Context
- **日時**: $TIMESTAMP | **プロジェクト**: $ACTIVE_PROJECT
## ユーザー
$(echo "$RECENT_USER" | while IFS= read -r line; do
  [ -n "$line" ] && echo "- $line"
done)
## アシスタント
$(echo "$RECENT_ASSISTANT" | while IFS= read -r line; do
  [ -n "$line" ] && echo "- $line"
done)
EOF

# Obsidian wiki log.md に session エントリを append
if [ -z "$OBSIDIAN_VAULT" ]; then
  printf "OBSIDIAN_VAULT が未設定です。Vault パスを入力してください（空Enter でスキップ）: " >&2
  read -r vault_input </dev/tty
  [ -n "$vault_input" ] && export OBSIDIAN_VAULT="$vault_input"
fi
WIKI_LOG="${OBSIDIAN_VAULT:+$OBSIDIAN_VAULT/log.md}"
if [ -n "$WIKI_LOG" ] && [ -f "$WIKI_LOG" ]; then
  SESSION_SUMMARY=""
  if [ -n "$RECENT_USER" ]; then
    SESSION_SUMMARY=$(echo "$RECENT_USER" | tail -1 | cut -c1-80)
  fi
  printf "\n## [%s] session | compact\n%s\n" \
    "$(date '+%Y-%m-%d %H:%M')" \
    "${SESSION_SUMMARY:-（コンテキスト圧縮）}" >> "$WIKI_LOG"
fi

# Hook使用ログ記録
python3 "$HOME/.claude/hooks/usage-log.py" Hook pre-compact-save.sh &

exit 0
