#!/usr/bin/env python3
"""轻量课程校验器：扫描增量状态并验证任务边界，不调度 Agent。"""
from __future__ import annotations
import argparse, json, importlib.util
from pathlib import Path
from course_contracts import SCHEMA_VERSION, atomic_json_write, validate_task
_spec = importlib.util.spec_from_file_location("course_manifest", Path(__file__).with_name("course-manifest.py"))
_manifest = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_manifest)
scan = _manifest.scan

def build_tasks(course_dir: Path, manifest: dict) -> list[dict]:
    tasks = []
    for source in manifest["sources"]:
        state = source.get("state", "NEW")
        if state == "DONE":
            continue
        stem = Path(source["file"]).stem
        lesson_id = f"L{len(tasks)+1:02d}"
        tasks.append({"task_id": f"lesson-{lesson_id}", "agent": "lesson-organizer",
            "course_id": course_dir.name, "lesson_id": lesson_id, "source_files": [source],
            "allowed_writes": [f"01. 课程笔记/{lesson_id} - {stem}.md"],
            "must_return": ["output_files", "coverage", "concept_candidates", "warnings"],
            "schema_version": SCHEMA_VERSION, "state": state})
    return tasks

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("course_dir", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args(); root = args.course_dir.resolve()
    manifest = scan(root)
    tasks = build_tasks(root, manifest)
    errors = [{"task_id": t["task_id"], "errors": validate_task(t, root)} for t in tasks]
    errors = [x for x in errors if x["errors"]]
    state = {"schema_version": SCHEMA_VERSION, "course_dir": str(root),
             "tasks": tasks, "invalid_tasks": errors,
             "instruction": "主 Agent 根据 tasks 分发任务；本工具不执行、重试或并发调度 Agent。"}
    out = args.output or (root / ".course-runtime.json")
    atomic_json_write(out, state)
    print(json.dumps(state, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
