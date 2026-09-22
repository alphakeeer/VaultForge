#!/usr/bin/env python3
"""课程版运行时契约、路径安全与稳定 ID 工具。"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "course-cn-v2"
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


def validate_write_path(raw: str, course_dir: str | Path) -> str | None:
    root = Path(course_dir).resolve()
    target = (root / raw).resolve()
    if root not in target.parents and target != root:
        return f"write_outside_course:{raw}"
    if target.name.startswith("."):
        return f"hidden_write:{raw}"
    return None


def validate_task(task: dict[str, Any], course_dir: str | Path) -> list[str]:
    errors = sorted(TASK_REQUIRED - set(task))
    if task.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version")
    if not isinstance(task.get("source_files"), list) or not isinstance(task.get("allowed_writes"), list):
        errors.append("source_files/allowed_writes must be lists")
    for raw in task.get("allowed_writes", []):
        error = validate_write_path(raw, course_dir)
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
