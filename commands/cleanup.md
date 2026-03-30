---
description: "session-env・plans・shell-snapshots等の古いファイルを整理する。蓄積したセッションファイルをクリーンアップする"
---

# /cleanup - ファイルクリーンアップ

`$ARGUMENTS` で対象を絞り込める（例: `sessions`, `plans`, `all`）。省略時は全カテゴリをスキャン。

## 手順

### 1. 蓄積ファイルのスキャン

以下のディレクトリを調査:

```bash
ls ~/.claude/session-env/ | wc -l   # セッション環境ファイル数
ls ~/.claude/plans/ | wc -l         # プランファイル数
ls ~/.claude/shell-snapshots/ 2>/dev/null | wc -l  # シェルスナップショット数
ls ~/.claude/tasks/ 2>/dev/null | wc -l            # タスクファイル数
du -sh ~/.claude/session-env/ ~/.claude/plans/ 2>/dev/null  # 合計サイズ
```

### 2. 削除候補の特定

以下の基準で削除候補を特定:
- **session-env**: 30日以上前のファイル
- **plans**: 完了・放置されたプランファイル（内容確認後）
- **shell-snapshots**: 30日以上前のファイル
- **tasks**: completedまたはdeleted状態のもの

候補一覧をユーザーに提示する。

### 3. ユーザー確認

```
## クリーンアップ候補

| カテゴリ | 件数 | サイズ | 基準 |
|---------|------|--------|------|
| session-env | XX件 | XX MB | 30日以上前 |
| plans | XX件 | XX KB | 古いプラン |
| shell-snapshots | XX件 | XX KB | 30日以上前 |

削除しますか？（yes/no）
```

### 4. 削除実行

承認されたカテゴリのみ削除:

```bash
# 30日以上前のsession-envを削除
find ~/.claude/session-env/ -mtime +30 -type f -delete

# 指定されたplansを削除
rm ~/.claude/plans/{ファイル名}

# 30日以上前のshell-snapshotsを削除
find ~/.claude/shell-snapshots/ -mtime +30 -type f -delete 2>/dev/null
```

### 5. 完了報告

削除したファイル数と解放したディスクスペースを報告。

```bash
vv "クリーンアップ完了なのだ！スッキリしたのだ"
```
