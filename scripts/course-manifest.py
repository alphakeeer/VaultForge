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
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from course_contracts import resolve_course_code, resolve_knowledge_root  # noqa: E402


SOURCE_EXTENSIONS = {".pdf", ".ppt", ".pptx", ".md", ".txt", ".doc", ".docx", ".html", ".htm"}
# 课程目录内由本 skill 生成的产物目录（不会被当成课件）
GENERATED_DIRS = {"01. 课程笔记", "02. 知识卡片"}
GENERATED_FILES = {"00. 课程索引.md"}
# 知识区自身的索引页
KNOWLEDGE_INDEX_FILES = {"_index.md"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def frontmatter(text: str) -> dict[str, Any]:
    """解析 YAML frontmatter 的单行标量、单行数组与多行数组。

    只覆盖本 skill 用到的有限子集：`key: value`、`key: [a, b]`、`key:` 后跟 `- item` 列表。
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    result: dict[str, Any] = {}
    lines = text[3:end].splitlines()
    index = 0
    while index < len(lines):
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", lines[index])
        if not match:
            index += 1
            continue
        key, raw = match.group(1), match.group(2).strip()
        if raw.startswith("[") and raw.endswith("]"):
            result[key] = [x.strip().strip("\"'") for x in raw[1:-1].split(",") if x.strip()]
        elif raw:
            result[key] = raw.strip("\"'")
        else:
            items, cursor = [], index + 1
            while cursor < len(lines):
                item = re.match(r"^\s+-\s+(.*)$", lines[cursor])
                if not item:
                    break
                items.append(item.group(1).strip().strip("\"'"))
                cursor += 1
            if items:
                result[key] = items
                index = cursor - 1
        index += 1
    return result


def scan(course_dir: Path, knowledge_root: Path | None = None) -> dict[str, Any]:
    course_dir = Path(course_dir).resolve()
    course_code = resolve_course_code(course_dir)
    if knowledge_root is None:
        knowledge_root = resolve_knowledge_root(course_dir)
    knowledge_root = Path(knowledge_root).resolve() if knowledge_root else None

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

    lessons_dir = course_dir / "01. 课程笔记"
    for path in sorted(lessons_dir.glob("*.md")) if lessons_dir.exists() else []:
        data = frontmatter(path.read_text(encoding="utf-8"))
        if data.get("type") == "lesson":
            lessons.append({"file": str(path.relative_to(course_dir)), **data})

    # 旧结构：卡片曾放在课程目录内的 `02. 知识卡片/`
    legacy_dir = course_dir / "02. 知识卡片"
    for path in sorted(legacy_dir.glob("*.md")) if legacy_dir.exists() else []:
        data = frontmatter(path.read_text(encoding="utf-8"))
        if data.get("type") == "concept":
            concepts.append({"file": str(path.relative_to(course_dir)), **data})

    # 新结构：卡片位于 vault 级知识区，按 `courses`（或 `course_id`）字段归属筛选
    if knowledge_root and knowledge_root.is_dir():
        inside_course = course_dir == knowledge_root or course_dir in knowledge_root.parents
        if not inside_course:
            for path in sorted(knowledge_root.rglob("*.md")):
                if path.name in KNOWLEDGE_INDEX_FILES or path.name.startswith("."):
                    continue
                data = frontmatter(path.read_text(encoding="utf-8"))
                if data.get("type") != "concept":
                    continue
                owned = data.get("courses") or data.get("course_id") or []
                owned = owned if isinstance(owned, list) else [owned]
                if course_code in owned or course_dir.name in owned:
                    concepts.append({"file": str(path), **data})

    # 区分两种语义：`state` 只表示「hash 是否变化」，`processed` 表示「是否已有对应课次产物」。
    # 只依赖 state == "DONE" 会漏掉「已登记 hash 但尚未处理」的课件。
    processed_sources = {x.get("source_file") for x in lessons if x.get("source_file")}
    for source in sources:
        source["processed"] = source["file"] in processed_sources

    progress_path = course_dir / ".course-progress.md"
    progress = progress_path.read_text(encoding="utf-8") if progress_path.exists() else ""
    return {"course_dir": str(course_dir), "course_code": course_code,
            "knowledge_root": str(knowledge_root) if knowledge_root else None,
            "sources": sources, "lessons": lessons, "concepts": concepts,
            "progress_exists": bool(progress), "progress": progress_data,
            "states": {state: sum(1 for s in sources if s.get("state") == state)
                       for state in ("NEW", "UPDATED", "DONE", "REMOVED")}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("course_dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--knowledge-root", type=Path, default=None,
                        help="跨课程知识区根目录；缺省时自动探测 .vaultforge.json 或 vault 根的 50 Knowledge")
    args = parser.parse_args()
    manifest = scan(args.course_dir.resolve(), args.knowledge_root)
    encoded = json.dumps(manifest, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    else:
        print(encoded)


if __name__ == "__main__":
    main()
