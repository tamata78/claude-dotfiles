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

# 直近のユーザーメッセージを最大5件抽出
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
  .[0:200]
' "$TRANSCRIPT" 2>/dev/null | tail -5)

# 直近のアシスタントメッセージを最大3件抽出
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
  .[0:300]
' "$TRANSCRIPT" 2>/dev/null | tail -3)

# コンテキストファイルに書き出し
cat > "$OUTPUT_FILE" << EOF
# Last Session Context

- **保全日時**: $TIMESTAMP
- **セッションID**: $SESSION_ID
- **作業ディレクトリ**: $CWD
- **作業プロジェクト**: $ACTIVE_PROJECT
- **Compactトリガー**: $TRIGGER

## 直近のユーザーメッセージ（最大5件）

$(echo "$RECENT_USER" | while IFS= read -r line; do
  [ -n "$line" ] && echo "- $line"
done)

## 直近のアシスタント応答（最大3件）

$(echo "$RECENT_ASSISTANT" | while IFS= read -r line; do
  [ -n "$line" ] && echo "- $line"
done)
EOF

exit 0
