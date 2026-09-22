import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("contracts", ROOT / "scripts/course_contracts.py")
contracts = importlib.util.module_from_spec(spec); spec.loader.exec_module(contracts)
spec2 = importlib.util.spec_from_file_location("manifest", ROOT / "scripts/course-manifest.py")
manifest = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(manifest)


class RuntimeContractTest(unittest.TestCase):
    def test_stable_concept_id_and_normalization(self):
        self.assertEqual(contracts.concept_id(" CNN "), contracts.concept_id("cnn"))

    def test_rejects_write_outside_course(self):
        task = {"task_id": "x", "course_id": "c", "source_files": [],
                "allowed_writes": ["../escape.md"], "must_return": [],
                "schema_version": contracts.SCHEMA_VERSION}
        self.assertTrue(contracts.validate_task(task, "/tmp/course"))

    def test_result_schema(self):
        result = {"task_id": "x", "status": "success", "output_files": [],
                  "coverage": [], "warnings": [], "schema_version": contracts.SCHEMA_VERSION}
        self.assertEqual(contracts.validate_result(result), [])

    def test_coverage_contract(self):
        good = [{"source": "lecture.pptx", "page": 3, "knowledge_points": ["卷积"], "status": "covered"}]
        self.assertEqual(contracts.validate_coverage(good, {"lecture.pptx"}), [])
        bad = [{"source": "missing.pptx", "page": 0, "knowledge_points": [], "status": "covered"}]
        self.assertGreater(len(contracts.validate_coverage(bad, {"lecture.pptx"})), 1)


class ManifestStateTest(unittest.TestCase):
    def test_new_done_updated_removed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root / "a.md").write_text("a", encoding="utf8")
            old_hash = manifest.sha256_file(root / "a.md")
            (root / ".course-progress.json").write_text(json.dumps({"sources": [{"file": "a.md", "hash": "sha256:" + old_hash}]}), encoding="utf8")
            out = manifest.scan(root)
            self.assertEqual(out["sources"][0]["state"], "DONE")
            (root / "a.md").write_text("b", encoding="utf8")
            self.assertEqual(manifest.scan(root)["sources"][0]["state"], "UPDATED")


if __name__ == "__main__":
    unittest.main()
