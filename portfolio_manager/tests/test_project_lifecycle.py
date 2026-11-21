"""Six-phase ownership, verified handoffs and durable completion receipts."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from business_portfolio.tools.build_browser import parse_project
from portfolio_manager.project_lifecycle import set_phase, read_completions, project_phase
from portfolio_manager.tests.test_runner import _record


class ProjectLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        legacy = _record(self.repo, "DEMO-101")
        self.path = legacy.parent.parent / "demo-101" / "project.md"
        self.path.parent.mkdir()
        (self.path.parent / "work").mkdir()
        self.path.write_bytes(legacy.read_bytes())
        legacy.unlink()
        meta, body = parse_project(self.path.read_text())
        meta.update(workflow_version=2, project_phase="working_phase_1")
        self.write(meta, body)
        self.selection = self.path.relative_to(self.repo).as_posix()

    def write(self, meta, body):
        self.path.write_text("---\n" + json.dumps(meta, indent=2) + "\n---\n" + body)

    def advance_to(self, number):
        current = int(project_phase(parse_project(self.path.read_text())[0]).rsplit('_', 1)[1])
        for n in range(current + 1, number + 1):
            args = {} if n <= 4 else {"actor": "codex", "evidence": "Fictional phase acceptance checks passed."}
            set_phase(self.repo, self.selection, "working_phase_" + str(n), **args)

    def complete(self):
        self.advance_to(6)
        return set_phase(self.repo, self.selection, "complete", actor="codex",
                         evidence="Fictional placements independently checked.",
                         description="A verified fictional release.",
                         sale_urls=["https://example.org/store"], marketing_urls=["https://example.org/promo"])

    def test_new_drafts_start_at_phase_1_and_legacy_is_readable(self):
        self.assertEqual(project_phase({"workflow_version": 2}), "working_phase_1")
        self.assertEqual(project_phase({}), "working_phase_2")

    def test_research_advances_manually_and_cannot_skip(self):
        with self.assertRaisesRegex(ValueError, "Invalid phase transition"):
            set_phase(self.repo, self.selection, "working_phase_3")
        with self.assertRaisesRegex(ValueError, "manually"):
            set_phase(self.repo, self.selection, "working_phase_2", actor="codex", evidence="Claim")
        self.advance_to(4)
        meta, _ = parse_project(self.path.read_text())
        self.assertEqual([h["actor"] for h in meta["phase_history"]], ["user"] * 3)
        self.assertEqual(meta["commercial_validation"], "unvalidated")

    def test_empty_project_cannot_advance(self):
        meta, body = parse_project(self.path.read_text())
        meta.update(title="Empty project", record_type="empty_project", draft=True)
        self.write(meta, body)
        original = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, "Paste a researched"):
            set_phase(self.repo, self.selection, "working_phase_2")
        self.assertEqual(self.path.read_bytes(), original)

    def test_execution_codex_requires_evidence_and_cannot_skip(self):
        self.advance_to(4)
        original = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, "completion evidence"):
            set_phase(self.repo, self.selection, "working_phase_5", actor="codex")
        with self.assertRaisesRegex(ValueError, "Invalid phase transition"):
            set_phase(self.repo, self.selection, "working_phase_6", actor="codex", evidence="Claim")
        self.assertEqual(self.path.read_bytes(), original)
        self.advance_to(6)
        self.assertEqual(project_phase(parse_project(self.path.read_text())[0]), "working_phase_6")

    def test_manual_execution_handoff_is_unverified_and_does_not_complete(self):
        self.advance_to(4)
        set_phase(self.repo, self.selection, "working_phase_5", actor="user")
        meta, body = parse_project(self.path.read_text())
        self.assertEqual(meta['phase_history'][-1]['actor'], "user")
        self.assertIn("MANUAL OVERRIDE", meta['phase_history'][-1]['evidence'])
        self.assertIn("NOT VERIFIED", meta['phase_history'][-1]['evidence'])
        self.assertEqual(meta['commercial_validation'], "unvalidated")
        set_phase(self.repo, self.selection, "working_phase_6", actor="user")
        meta, after = parse_project(self.path.read_text())
        self.assertEqual(meta['project_phase'], "working_phase_6")
        self.assertEqual(len([r for r in meta['phase_history'] if 'MANUAL OVERRIDE' in r['evidence']]), 2)
        self.assertEqual(body, after)
        self.assertFalse(read_completions(self.repo))
        with self.assertRaisesRegex(ValueError, "Only Codex can verify Phase 6 completion"):
            set_phase(self.repo, self.selection, "complete", actor="user",
                      description="Unverified", sale_urls=["https://example.org/store"],
                      marketing_urls=["https://example.org/post"])
        self.assertFalse(read_completions(self.repo))

    def test_codex_renames_title_without_moving_artifacts_or_changing_id(self):
        self.advance_to(4)
        artifact = self.path.parent / "work" / "finished.txt"
        artifact.write_bytes(b"Finished fictional work")
        set_phase(self.repo, self.selection, "working_phase_5", actor="codex", evidence="Acceptance passed.",
                  title="Fictional Useful Product")
        meta, _ = parse_project(self.path.read_text())
        self.assertEqual(meta["title"], "Fictional Useful Product")
        self.assertEqual(meta["id"], "DEMO-101")
        self.assertEqual(artifact.read_bytes(), b"Finished fictional work")

    def test_phase_4_cannot_handoff_an_empty_product_name(self):
        self.advance_to(4)
        meta, body = parse_project(self.path.read_text())
        meta['title'] = 'Empty project'
        self.write(meta, body)
        with self.assertRaisesRegex(ValueError, 'appropriate product name'):
            set_phase(self.repo, self.selection, 'working_phase_5', actor='codex', evidence='Claims done')
        result = set_phase(self.repo, self.selection, 'working_phase_5', actor='codex',
                           evidence='Acceptance passed', title='Useful Product')
        self.assertEqual(result['project_phase'], 'working_phase_5')

    def test_completion_requires_phase_6(self):
        self.advance_to(4)
        with self.assertRaisesRegex(ValueError, "Invalid phase transition"):
            set_phase(self.repo, self.selection, "complete", actor="codex", evidence="Claim",
                      description="Released", sale_urls=["https://example.org/store"],
                      marketing_urls=["https://example.org/post"])
        self.assertEqual(read_completions(self.repo), [])

    def test_completion_survives_original_file_deletion(self):
        result = self.complete()
        self.assertEqual(result["project_phase"], "complete")
        receipt = read_completions(self.repo)[0]
        self.assertEqual(receipt["id"], "DEMO-101")
        self.assertEqual(receipt["marketing_links"], ["https://example.org/promo"])
        self.path.unlink()
        self.assertEqual(len(read_completions(self.repo)), 1)

    def test_completed_project_can_be_reopened_and_receipt_revoked(self):
        self.complete()
        set_phase(self.repo, self.selection, "working_phase_2")
        self.assertFalse(read_completions(self.repo))
        self.assertEqual(project_phase(parse_project(self.path.read_text())[0]), "working_phase_2")

    def test_reopening_refuses_receipt_for_different_record(self):
        self.complete()
        receipt_path = self.repo / "business_portfolio/completed_projects/DEMO-101.json"
        receipt = json.loads(receipt_path.read_text())
        receipt["source_project"] = "business_portfolio/niches/other/project.md"
        receipt_path.write_text(json.dumps(receipt))
        original = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, "does not match"):
            set_phase(self.repo, self.selection, "working_phase_2")
        self.assertEqual(self.path.read_bytes(), original)

    def test_invalid_links_and_duplicate_completion_preserve_snapshot(self):
        self.advance_to(6)
        with self.assertRaisesRegex(ValueError, "HTTP"):
            set_phase(self.repo, self.selection, "complete", actor="codex", evidence="Checks",
                      description="Finished", sale_urls=["file:///etc/passwd"],
                      marketing_urls=["https://example.org/promo"])
        self.assertFalse(read_completions(self.repo))
        self.complete()
        receipt = read_completions(self.repo)[0]
        with self.assertRaisesRegex(ValueError, "already has a snapshot"):
            set_phase(self.repo, self.selection, "complete", actor="codex", evidence="Checks",
                      description="Changed", sale_urls=["https://example.org/other"],
                      marketing_urls=["https://example.org/promo"])
        self.assertEqual(read_completions(self.repo)[0], receipt)


if __name__ == "__main__":
    unittest.main()
