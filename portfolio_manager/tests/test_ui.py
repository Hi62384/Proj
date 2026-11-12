"""Owner-facing Qt acceptance tests using a disposable portfolio."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QPlainTextEdit, QPushButton
    from portfolio_manager.ui import ITEM_DATA, ManagerPanel, _scope_path
except ModuleNotFoundError as error:
    if error.name != "PySide6":
        raise
    QApplication = None


class CoordinatorFixture:
    def __init__(self, repo):
        self.repo = repo
        self.db_path = repo / "private-state" / "coordinator.sqlite3"
        self.mode = "afk"
        self.calls = []
        self.stopped = False
        self.emergency = False
        self.record = {
            "project_id": "DEMO-001",
            "title": "Fictional field mapping",
            "niche_path": "automation/agency/deep",
            "path": "niches/automation/agency/deep/projects/demo.md",
            "work_state": "planned",
            "status": "queued",
            "progress_pct": 25,
            "commercial_validation": "unvalidated",
            "next_action": "Compare the example fields",
            "actual_revenue": None,
            "verified_paid_pilots": 0,
            "body": "**Buyer:** Fictional agency\n**Problem/outcome:** Compare sample form fields.\n"
                    "- [x] Read the sample\n- [ ] Check the mapping\n<script>plain text</script>",
            "public_results": [
                {"label": "Verified proof", "path": "results/DEMO-001/proof.md"},
                {"label": "Future work", "path": "results/DEMO-001/future.md"},
                {"label": "Untrusted program", "path": "results/DEMO-001/unsafe.cmd"},
            ],
        }

    def snapshot(self, folder=None):
        return {
            "mode": self.mode,
            "stopped": self.stopped,
            "emergency": self.emergency,
            "counts": {"eligible": 1, "active": 0, "completed": 0, "blocked": 0, "remaining": 1},
            "projects": [self.record],
            "niches": [{"path": "automation/agency/deep", "title": "Deep agency work"}],
            "workers": [{"id": "worker-1", "label": "Worker one", "folder": "business_portfolio/niches",
                         "state": "running", "kind": "background", "status": "idle"}],
            "requests": [{"id": "request-1", "kind": "login", "project_id": "DEMO-001",
                          "worker_id": "worker-1", "action": "Sign in manually",
                          "reason": "Check access", "scope": "Fictional read-only account", "cost_cad": 0,
                          "consequences": "Manual account access", "after": "Verify access"}],
        }

    def register(self, folder, *, kind):
        self.calls.append(("register", folder, kind))
        return {"id": "new-worker"}

    def set_mode(self, value):
        self.mode = value

    def resolve_request(self, identifier, decision):
        self.calls.append(("resolve", identifier, decision))

    def resume(self, *, clear_emergency):
        self.calls.append(("resume", clear_emergency))
        self.stopped = False
        self.emergency = False

    def reconcile_task(self, project_id, task_id, *, note):
        self.calls.append(("reconcile", project_id, task_id, note))


class SupervisorFixture:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.calls = []

    def start(self, identifier):
        self.calls.append(("start", identifier))

    def pause(self, identifier):
        self.calls.append(("pause", identifier))

    def stop(self, identifier):
        self.calls.append(("stop", identifier))

    def stop_all(self):
        self.calls.append(("stop_all",))
        self.coordinator.stopped = True


@unittest.skipIf(QApplication is None, "PySide6 unavailable in this Python environment")
class ManagerPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name).resolve()
        self.folder = self.repo / "business_portfolio/niches/automation/agency/deep"
        (self.folder / "projects").mkdir(parents=True)
        (self.folder / "projects/demo.md").write_text("Safe saved record", encoding="utf-8")
        results = self.repo / "business_portfolio/results/DEMO-001"
        results.mkdir(parents=True)
        (results / "proof.md").write_text("Verified fictional proof", encoding="utf-8")
        (results / "unsafe.cmd").write_text("@echo off", encoding="utf-8")
        self.coordinator = CoordinatorFixture(self.repo)
        self.supervisor = SupervisorFixture(self.coordinator)
        self.bridge_calls = []
        self.panel = ManagerPanel(
            self.coordinator, self.supervisor, self.emergency,
            on_stop_all=lambda: self.bridge_calls.append("stop"),
        )
        self.addCleanup(self.panel.deleteLater)
        self.addCleanup(self.panel.shutdown)
        self.wait_for(lambda: self.panel.results.topLevelItemCount() == 4)

    def wait_for(self, predicate):
        deadline = time.monotonic() + 5
        while not predicate() and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(0.01)
        self.assertTrue(predicate())

    def emergency(self):
        self.bridge_calls.append("emergency")
        self.coordinator.emergency = True

    def test_project_overview_uses_saved_description_and_verified_milestones(self):
        text = self.panel.detail.toPlainText()
        for expected in ("Compare sample form fields", "Fictional agency", "25% of weighted milestones verified",
                         "Demand unverified", "No actual figures recorded", "Read the sample", "Check the mapping"):
            self.assertIn(expected, text)
        self.assertNotIn("plain text", text)
        self.assertIn("<script>plain text</script>", self.panel.raw_record.toPlainText())
        self.coordinator.record["progress_pct"] = None
        self.panel.refresh()
        self.wait_for(lambda: "Progress not calculated" in self.panel.detail.toPlainText())

    def test_tree_assigns_deep_folder_and_starts_official_worker(self):
        item = self.panel.project_tree.topLevelItem(0)
        for _ in range(3):
            item = item.child(0)
        self.assertEqual(item.text(0), "Deep agency work")
        self.panel.project_tree.setCurrentItem(item)
        self.wait_for(self.panel.start.isEnabled)
        self.panel.start.click()
        self.assertEqual(self.coordinator.calls[-1], ("register", "business_portfolio/niches/automation/agency/deep", "background"))
        self.assertEqual(self.supervisor.calls[-1], ("start", "new-worker"))
        self.assertEqual(_scope_path(self.repo, self.folder), item.data(0, ITEM_DATA)[1])
        with self.assertRaises(ValueError):
            _scope_path(self.repo, self.repo.parent)

    def test_afk_manual_request_and_emergency_are_distinct_owner_controls(self):
        self.assertTrue(self.panel.approve.isHidden())
        self.assertTrue(self.panel.manual_done.isHidden())
        self.assertTrue(self.panel.deny.isHidden())
        self.assertTrue(self.panel.later.isHidden())
        request = self.panel.requests.topLevelItem(0)
        self.panel.requests.setCurrentItem(request)
        self.assertFalse(self.panel.manual_done.isHidden())
        self.assertFalse(self.panel.deny.isHidden())
        self.assertFalse(self.panel.later.isHidden())
        self.assertTrue(self.panel.approve.isHidden())
        self.assertFalse(self.panel.manual_done.isEnabled())
        self.assertIn("Fictional read-only account", self.panel.request_details.toPlainText())
        self.panel.mode.setCurrentIndex(self.panel.mode.findData("human"))
        self.panel.mode.activated.emit(self.panel.mode.currentIndex())
        self.wait_for(self.panel.manual_done.isEnabled)
        self.panel.manual_done.click()
        self.assertIn(("resolve", "request-1", "complete"), self.coordinator.calls)
        self.panel.stop_all.click()
        self.assertEqual(self.bridge_calls, ["stop"])
        self.assertEqual(self.supervisor.calls[-1], ("stop_all",))
        self.panel._emergency()
        self.wait_for(lambda: "Emergency Stop is active" in self.panel.summary.text())
        self.assertEqual(self.bridge_calls, ["stop", "emergency"])
        self.assertFalse(self.panel.manual_done.isEnabled())

    def test_results_show_missing_files_and_refuse_executable_preview(self):
        rows = {self.panel.results.topLevelItem(i).text(0): self.panel.results.topLevelItem(i)
                for i in range(self.panel.results.topLevelItemCount())}
        self.assertEqual(rows["Verified proof"].text(1), "Available")
        self.assertEqual(rows["Future work"].text(1), "Unavailable")
        self.assertEqual(rows["Untrusted program"].text(1), "Unavailable")
        self.panel.results.setCurrentItem(rows["Untrusted program"])
        self.assertFalse(self.panel.open_result.isEnabled())
        self.panel.results.setCurrentItem(rows["Verified proof"])
        self.assertTrue(self.panel.open_result.isEnabled())

    def test_worker_artifact_preview_requires_same_project_and_exact_digest(self):
        state = self.coordinator.db_path.parent
        workspace = state / "worker-runs/DEMO-001" / ("a" * 32) / "workspace"
        workspace.mkdir(parents=True)
        artifact = workspace / "draft.py"
        body = b"print('Fictional example. Preview only.')\n"
        artifact.write_bytes(body)
        self.coordinator.record["milestones"] = [
            {"id": "draft", "title": "Write draft", "status": "completed", "verified": True,
             "evidence": {"kind": "verified_artifact", "path": str(artifact),
                          "sha256": hashlib.sha256(body).hexdigest()}},
            {"id": "other", "title": "Other project's result", "status": "completed", "verified": True,
             "evidence": {"kind": "verified_artifact",
                          "path": str(state / "worker-runs/DEMO-002" / ("a" * 32) / "workspace/draft.py"),
                          "sha256": hashlib.sha256(body).hexdigest()}},
        ]
        other_project = Path(self.coordinator.record["milestones"][1]["evidence"]["path"])
        other_project.parent.mkdir(parents=True)
        other_project.write_bytes(body)
        self.panel.refresh()
        self.wait_for(lambda: self.panel.results.topLevelItemCount() == 6)
        rows = {self.panel.results.topLevelItem(i).text(0): self.panel.results.topLevelItem(i)
                for i in range(self.panel.results.topLevelItemCount())}
        self.assertEqual(rows["Worker result · Write draft"].text(1), "Available")
        self.assertEqual(rows["Worker result · Other project's result"].text(1), "Unavailable")
        observed = []
        self.panel._show_preview = lambda title, path, preview, **options: observed.append((path, preview))
        self.panel.results.setCurrentItem(rows["Worker result · Write draft"])
        self.panel.open_result.click()
        self.assertEqual(observed, [(artifact, body.decode("utf-8"))])
        artifact.write_bytes(b"changed contents")
        self.panel.open_result.click()
        self.assertEqual(len(observed), 1)
        self.assertIn("changed", self.panel.notice.text())

    def test_interrupted_task_requires_owner_note_before_queueing(self):
        self.coordinator.record["milestones"] = [{
            "id": "interrupted", "title": "Review saved mapping", "status": "reconcile",
            "checkpoint": "The test worker lost its lease.",
        }]
        self.panel.refresh()
        self.wait_for(lambda: not self.panel.review_task.isHidden())
        observed = []

        def review():
            dialog = self.app.activeModalWidget()
            if dialog is None:
                return
            accept = next(button for button in dialog.findChildren(QPushButton) if button.text() == "Return to queue")
            observed.append(accept.isEnabled())
            note = next(widget for widget in dialog.findChildren(QPlainTextEdit)
                        if widget.accessibleName() == "Your verification note")
            note.setPlainText("Reviewed the fictional saved state.")
            accept.click()

        QTimer.singleShot(0, review)
        self.panel.review_task.click()
        self.assertEqual(observed, [False])
        self.assertIn(("reconcile", "DEMO-001", "interrupted", "Reviewed the fictional saved state."), self.coordinator.calls)

    def test_multiple_blocked_tasks_review_selected_candidate(self):
        self.coordinator.record["milestones"] = [
            {"id": "interrupted", "title": "Interrupted", "status": "reconcile"},
            {"id": "candidate", "title": "Candidate", "status": "blocked",
             "evidence": {"kind": "passed_test", "sha256": "a" * 64}},
        ]
        calls = []

        class CandidateHost:
            def review_candidate(self, project, task):
                calls.append(("review", project, task))
                return {"sha256": "a" * 64, "files": [{"diff": "example change"}]}

            def apply_candidate(self, project, task, digest):
                calls.append(("apply", project, task, digest))

        self.panel.candidate_host = CandidateHost()
        self.panel.refresh()
        self.wait_for(lambda: not self.panel.review_task.isHidden())

        def approve():
            dialog = self.app.activeModalWidget()
            changes = dialog.findChild(QPlainTextEdit)
            self.assertEqual(changes.toPlainText(), "example change")
            next(button for button in dialog.findChildren(QPushButton)
                 if button.text() == "Apply reviewed changes").click()

        with patch("portfolio_manager.ui.QInputDialog.getItem", return_value=("Candidate (candidate)", True)):
            QTimer.singleShot(0, approve)
            self.panel.review_task.click()
        self.assertEqual(calls, [("review", "DEMO-001", "candidate"),
                                 ("apply", "DEMO-001", "candidate", "a" * 64)])

    def test_verify_candidate_runs_and_reports_result(self):
        self.coordinator.record['milestones'] = [
            {'id': 'candidate', 'title': 'Candidate', 'status': 'blocked',
             'evidence': {'kind': 'passed_test', 'sha256': 'a' * 64}},
        ]

        class CandidateHost:
            def verify_candidate(self, project, task):
                return {'tests_run': 3, 'files': ['example.py']}

        self.panel.candidate_host = CandidateHost()
        self.panel.refresh()
        self.wait_for(lambda: not self.panel.verify_candidate.isHidden())
        self.panel.verify_candidate.click()
        self.wait_for(lambda: 'passed 3 tests' in self.panel.notice.text())
        self.assertIn('still needs review', self.panel.notice.text())

    def test_candidate_completion_requires_review_note(self):
        self.coordinator.record['milestones'] = [{
            'id': 'candidate', 'title': 'Candidate', 'status': 'blocked',
            'criteria': 'The example output matches the specification.',
            'evidence': {'kind': 'passed_test', 'sha256': 'a' * 64},
        }]
        calls = []

        class CandidateHost:
            def complete_candidate(self, project, task, *, note):
                calls.append((project, task, note))

        self.panel.candidate_host = CandidateHost()
        self.panel.refresh()
        self.wait_for(lambda: not self.panel.complete_candidate.isHidden())
        observed = []

        def review():
            dialog = self.app.activeModalWidget()
            accept = next(button for button in dialog.findChildren(QPushButton)
                          if button.text() == 'Confirm completion')
            observed.append(accept.isEnabled())
            criteria = next(widget for widget in dialog.findChildren(QPlainTextEdit)
                            if widget.accessibleName() == 'Task acceptance criteria')
            self.assertIn('matches the specification', criteria.toPlainText())
            note = next(widget for widget in dialog.findChildren(QPlainTextEdit)
                        if widget.accessibleName() == 'Completion review note')
            note.setPlainText('Checked the example against the specification.')
            accept.click()

        QTimer.singleShot(0, review)
        self.panel.complete_candidate.click()
        self.assertEqual(observed, [False])
        self.assertEqual(calls, [('DEMO-001', 'candidate', 'Checked the example against the specification.')])


if __name__ == "__main__":
    unittest.main()
