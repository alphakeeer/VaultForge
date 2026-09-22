#!/usr/bin/env python3
"""轻量课程校验器：扫描增量状态并验证任务边界，不调度 Agent。"""
from __future__ import annotations
import argparse, json, importlib.util
from pathlib import Path
from course_contracts import (SCHEMA_VERSION, atomic_json_write,
                              resolve_course_code, resolve_knowledge_root, validate_task)
_spec = importlib.util.spec_from_file_location("course_manifest", Path(__file__).with_name("course-manifest.py"))
_manifest = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_manifest)
scan = _manifest.scan


def build_tasks(course_dir: Path, manifest: dict) -> list[dict]:
    """为「尚无对应课次产物」的课件生成 lesson-organizer 任务信封。

    跳过依据是 `processed`（是否已存在由该课件产出的课次笔记），而**不是**
    `state == "DONE"`。`state` 只表示「hash 与上次登记一致」，把课件写进
    `.course-progress.json` 之后，未处理的课件也会显示 DONE，据此跳过会漏处理。
    """
    tasks = []
    for source in manifest["sources"]:
        if source.get("processed"):
            continue
        stem = Path(source["file"]).stem
        lesson_id = f"L{len(tasks)+1:02d}"
        tasks.append({"task_id": f"lesson-{lesson_id}", "agent": "lesson-organizer",
            "course_id": manifest.get("course_code") or course_dir.name,
            "lesson_id": lesson_id, "source_files": [source],
            "allowed_writes": [f"01. 课程笔记/{lesson_id} - {stem}.md"],
            "must_return": ["output_files", "coverage", "concept_candidates", "warnings"],
            "schema_version": SCHEMA_VERSION, "state": source.get("state", "NEW")})
    return tasks


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("course_dir", type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--knowledge-root", type=Path, default=None,
                   help="跨课程知识区根目录；缺省时自动探测 .vaultforge.json 或 vault 根的 50 Knowledge")
    args = p.parse_args(); root = args.course_dir.resolve()
    knowledge_root = args.knowledge_root or resolve_knowledge_root(root)
    manifest = scan(root, knowledge_root)
    tasks = build_tasks(root, manifest)
    extra = (knowledge_root,) if knowledge_root else ()
    errors = [{"task_id": t["task_id"], "errors": validate_task(t, root, extra)} for t in tasks]
    errors = [x for x in errors if x["errors"]]
    state = {"schema_version": SCHEMA_VERSION, "course_dir": str(root),
             "course_code": resolve_course_code(root),
             "knowledge_root": str(knowledge_root) if knowledge_root else None,
             "tasks": tasks, "invalid_tasks": errors,
             "instruction": "主 Agent 根据 tasks 分发任务；本工具不执行、重试或并发调度 Agent。"}
    out = args.output or (root / ".course-runtime.json")
    atomic_json_write(out, state)
    print(json.dumps(state, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
