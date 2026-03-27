#!/usr/bin/env python3
"""Token audit scanner - ~/.claude/ 配下のトークン消費要因を分析する"""
import json
import os
import sys
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
BYTES_PER_TOKEN = 3  # 日本語混在テキストの概算


def scan_file_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    elif path.is_dir():
        return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    return 0


def find_bak_files() -> list[dict]:
    results = []
    for p in CLAUDE_DIR.rglob("*.bak"):
        size = scan_file_size(p)
        results.append({"path": str(p), "size": size, "type": "dir" if p.is_dir() else "file"})
    for p in CLAUDE_DIR.glob("skills/*.bak"):
        if p.is_dir():
            size = scan_file_size(p)
            results.append({"path": str(p), "size": size, "type": "dir"})
    return results


def scan_claude_md() -> list[dict]:
    results = []
    global_md = CLAUDE_DIR / "CLAUDE.md"
    if global_md.exists():
        size = global_md.stat().st_size
        results.append({"name": "Global CLAUDE.md", "path": str(global_md), "size": size, "load": "every_turn"})

    cwd_md = Path.cwd() / "CLAUDE.md"
    if cwd_md.exists() and cwd_md != global_md:
        size = cwd_md.stat().st_size
        results.append({"name": "Project CLAUDE.md", "path": str(cwd_md), "size": size, "load": "every_turn"})

    # Check for plugin CLAUDE.md files
    plugins_dir = CLAUDE_DIR / "plugins"
    if plugins_dir.exists():
        for md in plugins_dir.rglob("CLAUDE.md"):
            size = md.stat().st_size
            results.append({"name": f"Plugin CLAUDE.md ({md.parent.name})", "path": str(md), "size": size, "load": "every_turn"})
    return results


def scan_skills() -> list[dict]:
    results = []
    skills_dir = CLAUDE_DIR / "skills"
    if not skills_dir.exists():
        return results
    for d in sorted(skills_dir.iterdir()):
        if d.is_dir():
            size = scan_file_size(d)
            is_bak = d.name.endswith(".bak")
            results.append({"name": d.name, "path": str(d), "size": size, "is_bak": is_bak})
    return results


def scan_plugin_cache() -> list[dict]:
    results = []
    cache_dir = CLAUDE_DIR / "plugins" / "cache"
    if not cache_dir.exists():
        return results
    for plugin_dir in sorted(cache_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue
        for skill_dir in sorted(plugin_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            versions = [v for v in skill_dir.iterdir() if v.is_dir()]
            total_size = sum(scan_file_size(v) for v in versions)
            results.append({
                "name": f"{plugin_dir.name}/{skill_dir.name}",
                "path": str(skill_dir),
                "versions": len(versions),
                "total_size": total_size,
            })
    return results


def scan_memory() -> dict:
    memory_dirs = list(CLAUDE_DIR.glob("projects/*/memory"))
    total_size = 0
    file_count = 0
    for d in memory_dirs:
        for f in d.rglob("*.md"):
            total_size += f.stat().st_size
            file_count += 1
    return {"total_size": total_size, "file_count": file_count, "dirs": [str(d) for d in memory_dirs]}


def scan_settings() -> dict:
    settings = CLAUDE_DIR / "settings.json"
    if settings.exists():
        return {"path": str(settings), "size": settings.stat().st_size}
    return {"path": str(settings), "size": 0}


def scan_auxiliary_files() -> list[dict]:
    """CLAUDE.mdから参照される補助ファイル等"""
    results = []
    candidates = [
        CLAUDE_DIR / "voicevox-scripts.md",
        CLAUDE_DIR / "context" / "last-session.md",
    ]
    for f in candidates:
        if f.exists():
            results.append({"name": f.name, "path": str(f), "size": f.stat().st_size})
    return results


def main():
    report = {
        "claude_md": scan_claude_md(),
        "skills": scan_skills(),
        "plugin_cache": scan_plugin_cache(),
        "memory": scan_memory(),
        "settings": scan_settings(),
        "bak_files": find_bak_files(),
        "auxiliary": scan_auxiliary_files(),
        "bytes_per_token": BYTES_PER_TOKEN,
    }
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
