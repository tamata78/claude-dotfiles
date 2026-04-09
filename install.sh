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
link "commands/commit.md"
link "commands/quick-review.md"
link "commands/debug.md"
link "commands/morning.md"
link "commands/release.md"
link "commands/pr-review.md"
link "commands/cleanup.md"
link "commands/rpi.md"
link "commands/tips.md"
link "commands/dependency-audit.md"
link "commands/project-init.md"
link "commands/security-audit.md"
link "commands/skill-tips.md"

# --- フック ---
echo "--- フック ---"
mkdir -p "${CLAUDE_DIR}/hooks"
link "hooks/pre-compact-save.sh"
link "hooks/risk-analyzer.py"
link "hooks/session-start-snapshot.sh"
link "hooks/operation-logger.py"
link "hooks/post-risk-logger.py"
chmod +x "${DOTFILES_DIR}/hooks/pre-compact-save.sh"
chmod +x "${DOTFILES_DIR}/hooks/session-start-snapshot.sh"

# --- スクリプト ---
echo "--- スクリプト ---"
mkdir -p "${CLAUDE_DIR}/scripts"
link "scripts/statusline-ring.py"

# --- VOICEVOXコマンド ---
echo "--- VOICEVOXコマンド ---"
mkdir -p "${HOME}/.local/bin"
for cmd in vv vv-mute vv-voice; do
  SRC="${DOTFILES_DIR}/scripts/${cmd}"
  DST="${HOME}/.local/bin/${cmd}"
  chmod +x "${SRC}"
  if [ -L "${DST}" ]; then
    rm "${DST}"
  elif [ -e "${DST}" ]; then
    mv "${DST}" "${DST}.bak"
  fi
  ln -s "${SRC}" "${DST}"
  echo "  [link]   ${DST}"
done

# ~/.local/bin を PATH に追加（未追加の場合のみ）
SHELL_RC="${HOME}/.zshrc"
LOCAL_BIN_LINE='export PATH="$HOME/.local/bin:$PATH"'
if ! grep -qF "${LOCAL_BIN_LINE}" "${SHELL_RC}" 2>/dev/null; then
  echo "" >> "${SHELL_RC}"
  echo "# added by claude-dotfiles install.sh" >> "${SHELL_RC}"
  echo "${LOCAL_BIN_LINE}" >> "${SHELL_RC}"
  echo "  [update] ${SHELL_RC} に ~/.local/bin を PATH 追加"
else
  echo "  [skip]   ~/.local/bin は既に PATH に設定済み"
fi

# --- スキル ---
echo "--- スキル ---"
mkdir -p "${CLAUDE_DIR}/skills"
link_dir "skills/claude-md-improver"
link_dir "skills/dependency-audit"
link_dir "skills/dotfiles-sync"
link_dir "skills/feature-dev"
link_dir "skills/project-init"
link_dir "skills/project-snapshot"
link_dir "skills/security-audit"
link_dir "skills/token-audit"

# --- Agent Teams ---
echo "--- Agent Teams ---"
link_dir "agent-teams"

# --- グローバル Git フック ---
echo "--- グローバル Git フック ---"
GLOBAL_HOOKS_DIR="${CLAUDE_DIR}/git-hooks"
mkdir -p "${GLOBAL_HOOKS_DIR}"

# pre-commit hook をリンク
if [ -e "${GLOBAL_HOOKS_DIR}/pre-commit" ] && [ ! -L "${GLOBAL_HOOKS_DIR}/pre-commit" ]; then
  mv "${GLOBAL_HOOKS_DIR}/pre-commit" "${GLOBAL_HOOKS_DIR}/pre-commit.bak"
elif [ -L "${GLOBAL_HOOKS_DIR}/pre-commit" ]; then
  rm "${GLOBAL_HOOKS_DIR}/pre-commit"
fi
ln -s "${DOTFILES_DIR}/git-hooks/pre-commit" "${GLOBAL_HOOKS_DIR}/pre-commit"
chmod +x "${DOTFILES_DIR}/git-hooks/pre-commit"
echo "  [link]   ${GLOBAL_HOOKS_DIR}/pre-commit"

# commit-msg hook をリンク
if [ -L "${GLOBAL_HOOKS_DIR}/commit-msg" ]; then
  rm "${GLOBAL_HOOKS_DIR}/commit-msg"
fi
ln -s "${DOTFILES_DIR}/git-hooks/commit-msg" "${GLOBAL_HOOKS_DIR}/commit-msg"
chmod +x "${DOTFILES_DIR}/git-hooks/commit-msg"
echo "  [link]   ${GLOBAL_HOOKS_DIR}/commit-msg"

# core.hooksPath をグローバル設定（全プロジェクトに適用）
git config --global core.hooksPath "${GLOBAL_HOOKS_DIR}"
echo "  [config] git core.hooksPath -> ${GLOBAL_HOOKS_DIR}"
echo ""
echo "  注意: プロジェクト固有のhookは .git/hooks/pre-commit.local に"
echo "        リネームするか、husky/.lefthook を使えば自動チェーンされます"

# --- 旧 pre-push hook のクリーンアップ ---
REPO_GIT_HOOKS="${DOTFILES_DIR}/.git/hooks"
if [ -L "${REPO_GIT_HOOKS}/pre-push" ]; then
  rm "${REPO_GIT_HOOKS}/pre-push"
  echo "  [cleanup] 旧 .git/hooks/pre-push シンボリックリンクを削除"
fi

# --- ホームディレクトリのdotfiles ---
echo "--- ホームディレクトリ ---"
link_home() {
  local src="${DOTFILES_DIR}/${1}"
  local dst="${HOME}/${1}"

  if [ -e "${dst}" ] && [ ! -L "${dst}" ]; then
    echo "  [backup] ${dst} -> ${dst}.bak"
    mv "${dst}" "${dst}.bak"
  elif [ -L "${dst}" ]; then
    rm "${dst}"
  fi

  ln -s "${src}" "${dst}"
  echo "  [link]   ${dst}"
}
link_home ".tmux.conf"

# --- TPM (Tmux Plugin Manager) ---
echo "--- TPM ---"
TPM_DIR="${HOME}/.tmux/plugins/tpm"
if [ -d "${TPM_DIR}" ]; then
  echo "  [skip]   TPM already installed at ${TPM_DIR}"
else
  git clone https://github.com/tmux-plugins/tpm "${TPM_DIR}"
  echo "  [clone]  ${TPM_DIR}"
fi

# プラグインを自動インストール (tmuxセッションが不要なバッチモード)
if command -v tmux &>/dev/null && [ -f "${HOME}/.tmux.conf" ]; then
  echo "  [install] tmux plugins via TPM..."
  TMUX_PLUGIN_MANAGER_PATH="${HOME}/.tmux/plugins/" "${TPM_DIR}/bin/install_plugins"
  echo "  [done]   tmux plugins installed"
fi

echo ""
echo "==> インストール完了"
echo ""
echo "注意:"
echo "  - プライベートファイル (commands/kamiya-news.md, projects/*/memory/) は管理対象外です"
echo "  - マシン固有の設定は ~/.claude/settings.local.json で管理してください"
