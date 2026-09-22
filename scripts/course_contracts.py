#!/usr/bin/env python3
"""课程版运行时契约、路径安全与稳定 ID 工具。"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "course-cn-v3"
TASK_REQUIRED = {"task_id", "agent", "course_id", "source_files", "allowed_writes", "must_return", "schema_version"}
RESULT_REQUIRED = {"task_id", "status", "output_files", "coverage", "warnings", "schema_version"}
STATUSES = {"success", "needs_review", "blocked", "failed"}
RELATION_TYPES = {"prerequisite", "component", "contrast", "extension", "application", "sequence"}


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).strip().casefold()
    value = re.sub(r"[\s_\-–—]+", "", value)
    return value


def concept_id(canonical_name: str, context: str = "") -> str:
    base = normalize_name(canonical_name)
    slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", base).strip("-")[:48] or "concept"
    return slug or normalize_name(context) or "concept"


def resolve_knowledge_root(course_dir: str | Path) -> Path | None:
    """定位跨课程知识区（知识卡片的家）。

    优先级：
      1. 课程目录下的 `.vaultforge.json` 里的 `knowledge_root`（相对课程目录或绝对路径）；
      2. 从课程目录**向上**找到含 `.obsidian` 的 vault 根，其下的 `50 Knowledge/`；
      3. 回退到旧结构：课程目录内的 `02. 知识卡片/`（向后兼容）。
    找不到时返回 None（此时卡片任务必须显式给出 allowed_writes）。
    """
    root = Path(course_dir).resolve()

    config = root / ".vaultforge.json"
    if config.exists():
        try:
            data = json.loads(config.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        raw = data.get("knowledge_root") if isinstance(data, dict) else None
        if isinstance(raw, str) and raw.strip():
            candidate = Path(raw).expanduser()
            candidate = candidate if candidate.is_absolute() else (root / candidate)
            return candidate.resolve()

    for parent in root.parents:
        candidate = parent / "50 Knowledge"
        if candidate.is_dir() and (parent / ".obsidian").is_dir():
            return candidate.resolve()

    legacy = root / "02. 知识卡片"
    if legacy.is_dir():
        return legacy.resolve()
    return None


def resolve_course_code(course_dir: str | Path) -> str:
    """课程代码：优先取 `.vaultforge.json` 的 `course_code`，否则用目录名。"""
    root = Path(course_dir).resolve()
    config = root / ".vaultforge.json"
    if config.exists():
        try:
            data = json.loads(config.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        code = data.get("course_code") if isinstance(data, dict) else None
        if isinstance(code, str) and code.strip():
            return code.strip()
    return root.name


def validate_write_path(raw: str, course_dir: str | Path, extra_roots: tuple[str | Path, ...] = ()) -> str | None:
    """校验写入路径是否落在允许范围内。

    `extra_roots` 用于容纳课程目录之外的产物（例如跨课程知识区）。路径可以是
    相对课程目录的相对路径，也可以是绝对路径。
    """
    root = Path(course_dir).resolve()
    target = Path(raw).expanduser()
    target = target.resolve() if target.is_absolute() else (root / raw).resolve()
    roots = [root, *(Path(r).expanduser().resolve() for r in extra_roots if r)]
    if not any(target == r or r in target.parents for r in roots):
        return f"write_outside_course:{raw}"
    if target.name.startswith("."):
        return f"hidden_write:{raw}"
    return None


def validate_task(task: dict[str, Any], course_dir: str | Path,
                  extra_roots: tuple[str | Path, ...] = ()) -> list[str]:
    errors = sorted(TASK_REQUIRED - set(task))
    if task.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version")
    if not isinstance(task.get("source_files"), list) or not isinstance(task.get("allowed_writes"), list):
        errors.append("source_files/allowed_writes must be lists")
    for raw in task.get("allowed_writes", []):
        error = validate_write_path(raw, course_dir, extra_roots)
        if error:
            errors.append(error)
    return errors


def validate_result(result: dict[str, Any]) -> list[str]:
    errors = sorted(RESULT_REQUIRED - set(result))
    if result.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version")
    if result.get("status") not in STATUSES:
        errors.append("invalid_status")
    if not isinstance(result.get("output_files"), list):
        errors.append("output_files must be a list")
    if not isinstance(result.get("coverage"), list):
        errors.append("coverage must be a list")
    return errors


def validate_coverage(coverage: list[dict[str, Any]], source_files: set[str]) -> list[str]:
    errors = []
    allowed = {"covered", "no_knowledge", "needs_review"}
    for index, item in enumerate(coverage):
        if not isinstance(item, dict):
            errors.append(f"coverage[{index}] must be object"); continue
        if item.get("source") not in source_files:
            errors.append(f"coverage[{index}].source_missing")
        if not isinstance(item.get("page"), int) or item["page"] < 1:
            errors.append(f"coverage[{index}].page_invalid")
        if item.get("status") not in allowed:
            errors.append(f"coverage[{index}].status_invalid")
        if item.get("status") != "no_knowledge" and not item.get("knowledge_points"):
            errors.append(f"coverage[{index}].knowledge_points_missing")
    return errors


def atomic_json_write(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    json.loads(tmp.read_text(encoding="utf-8"))
    tmp.replace(path)
