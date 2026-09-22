import py_compile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CourseSkillIntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")

    def test_chinese_course_model_present(self):
        for marker in ("课程索引", "课程笔记", "知识卡片", "课程扫描与增量判定"):
            self.assertIn(marker, self.skill)

    def test_research_and_redundant_outputs_removed(self):
        self.assertIn("争议分析文件", self.skill)
        self.assertIn("不生成额外报告文件", self.skill)
        self.assertNotIn("Phase 6", self.skill)

    def test_course_agents_exist(self):
        for name in ("lesson-organizer", "concept-card-builder", "course-index-manager", "course-reviewer"):
            path = ROOT / "agents" / f"{name}.md"
            self.assertTrue(path.exists(), path)
            text = path.read_text(encoding="utf-8")
            self.assertIn("name:", text[:200])
            self.assertIn("description:", text[:300])

    def test_no_legacy_agent_files(self):
        for name in ("roadmap-generator.md", "file-structure-creator.md", "atomic-note-filler.md", "note-reviewer.md"):
            self.assertFalse((ROOT / "agents" / name).exists(), name)

    def test_frontmatter_contract(self):
        for field in ("type: lesson | concept", "lesson_id", "concept_id", "source_hash", "vf_status"):
            self.assertIn(field, self.skill)

    def test_orchestration_contract_present(self):
        for marker in ("主 Agent 的职责", "子 Agent 的职责边界", "子 Agent 任务信封", "冲突与锁定规则"):
            self.assertIn(marker, self.skill)

    def test_agents_have_contracts(self):
        for path in (ROOT / "agents").glob("*.md"):
            text = path.read_text(encoding="utf-8")
            self.assertGreater(len(text), 700, f"{path.name} is underspecified")
            self.assertIn("输入契约", text)
            self.assertIn("返回格式", text)


class ScriptSyntaxTest(unittest.TestCase):
    def test_context_extractor_syntax(self):
        py_compile.compile(str(ROOT / "scripts" / "context-extractor.py"), doraise=True)

    def test_double_link_builder_syntax(self):
        py_compile.compile(str(ROOT / "scripts" / "double-link-builder.py"), doraise=True)

    def test_course_manifest_syntax(self):
        py_compile.compile(str(ROOT / "scripts" / "course-manifest.py"), doraise=True)


if __name__ == "__main__":
    unittest.main()
