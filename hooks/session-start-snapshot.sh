#!/bin/bash
# セッション開始時にプロジェクトのスナップショットを自動読み込みする
SNAPSHOT="$PWD/.claude/snapshot.md"
REVIEW="$PWD/.claude/snapshot-review.md"

# セッション開始時刻を記録（StatusLine経過時間表示用）
SESSION_ENV_DIR="$HOME/.claude/session-env"
mkdir -p "$SESSION_ENV_DIR"
date +%s.%N > "$SESSION_ENV_DIR/current-start" 2>/dev/null || date +%s > "$SESSION_ENV_DIR/current-start"

# 30日以上前のsession-envファイルを自動削除
find "$SESSION_ENV_DIR" -maxdepth 1 -type f -mtime +30 -not -name "current-start" -delete 2>/dev/null

if [ -f "$SNAPSHOT" ]; then
    export SNAPSHOT_PATH="$SNAPSHOT"
    export REVIEW_PATH="$REVIEW"
    python3 -c "
import json, os

snapshot_path = os.environ['SNAPSHOT_PATH']
review_path = os.environ.get('REVIEW_PATH', '')

with open(snapshot_path) as f:
    snapshot_content = f.read()

# 品質レビューが存在すればスコア合計行のみ抽出（トークン節約）
review_section = ''
if review_path and os.path.exists(review_path):
    with open(review_path) as f:
        review_content = f.read()
    blocks = [b for b in review_content.split('\n## ') if b.strip()]
    if blocks:
        latest = blocks[-1].strip()
        score_line = next((l for l in latest.splitlines() if '合計:' in l or 'Total:' in l), None)
        date_line = latest.splitlines()[0] if latest else ''
        if score_line:
            review_section = f'\n\n---\n### 前回レビュー: {date_line} — {score_line.strip()}'

# 分析指示テキスト
instruction = '''

---
📋 スナップショットを読み込みました。
このセッション終了時または /project-snapshot 実行時に、
上記スナップショットの品質を .claude/snapshot-review.md に記録してください。
既にレビューがある場合は、低スコア項目をスナップショット更新で改善してください。'''

context = snapshot_content + review_section + instruction

print(json.dumps({
    'hookSpecificOutput': {
        'hookEventName': 'SessionStart',
        'additionalContext': '## プロジェクトスナップショット (自動読み込み)\n\n' + context
    }
}))
"
fi

# Hook使用ログ記録
python3 "$HOME/.claude/hooks/usage-log.py" Hook session-start-snapshot.sh &
