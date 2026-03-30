---
description: "リリースワークフロー。コードレビュー→テスト→バージョンバンプ→CHANGELOG→commit→push→デプロイの一連フローを実行する"
---

# /release - リリースワークフロー

`$ARGUMENTS` にバージョン番号（例: `1.2.0`）またはリリースタイプ（`patch`, `minor`, `major`）を渡す。

## 手順

### 1. 事前チェック

```bash
git status           # 未コミット変更がないことを確認
git log --oneline -5  # 最近のコミットを確認
```

未コミット変更がある場合は「コミットしてから実行してください」と通知して終了。

### 2. コードレビュー

`/quick-review` の手順に従って、前回リリース以降の変更をレビューする。

```bash
git log v{前バージョン}..HEAD --oneline  # 変更一覧
git diff v{前バージョン}..HEAD           # 差分
```

Criticalな問題があれば修正を促して終了。

### 3. テスト実行

プロジェクトのテストコマンドを実行:
- Node.js: `npm test` または `npm run test`
- Python: `pytest`

テストが失敗した場合は修正を促して終了。

### 4. バージョンバンプ

`package.json` がある場合:
```bash
npm version {patch|minor|major}
# または手動でバージョン番号を変更
```

`pyproject.toml` / `setup.py` の場合は手動で変更。

### 5. CHANGELOG 生成

前回リリース以降のコミットから CHANGELOG エントリを生成:

```markdown
## v{新バージョン} - {日付}

### Added
- {新機能のコミット}

### Fixed
- {バグ修正のコミット}

### Changed
- {変更のコミット}
```

`CHANGELOG.md` が存在する場合は冒頭に追加。存在しない場合は作成。

### 6. コミット & タグ

```bash
git add CHANGELOG.md package.json   # バージョン関連ファイル
git commit -m "chore: release v{新バージョン}"
git tag v{新バージョン}
```

### 7. Push

ユーザーに確認してから実行:
> 「`git push && git push --tags` を実行しますか？」

### 8. デプロイ（プロジェクト固有）

プロジェクトの CLAUDE.md にデプロイ手順がある場合は案内する。
launchd 管理のサービスは:
```bash
launchctl unload ... && launchctl load ...
```

### 9. 完了通知

```bash
vv "リリース完了なのだ！バージョン{新バージョン}をリリースしたのだ"
```
