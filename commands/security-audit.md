---
name: security-audit
description: "プロジェクトのセキュリティ監査スキル。「セキュリティチェック」「脆弱性スキャン」「security-audit」「秘密鍵が漏れてないか」「npm audit」などのキーワードで起動。.env漏洩・依存パッケージ脆弱性・ハードコード秘密鍵を一括検出する。"
---

# security-audit スキル

プロジェクトのセキュリティ問題を一括検出する。`$ARGUMENTS` にプロジェクトパスを指定できる（省略時はCWD）。

## 実行手順

### 1. スキャン対象の確定

対象ディレクトリを確認し、以下を特定:
- 技術スタック（Node.js / Python / その他）
- `.git` の有無（gitignore確認のため）

### 2. ハードコード秘密情報のスキャン

```bash
# APIキー・パスワード・シークレットのパターンを検索
grep -rn --include="*.ts" --include="*.js" --include="*.py" --include="*.json" \
  -E "(api[_-]?key|secret[_-]?key|password|passwd|token|private[_-]?key)\s*[=:]\s*['\"][^'\"]{8,}['\"]" \
  {対象ディレクトリ}/src/ 2>/dev/null | grep -v node_modules | grep -v dist
```

`.env` ファイルの git トラッキング状態を確認:
```bash
git ls-files | grep -E "\.env$|\.env\."
```

### 3. 依存パッケージの脆弱性スキャン

**Node.js プロジェクトの場合:**
```bash
npm audit --audit-level=moderate 2>/dev/null
```

**Python プロジェクトの場合:**
```bash
pip-audit 2>/dev/null || pip install pip-audit && pip-audit
```

### 4. .gitignore の確認

重要ファイルが適切に除外されているか確認:
```bash
cat .gitignore 2>/dev/null | grep -E "\.env|secrets|credentials|*.key|*.pem"
```

未除外の場合は `.gitignore` への追加を提案。

### 5. 結果レポート

```
## セキュリティ監査レポート - {プロジェクト名}

### 🔴 Critical（即時対応必要）
- {問題}: {詳細}

### 🟡 Warning（対応推奨）
- {問題}: {詳細}

### ✅ 問題なし
{問題がない場合}

### 推奨アクション
1. {アクション1}
2. {アクション2}
```

### 6. 修正支援

Criticalな問題がある場合:
- ハードコード秘密情報 → 環境変数化を提案・実施
- .env の git トラッキング → `git rm --cached .env` を提案

```bash
vv "セキュリティ監査完了なのだ！"
```

依存パッケージの詳細な更新計画（破壊的変更リスク評価・優先度付き）が必要な場合は `/dependency-audit` を使用。
