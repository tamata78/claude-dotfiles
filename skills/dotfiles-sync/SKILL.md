---
name: dotfiles-sync
description: claude-dotfilesリポジトリに共通設定を同期するスキル。「dotfilesに反映して」「claude-dotfilesを更新して」「設定を同期して」「新しいスキルをdotfilesに追加して」「dotfilesにpushして」「dotfilesを整理して」などと言われたときは必ずこのスキルを使うこと。~/.claude/の変更・新規ファイルを分析し、ポータブルな設定のみをclaude-dotfilesに反映する。
---

# dotfiles-sync

`~/.claude/` の変更をclaude-dotfilesリポジトリに同期するスキル。

**シンボリックリンク方式**のため、すでにdotfiles管理下のファイルは自動的に同期済み。
このスキルの主な役割は「まだdotfilesに入っていない新規ファイル」の発見・分類・追加。

## ステップ1: dotfilesリポジトリを特定する

```bash
# よくある場所を探す
ls ~/work/claude-dotfiles 2>/dev/null || ls ~/claude-dotfiles 2>/dev/null || find ~ -maxdepth 3 -name "install.sh" -path "*/claude-dotfiles/*" 2>/dev/null | head -1
```

見つかったパスを `DOTFILES_DIR` として以降の処理で使う。

## ステップ2: 未管理ファイルを発見する

`~/.claude/` にあるファイルのうち、dotfilesへのシンボリックリンクでないものを列挙する。

```bash
CLAUDE_DIR="$HOME/.claude"
# シンボリックリンクでないファイルを列挙（.gitignore対象・除外パターンを除く）
find "$CLAUDE_DIR" -maxdepth 3 \( -type f -o -type d \) ! -type l \
  ! -path "*/.git/*" \
  ! -path "*/memory/*" \
  ! -path "*/context/*" \
  ! -path "*/projects/*" \
  ! -path "*/.bak" \
  ! -name "*.bak" \
  ! -name "settings.local.json" \
  | sort
```

dotfilesへのシンボリックリンクであるファイルは管理済みなのでスキップ。

## ステップ3: 共通 vs プライベートの分類

各ファイルを以下の基準で分類する。

### 共通（dotfilesに入れるべき）

| パス | 説明 |
|---|---|
| `CLAUDE.md` | グローバルルール |
| `voicevox-scripts.md` | 音声通知スクリプト集 |
| `settings.json` | ベース設定（ローカル固有でない） |
| `commands/*.md` | 汎用スラッシュコマンド |
| `hooks/*.sh`, `hooks/*.py` | フックスクリプト |
| `scripts/*.py` | ユーティリティスクリプト |
| `skills/*/SKILL.md` および関連ファイル | スキル定義 |
| `agent-teams/**` | エージェントチーム設定 |
| `git-hooks/*` | gitフック |

### プライベート（dotfilesに入れない）

| パス | 理由 |
|---|---|
| `settings.local.json` | マシン固有設定 |
| `commands/kamiya-news.md` | 個人用コマンド |
| `memory/**` | プロジェクトメモリ（個人データ） |
| `context/**` | セッションコンテキスト（一時的） |
| `projects/**` | プロジェクト固有ファイル |
| `*.bak` | バックアップファイル |
| `plugins/cache/**` | プラグインキャッシュ |

**プライベート判定のヒント（判断に迷う場合）：**
- ファイル名に `personal`/`private`/`local`/`my-` などを含む → プライベート候補
- ファイル内容に固有名詞（プロジェクト名・サービス名）が多い → プライベート候補
- 上記に該当する場合はユーザーに確認してから追加する

## ステップ4: ポータビリティチェック

共通と分類したファイルについて、以下を検証する。

### ローカルパスチェック
```bash
grep -En '/Users/[^/]+' "$file" 2>/dev/null
```
見つかった場合は `$HOME` に置き換えるよう提案する。

### 秘匿情報チェック
```bash
grep -EnP '(?i)(password|secret|token|api_key)\s*[:=]\s*\S{6,}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{36}|-----BEGIN.*PRIVATE KEY' "$file" 2>/dev/null
```
見つかった場合はdotfilesへの追加をブロックし、ユーザーに報告する。

## ステップ5: ユーザーへの確認と同期計画の提示

以下の形式でレポートを提示し、確認を取る：

```
📋 dotfiles同期レポート
========================

✅ 管理済み（シンボリックリンク済み）:
  - settings.json → dotfiles
  - CLAUDE.md → dotfiles
  ...

🆕 新規・未管理ファイル:
  [共通] skills/my-new-skill/SKILL.md → dotfilesに追加推奨
  [プライベート] commands/personal-cmd.md → 除外（個人用）
  [要確認] hooks/new-hook.sh → 共通？プライベート？

⚠️ 問題あり（要修正）:
  - scripts/foo.py: ローカルパス /Users/username/ を含む
```

同期してよいか確認してから次のステップへ進む。

## ステップ6: dotfilesへのコピーと install.sh の更新

ユーザーが承認したファイルについて：

1. **ファイルをdotfilesにコピー**
   ```bash
   cp "$HOME/.claude/$relative_path" "$DOTFILES_DIR/$relative_path"
   ```

2. **install.sh を更新**（新規ファイルの場合）

   ファイルの種類に応じて適切なセクションに `link` または `link_dir` を追加する。
   既存の `install.sh` のパターンに合わせること。

3. **シンボリックリンクに変換**
   ```bash
   rm "$HOME/.claude/$relative_path"
   ln -s "$DOTFILES_DIR/$relative_path" "$HOME/.claude/$relative_path"
   ```
   これ以降は dotfiles 経由で管理される。

## ステップ7: git差分の確認・自動コミット・push促進

```bash
cd "$DOTFILES_DIR"
git diff
git status
```

変更内容をユーザーに見せた後、**自動的に以下を実行する**：

```bash
cd "$DOTFILES_DIR"
git add -A
git commit -m "<変更内容を端的に表すメッセージ>"
```

コミット完了後、必ず以下のメッセージをユーザーに伝える：

```
✅ コミット完了！

リモートへのpushは手動で行ってください：
  git push

または確認してからpush：
  git log origin/main..HEAD  # pushされる内容を確認
  git push
```

**pushは絶対に自動で実行しない。** ユーザーが明示的に依頼した場合のみ実行する。

## ステップ8: Dev Portal設定同期（オプション）

dotfilesの変更をDev Portalのデータにも反映する。

```bash
# Dev Portalリポジトリを探す
DEV_PORTAL_DIR=""
for candidate in "$HOME/work/dev_portal" "$HOME/dev_portal"; do
  if [ -f "$candidate/portal.config.json" ]; then
    DEV_PORTAL_DIR="$candidate"
    break
  fi
done
```

- **見つかった場合**: 以下を実行する
  ```bash
  cd "$DEV_PORTAL_DIR" && npm run sync
  ```
  完了したらユーザーに「Dev Portalの設定同期も完了しました」と報告する。

- **見つからなかった場合**: サイレントスキップ。エラーにしない。ユーザーへの報告も不要。

※ `data/` はgit管理外のため、このステップでコミット・pushは不要。

## 注意事項

- **`.bak` ファイルは無視する** - install.sh が生成するバックアップであり管理対象外
- **plugins/cache/ は無視する** - プラグインのキャッシュは自動生成物
- **install.sh の冪等性を維持する** - 同じファイルへのリンクが重複しないよう確認する
- **新しいスキルを追加する場合は `link_dir` を使う** - ディレクトリごとリンクする
- **Dev Portal同期はオプション** - `portal.config.json` の存在で判定。dev_portalがない環境ではスキップされる
