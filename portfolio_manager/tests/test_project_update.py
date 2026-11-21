"""Verify append-only imports, source lineage, backups and phase transitions."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from portfolio_manager.project_update import replace_project_from_file, snapshot_sha256
from portfolio_manager.tests.test_runner import _record
from business_portfolio.tools.build_browser import parse_project


class Phase3UpdateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "repo"
        legacy = _record(self.repo, "DEMO-301")
        folder = legacy.parent / "demo-301"
        folder.mkdir()
        self.path = folder / "project.md"
        self.path.write_bytes(legacy.read_bytes())
        legacy.unlink()
        (folder / "work").mkdir()
        self.selection = self.path.relative_to(self.repo).as_posix()
        from portfolio_manager.project_lifecycle import set_phase
        set_phase(self.repo, self.selection, "working_phase_3")

    def update_file(self, heading, status, *, change=None, base=None):
        original = self.path.read_text(encoding="utf-8")
        meta, _ = parse_project(original, self.selection)
        meta["phase3_update_base_sha256"] = base or snapshot_sha256(original)
        meta.update(status)
        if change:
            meta.update(change)
        _, _, body = original.partition("\n---\n")
        contents = "---\n" + json.dumps(meta) + "\n---\n" + body + "\n\n" + heading
        source = Path(self.tmp.name) / "phase3-update.md"
        source.write_text(contents, encoding="utf-8")
        return source

    def test_3a_then_3b_approval_moves_to_phase4_preserving_body_and_work(self):
        original = self.path.read_text()
        (self.path.parent / "work" / "asset.txt").write_text("asset")
        first = self.update_file("## Phase 3a — Distribution and marketing research\nhttps://example.org/store\n",
                                 {"phase3_plan_status": "researched"})
        stage = replace_project_from_file(self.repo, self.selection, first)
        self.assertEqual(stage["project_phase"], "working_phase_3")
        self.assertEqual(stage["import_stage"], "3a")
        self.assertIn(original.partition("\n---\n")[2], self.path.read_text())
        self.assertTrue(Path(stage["backup"]).is_file())
        self.assertEqual((self.path.parent / "work" / "asset.txt").read_text(), "asset")
        second = self.update_file("## Phase 3b — Independent validation and final launch plan\n"
                                  "VERDICT: APPROVED\nhttps://example.org/rules\n",
                                  {"phase3_validation_status": "approved"})
        stage = replace_project_from_file(self.repo, self.selection, second)
        self.assertEqual(stage["project_phase"], "working_phase_4")
        self.assertEqual(stage["import_stage"], "3b")
        self.assertIn("## Phase 3a", self.path.read_text())
        self.assertIn("## Phase 3b", self.path.read_text())
        self.assertEqual((self.path.parent / "work" / "asset.txt").read_text(), "asset")

    def test_unapproved_3b_does_not_advance(self):
        replace_project_from_file(self.repo, self.selection,
            self.update_file("## Phase 3a — Sources\nhttps://example.org\n",
                             {"phase3_plan_status": "researched"}))
        outcome = replace_project_from_file(self.repo, self.selection,
            self.update_file("## Phase 3b — Review\nVERDICT: NEEDS_REVISION\nhttps://example.org/new\n",
                             {"phase3_validation_status": "needs_revision"}))
        self.assertEqual(outcome["project_phase"], "working_phase_3")

    def test_reject_stale_rewrite_or_protected_metadata(self):
        before = self.path.read_bytes()
        source = self.update_file("## Phase 3a — Research\nhttps://example.org\n",
                                  {"phase3_plan_status": "researched"},
                                  base="0" * 64)
        with self.assertRaisesRegex(ValueError, "stale"):
            replace_project_from_file(self.repo, self.selection, source)
        source = self.update_file("## Phase 3a — Research\nhttps://example.org\n",
                                  {"phase3_plan_status": "researched"},
                                  change={"commercial_validation": "commercially_validated"})
        with self.assertRaisesRegex(ValueError, "protected"):
            replace_project_from_file(self.repo, self.selection, source)
        self.assertEqual(self.path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
