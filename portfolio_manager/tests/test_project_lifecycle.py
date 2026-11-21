"""Offline phase transitions and durable completion receipts."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from portfolio_manager.project_lifecycle import set_phase, read_completions, project_phase
from portfolio_manager.tests.test_runner import _record


class ProjectLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.legacy = _record(self.repo, "DEMO-101")
        self.selection = self.legacy.relative_to(self.repo).as_posix()

    def test_phase_2_is_default_for_existing_records(self):
        raw = self.legacy.read_text()
        self.assertNotIn('"project_phase"', raw)
        self.assertEqual(project_phase(json.loads(raw.split("---", 2)[1])), "working_phase_2")

    def test_transition_requires_phase_3_before_completion(self):
        original = self.legacy.read_bytes()
        with self.assertRaisesRegex(ValueError, "Invalid phase transition"):
            set_phase(self.repo, self.selection, "complete", description="Released",
                      sale_urls=["https://example.org/store"], marketing_urls=["https://example.org/post"])
        self.assertEqual(self.legacy.read_bytes(), original)
        self.assertEqual(read_completions(self.repo), [])

    def test_phase_can_move_back_and_forward(self):
        set_phase(self.repo, self.selection, "working_phase_3")
        self.assertEqual(set_phase(self.repo, self.selection, "working_phase_2")["project_phase"],
                         "working_phase_2")
        self.assertEqual(set_phase(self.repo, self.selection, "working_phase_3")["project_phase"],
                         "working_phase_3")
        self.assertFalse(read_completions(self.repo))
        self.assertEqual(set_phase(self.repo, self.selection, "working_phase_4")["project_phase"],
                         "working_phase_4")
        self.assertEqual(set_phase(self.repo, self.selection, "working_phase_3")["project_phase"],
                         "working_phase_3")

    def test_completed_project_can_be_demoted_and_receipt_revoked(self):
        set_phase(self.repo, self.selection, "working_phase_3")
        set_phase(self.repo, self.selection, "working_phase_4")
        set_phase(self.repo, self.selection, "complete", description="Verified fictional package",
                  sale_urls=["https://example.org/store"],
                  marketing_urls=["https://example.org/promo"])
        self.assertEqual(len(read_completions(self.repo)), 1)
        set_phase(self.repo, self.selection, "working_phase_3")
        self.assertFalse(read_completions(self.repo))
        set_phase(self.repo, self.selection, "working_phase_2")
        self.assertEqual(project_phase(json.loads(self.legacy.read_text().split("---", 2)[1])),
                         "working_phase_2")

    def test_completed_project_can_return_directly_to_phase_2(self):
        set_phase(self.repo, self.selection, "working_phase_3")
        set_phase(self.repo, self.selection, "working_phase_4")
        set_phase(self.repo, self.selection, "complete", description="Verified fictional release",
                  sale_urls=["https://example.org/store"],
                  marketing_urls=["https://example.org/promo"])
        self.assertEqual(len(read_completions(self.repo)), 1)
        result = set_phase(self.repo, self.selection, "working_phase_2")
        self.assertEqual(result["project_phase"], "working_phase_2")
        self.assertFalse(read_completions(self.repo))
        self.assertEqual(project_phase(json.loads(self.legacy.read_text().split("---", 2)[1])),
                         "working_phase_2")

    def test_completion_survives_original_file_deletion(self):
        set_phase(self.repo, self.selection, "working_phase_3")
        set_phase(self.repo, self.selection, "working_phase_4")
        result = set_phase(self.repo, self.selection, "complete", description="A verified fictional release.",
                           sale_urls=["https://example.org/store"], marketing_urls=["https://example.org/promo"],
                           other_urls=["https://example.org/help"])
        self.assertEqual(result["project_phase"], "complete")
        receipt = read_completions(self.repo)[0]
        self.assertEqual(receipt["id"], "DEMO-101")
        self.assertEqual(receipt["marketing_links"], ["https://example.org/promo"])
        self.legacy.unlink()
        self.assertEqual(len(read_completions(self.repo)), 1)

    def test_invalid_links_and_duplicate_completion_preserve_snapshot(self):
        set_phase(self.repo, self.selection, "working_phase_3")
        set_phase(self.repo, self.selection, "working_phase_4")
        with self.assertRaisesRegex(ValueError, "HTTP"):
            set_phase(self.repo, self.selection, "complete", description="Finished",
                      sale_urls=["file:///etc/passwd"], marketing_urls=["https://example.org/promo"])
        self.assertFalse(read_completions(self.repo))
        set_phase(self.repo, self.selection, "complete", description="Finished",
                  sale_urls=["https://example.org/store"], marketing_urls=["https://example.org/promo"])
        receipt = read_completions(self.repo)[0]
        with self.assertRaisesRegex(ValueError, "already has a snapshot"):
            set_phase(self.repo, self.selection, "complete", description="Changed",
                      sale_urls=["https://example.org/other"], marketing_urls=["https://example.org/promo"])
        self.assertEqual(read_completions(self.repo)[0], receipt)


if __name__ == "__main__":
    unittest.main()
