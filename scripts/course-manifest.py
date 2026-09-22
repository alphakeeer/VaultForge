#!/usr/bin/env python3
"""生成课程增量清单，不修改课程目录。

用法:
  python3 scripts/course-manifest.py <course_dir> --output manifest.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


SOURCE_EXTENSIONS = {".pdf", ".ppt", ".pptx", ".md", ".txt", ".doc", ".docx", ".html", ".htm"}
GENERATED_DIRS = {"01. 课程笔记", "02. 知识卡片"}
GENERATED_FILES = {"00. 课程索引.md"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    result: dict[str, str] = {}
    for line in text[3:end].splitlines():
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.+)$", line.strip())
        if match:
            result[match.group(1)] = match.group(2).strip().strip('"')
    return result


def scan(course_dir: Path) -> dict[str, Any]:
    progress_data = {}
    progress_json = course_dir / ".course-progress.json"
    if progress_json.exists():
        try:
            progress_data = json.loads(progress_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            progress_data = {}
    previous = {x.get("file"): x for x in progress_data.get("sources", []) if isinstance(x, dict)}
    sources = []
    for path in sorted(course_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        rel = path.relative_to(course_dir)
        if rel.parts and rel.parts[0] in GENERATED_DIRS:
            continue
        if path.name in GENERATED_FILES or path.name.startswith("."):
            continue
        current = {
            "file": str(rel),
            "hash": "sha256:" + sha256_file(path),
            "bytes": path.stat().st_size,
        }
        old = previous.get(current["file"])
        current["state"] = "DONE" if old and old.get("hash") == current["hash"] else ("UPDATED" if old else "NEW")
        sources.append(current)
    current_files = {s["file"] for s in sources}
    removed = [{"file": f, "hash": v.get("hash"), "state": "REMOVED"}
               for f, v in previous.items() if f not in current_files]
    sources.extend(removed)

    lessons = []
    concepts = []
    for path in sorted((course_dir / "01. 课程笔记").glob("*.md")) if (course_dir / "01. 课程笔记").exists() else []:
        data = frontmatter(path.read_text(encoding="utf-8"))
        if data.get("type") == "lesson":
            lessons.append({"file": str(path.relative_to(course_dir)), **data})
    for path in sorted((course_dir / "02. 知识卡片").glob("*.md")) if (course_dir / "02. 知识卡片").exists() else []:
        data = frontmatter(path.read_text(encoding="utf-8"))
        if data.get("type") == "concept":
            concepts.append({"file": str(path.relative_to(course_dir)), **data})

    progress_path = course_dir / ".course-progress.md"
    progress = progress_path.read_text(encoding="utf-8") if progress_path.exists() else ""
    return {"course_dir": str(course_dir), "sources": sources, "lessons": lessons, "concepts": concepts,
            "progress_exists": bool(progress), "progress": progress_data,
            "states": {state: sum(1 for s in sources if s.get("state") == state)
                       for state in ("NEW", "UPDATED", "DONE", "REMOVED")}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("course_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = scan(args.course_dir.resolve())
    encoded = json.dumps(manifest, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    else:
        print(encoded)


if __name__ == "__main__":
    main()
