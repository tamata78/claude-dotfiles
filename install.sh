#!/usr/bin/env bash
# install.sh — claude-dotfiles セットアップスクリプト
# ~/.claude/ 配下に本リポジトリのファイルへのシンボリックリンクを作成する
# 冪等: 再実行しても安全。既存ファイルは .bak にバックアップしてから置換。

set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${HOME}/.claude"

echo "==> claude-dotfiles インストール開始"
echo "    ソース: ${DOTFILES_DIR}"
echo "    ターゲット: ${CLAUDE_DIR}"
echo ""

# --- ヘルパー ---
link() {
  local src="${DOTFILES_DIR}/${1}"
  local dst="${CLAUDE_DIR}/${1}"
  local dst_dir
  dst_dir="$(dirname "${dst}")"

  # 親ディレクトリがなければ作成
  mkdir -p "${dst_dir}"

  # 既存ファイル/リンクがある場合はバックアップ
  if [ -e "${dst}" ] && [ ! -L "${dst}" ]; then
    echo "  [backup] ${dst} -> ${dst}.bak"
    mv "${dst}" "${dst}.bak"
  elif [ -L "${dst}" ]; then
    # 既存シンボリックリンクは上書き
    rm "${dst}"
  fi

  ln -s "${src}" "${dst}"
  echo "  [link]   ${dst}"
}

link_dir() {
  local src="${DOTFILES_DIR}/${1}"
  local dst="${CLAUDE_DIR}/${1}"

  if [ -e "${dst}" ] && [ ! -L "${dst}" ]; then
    echo "  [backup] ${dst} -> ${dst}.bak"
    mv "${dst}" "${dst}.bak"
  elif [ -L "${dst}" ]; then
    rm "${dst}"
  fi

  ln -s "${src}" "${dst}"
  echo "  [link]   ${dst}/"
}

# --- ルールファイル ---
echo "--- ルール ---"
link "CLAUDE.md"
link "voicevox-scripts.md"

# --- 設定 ---
echo "--- 設定 ---"
link "settings.json"

# --- コマンド ---
echo "--- コマンド ---"
mkdir -p "${CLAUDE_DIR}/commands"
link "commands/review-rules.md"
link "commands/team.md"

# --- フック ---
echo "--- フック ---"
mkdir -p "${CLAUDE_DIR}/hooks"
link "hooks/pre-compact-save.sh"
link "hooks/risk-analyzer.py"
chmod +x "${DOTFILES_DIR}/hooks/pre-compact-save.sh"

# --- スクリプト ---
echo "--- スクリプト ---"
mkdir -p "${CLAUDE_DIR}/scripts"
link "scripts/statusline-ring.py"

# --- スキル ---
echo "--- スキル ---"
mkdir -p "${CLAUDE_DIR}/skills"
link_dir "skills/claude-md-improver"
link_dir "skills/feature-dev"
link_dir "skills/prompt-review"
link_dir "skills/skill-creator"

# --- Agent Teams ---
echo "--- Agent Teams ---"
link_dir "agent-teams"

echo ""
echo "==> インストール完了"
echo ""
echo "注意:"
echo "  - プライベートファイル (commands/kamiya-news.md, projects/*/memory/) は管理対象外です"
echo "  - マシン固有の設定は ~/.claude/settings.local.json で管理してください"
