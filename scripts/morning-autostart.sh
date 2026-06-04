#!/bin/bash
# 5:00 以降の最初の PC 起動時に tmux `claude` セッション + claude 対話モードを Terminal で開く
set -euo pipefail

LOG="$HOME/.local/log/morning-autostart.log"
FLAG="$HOME/.cache/morning-autostart-last"
TODAY=$(date +%Y-%m-%d)
HOUR=$(date +%H)
SESSION="claude"
WD="$HOME/work/time-tracker"
TMUX_BIN="/usr/local/bin/tmux"

mkdir -p "$(dirname "$LOG")" "$(dirname "$FLAG")"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] trigger fired" >> "$LOG"

# Guard 1: 5:00 未満ならスキップ（深夜起動時の暴発防止）
if [ "$HOUR" -lt 5 ]; then
  echo "[$(date '+%H:%M:%S')] skip: hour=$HOUR < 5" >> "$LOG"
  exit 0
fi

# Guard 2: 今日既に起動済みならスキップ（RunAtLoad + StartCalendarInterval の両発火対策）
if [ -f "$FLAG" ] && [ "$(cat "$FLAG")" = "$TODAY" ]; then
  echo "[$(date '+%H:%M:%S')] skip: already ran today" >> "$LOG"
  exit 0
fi

echo "$TODAY" > "$FLAG"

# tmux セッションの存在チェック
if "$TMUX_BIN" has-session -t "$SESSION" 2>/dev/null; then
  echo "[$(date '+%H:%M:%S')] session '$SESSION' already exists — will only attach (no kill, no re-layout, no claude launch)" >> "$LOG"
else
  echo "[$(date '+%H:%M:%S')] creating new tmux session '$SESSION' with 4-pane layout" >> "$LOG"
  # ~/.tmux.conf の `bind M` と同じ分割手順を再現
  "$TMUX_BIN" new-session -d -s "$SESSION" -c "$WD"
  "$TMUX_BIN" split-window -h -t "$SESSION"
  "$TMUX_BIN" split-window -v -t "$SESSION"
  "$TMUX_BIN" select-pane -L -t "$SESSION"
  "$TMUX_BIN" split-window -v -t "$SESSION"
  "$TMUX_BIN" select-pane -t "${SESSION}:.1"

  # pane 1.2（右上）で claude を起動 + 朝のスキル案内
  "$TMUX_BIN" send-keys -t "${SESSION}:.2" \
    "clear && echo '☀️ おはよう。今朝打つスキル:' && echo '   /morning-life' && echo '   /vault-daily-brief' && echo '   /furikaeri  (前日分の振り返り)' && echo '' && claude" C-m
fi

# tmux セッションが既に attach 済みなら Terminal を前面に出すだけ。未 attach なら新しく開く
ATTACHED=$("$TMUX_BIN" list-sessions -F '#{session_name}:#{session_attached}' 2>/dev/null \
  | grep "^${SESSION}:" | cut -d: -f2 || echo "0")

if [ "${ATTACHED:-0}" -ge 1 ]; then
  echo "[$(date '+%H:%M:%S')] tmux session already attached — activating Terminal only" >> "$LOG"
  /usr/bin/osascript -e 'tell application "Terminal" to activate' 2>/dev/null || true
else
  echo "[$(date '+%H:%M:%S')] opening Terminal with tmux attach" >> "$LOG"
  /usr/bin/osascript <<APPLESCRIPT
tell application "Terminal"
  activate
  do script "$TMUX_BIN attach -t $SESSION"
end tell
APPLESCRIPT
fi

# VOICEVOX 通知
"$HOME/.local/bin/vv" "おはようなのだ。クロードのtmuxを起動したよ" || true

echo "[$(date '+%H:%M:%S')] done" >> "$LOG"
