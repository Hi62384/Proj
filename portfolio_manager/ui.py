"""Owner dashboard embedded in the existing Computer Bridge window."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import hashlib
from html import escape
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
from urllib.parse import urlsplit

from PySide6.QtCore import QTimer, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFileDialog, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QSplitter,
    QTabWidget, QTextBrowser, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)

from business_portfolio.tools import build_browser
from business_portfolio.tools.serve_browser import PUBLIC_LINKS, public_results, result_file, safe_file
from .runner import DRAFTS, MAX_FILE_BYTES


NICHE_ROOT = PurePosixPath("business_portfolio/niches")
ITEM_DATA = Qt.ItemDataRole.UserRole
STATE_LABELS = {
    "active": "In progress", "archived": "Archived", "blocked": "Blocked",
    "cancelled": "Cancelled", "checkpointed": "Work saved", "completed": "Completed", "deferred": "Deferred",
    "idle": "Idle", "legacy_preserved": "Preserved", "needs_reconciliation": "Needs review",
    "operational_reported": "In use", "package_ready": "Ready to integrate", "paused": "Paused",
    "planned": "Not started", "prototype_reported": "Prototype", "published_reported": "Published",
    "queued": "Queued", "ready_for_test": "Ready to test", "ready_to_launch": "Ready to launch",
    "stopped": "Stopped", "testing": "Testing", "waiting": "Waiting for human",
    "waiting_for_human": "Waiting for human", "working": "Working",
}
COMMERCIAL_LABELS = {
    "unvalidated": "Demand unverified",
    "published_unvalidated": "Published, demand unverified",
    "buyer_signal": "Buyer interest recorded",
    "paid_pilot": "Paid pilot recorded",
    "repeat_paid": "Repeat sales recorded",
    "commercially_validated": "Commercial validation recorded",
    "not_applicable": "Not a commercial project",
}
KNOWN_DESCRIPTIONS = {
    "EX-001": "A spreadsheet for cleaning businesses to estimate job prices from their own labor, travel and supply costs.",
    "EX-002": "A spreadsheet that shows when a single inventory item falls below its reorder threshold.",
    "EX-007": "The local connection between official Codex and authorized browser or desktop actions.",
}
STYLE = """
QWidget#portfolioManager { background: #f5f7f8; color: #1a2930; }
QLabel#managerTitle { font-family: "Segoe UI"; font-size: 24px; font-weight: 700; color: #183a32; }
QLabel#managerSummary, QLabel#folderScope, QLabel#managerNotice { color: #3f5459; }
QLabel#detailTitle { font-size: 19px; font-weight: 650; color: #183a32; }
QWidget#managerBar { background: white; border: 1px solid #dce5e3; border-radius: 8px; }
QPushButton#primaryWorkerButton { background: #20594b; border-color: #20594b; color: white; font-weight: 600; }
QPushButton#primaryWorkerButton:hover { background: #2b6a58; }
QPushButton#primaryWorkerButton:disabled { background: #dce5e3; color: #465b57; border-color: #dce5e3; }
QPushButton#emergencyButton { color: #982c23; border-color: #dca9a3; font-weight: 600; }
QPushButton#emergencyButton:hover { background: #fff0ef; }
QTreeWidget, QTextBrowser, QPlainTextEdit, QLineEdit, QComboBox {
    background: white; border: 1px solid #d7e1df; border-radius: 5px; padding: 4px;
    selection-background-color: #cce8df; selection-color: #12382e;
}
QHeaderView::section { padding: 6px; background: #edf2f1; border: 0; color: #3a5550; }
QTabBar::tab { padding: 7px 13px; margin-right: 4px; }
QTabBar::tab:selected { color: #20594b; font-weight: 600; }
QGroupBox { border: 1px solid #dce5e3; border-radius: 6px; margin-top: 11px; padding-top: 8px; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 8px; }
"""


def _label(text="", *, wrap=False):
    label = QLabel(text)
    label.setTextFormat(Qt.TextFormat.PlainText)
    label.setWordWrap(wrap)
    return label


def _button(text, slot, object_name=None):
    widget = QPushButton(text)
    if object_name:
        widget.setObjectName(object_name)
    widget.clicked.connect(slot)
    return widget


def _tree(headers):
    tree = QTreeWidget()
    tree.setHeaderLabels(headers)
    tree.setAlternatingRowColors(True)
    tree.setUniformRowHeights(True)
    tree.header().setStretchLastSection(False)
    tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    for index in range(1, len(headers)):
        tree.header().setSectionResizeMode(index, QHeaderView.ResizeMode.ResizeToContents)
    return tree


def _text(value, fallback=""):
    if value is None:
        return fallback
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)


def _status(value):
    return STATE_LABELS.get(value, str(value or "Not recorded").replace("_", " ").capitalize())


def _project_id(project):
    return project.get("project_id") or project.get("id")


def _scope_path(repo, selected):
    """Normalize an owner-picked directory without accepting links or junctions."""
    base = repo.joinpath(*NICHE_ROOT.parts)
    path = Path(selected)
    if not path.is_absolute():
        path = repo / path
    relative = path.relative_to(base)
    if ".." in relative.parts:
        raise ValueError("Choose a folder inside the portfolio project directory.")
    parents = [base.parent, base]
    parents.extend(base.joinpath(*relative.parts[:depth]) for depth in range(1, len(relative.parts) + 1))
    for part in parents:
        if build_browser.linked_input(part):
            raise ValueError("Choose a project folder directly instead of using a linked folder.")
    if not path.is_dir() or not path.resolve(strict=True).is_relative_to(base.resolve(strict=True)):
        raise ValueError("Choose a folder inside the portfolio project directory.")
    return path.relative_to(repo).as_posix()


def _description(project):
    body = project.get("body", "")
    outcome = re.search(r"(?m)^\*\*Problem/outcome:\*\*\s*([^\n]+)", body)
    buyer = re.search(r"(?m)^\*\*Buyer:\*\*\s*([^\n]+)", body)
    description = project.get("description") or (outcome.group(1) if outcome else None)
    description = description or KNOWN_DESCRIPTIONS.get(_project_id(project))
    if not description:
        bounded = re.search(r"(?m)^## Bounded deliverable\s*\n+([^\n]+)", body)
        description = bounded.group(1) if bounded else project.get("next_action")
    return _text(description, "See the saved project instructions."), buyer.group(1) if buyer else ""


def _worker_artifact(state_directory, project_id, evidence):
    """Resolve one verified text draft from this project's private run directory."""
    if not isinstance(evidence, dict) or evidence.get("kind") not in {"verified_artifact", "passed_test"}:
        return None
    digest = evidence.get("sha256")
    path = evidence.get("path")
    if (not isinstance(project_id, str) or not re.fullmatch(r"[A-Z][A-Z0-9_-]*-[0-9]{3,}", project_id)
            or not isinstance(path, str) or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)):
        return None
    base = state_directory / "worker-runs" / project_id
    target = Path(path)
    try:
        run, workspace, name = target.relative_to(base).parts
        if not re.fullmatch(r"[0-9a-f]{32}", run) or workspace != "workspace" or name not in DRAFTS:
            return None
        for part in (state_directory, base.parent, base, base / run, base / run / workspace, target):
            if build_browser.linked_input(part):
                return None
        if not target.resolve(strict=True).is_relative_to(base.resolve(strict=True)) or not target.is_file():
            return None
        with target.open("rb") as handle:
            contents = handle.read(MAX_FILE_BYTES + 1)
            observed = os.fstat(handle.fileno())
        if (len(contents) > MAX_FILE_BYTES or b"\x00" in contents
                or hashlib.sha256(contents).hexdigest() != digest
                or not os.path.samestat(observed, target.stat()) or build_browser.linked_input(target)):
            return None
        return target, contents.decode("utf-8")
    except (OSError, ValueError):
        return None


def _project_body(project, workers):
    """Create display markup with escaped values only. It never loads remote resources."""
    description, buyer = _description(project)
    percent = project.get("progress_pct")
    if type(percent) in (int, float) and math.isfinite(percent) and 0 <= percent <= 100:
        progress = f"{percent:g}% of weighted milestones verified"
    else:
        progress = "Progress not calculated. No verified milestone plan is available."
    task = project.get("current_task") or {}
    worker = workers.get(project.get("worker_id"), {})
    current = task.get("title") or task.get("objective") or task.get("action") or task.get("description")
    next_action = task.get("next_action") or project.get("next_action")
    status = project.get("status") or project.get("work_state")
    blocker = task.get("blocker") or task.get("last_error") or project.get("blocker")
    if not blocker and status in ("blocked", "needs_reconciliation", "waiting", "waiting_for_human"):
        blocker = next_action or "See the saved instructions and human requests."
    validation = project.get("commercial_validation", "unvalidated")
    commercial = COMMERCIAL_LABELS.get(validation, _status(validation))
    launch = project.get("launch_status") or (
        "Published in the saved record" if project.get("work_state") == "published_reported"
        or validation == "published_unvalidated" else "Publication not recorded"
    )
    parts = [f"<p>{escape(description)}</p>"]

    def field(name, value):
        if value is not None and value != "":
            parts.append(f"<p><b>{escape(name)}</b> · {escape(_text(value))}</p>")

    field("Who it serves", buyer)
    price = project.get("offer_price_cad_hypothesis")
    if isinstance(price, list) and len(price) == 2 and all(type(amount) in (int, float) for amount in price):
        field("Proposed price", f"CAD {price[0]:g}–{price[1]:g}")
    field("Status", _status(status))
    field("Development progress", progress)
    field("Worker", worker.get("label") or ("Assigned" if project.get("worker_id") else "Unassigned"))
    field("Current task", current)
    field("Next step", next_action)
    field("Blocker", blocker)
    field("Launch", launch)
    field("Commercial performance", commercial)
    field("Verified paid pilots", project.get("verified_paid_pilots"))
    for key, title in (("verified_customers", "Verified customers"), ("actual_revenue", "Recorded revenue"),
                       ("actual_expenses", "Recorded expenses"), ("actual_profit", "Recorded profit")):
        value = project.get(key)
        if value is not None:
            currency = project.get("actual_currency") if key.startswith("actual_") else None
            field(title, f"{currency} {value}" if currency else value)
    if all(project.get(key) is None for key in ("actual_revenue", "actual_expenses", "actual_profit")):
        field("Financial results", "No actual figures recorded")

    checks = re.findall(r"(?m)^\s*[-*] \[([ xX])\]\s+(.+)$", project.get("body", ""))
    milestones = project.get("milestones") or []
    for completed, title in ((True, "Completed work"), (False, "Remaining work")):
        items = [f"Saved checklist · {name}" for state, name in checks if (state.lower() == "x") == completed]
        for milestone in milestones:
            verified = milestone.get("verified") is True or milestone.get("status") == "verified"
            if verified == completed:
                name = milestone.get("title") or milestone.get("label") or milestone.get("name") or milestone.get("id")
                if name:
                    items.append(f"Milestone · {name}")
        parts.append(f"<h4>{title}</h4>")
        if items:
            parts.append("<ul>" + "".join(f"<li>{escape(item)}</li>" for item in items) + "</ul>")
        else:
            parts.append("<p>No items recorded.</p>")
    return "".join(parts)


class ManagerPanel(QWidget):
    """One owner-facing surface for the coordinator, with an embedded bridge sibling tab."""

    def __init__(self, coordinator, supervisor, on_emergency, parent=None, *, on_stop_all=None,
                 on_context=None, start_context_worker=None, can_start_context=None, context_worker=None,
                 header_layout=None):
        super().__init__(parent)
        self.coordinator = coordinator
        self.supervisor = supervisor
        self.on_emergency = on_emergency
        self.on_stop_all = on_stop_all
        self.on_context = on_context
        self.start_context_worker = start_context_worker
        self.can_start_context = can_start_context
        self.context_worker = context_worker
        self.header_layout = header_layout
        self.context_record = None
        self.repo = Path(coordinator.repo).resolve(strict=True)
        self.folder = NICHE_ROOT.as_posix()
        self._state = {}
        self._projects = {}
        self._workers = {}
        self._requests = {}
        self._tree_signature = None
        self._detail_signature = None
        self._result_entries = {}
        self._result_files = {}
        self._selected_project = None
        self._future = None
        self._closed = False
        self._epoch = 0
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="portfolio-dashboard")
        self.setObjectName("portfolioManager")
        self.setStyleSheet(STYLE)
        self._layout()
        self._updates = QTimer(self)
        self._updates.setInterval(2400)
        self._updates.timeout.connect(self.refresh)
        self._collect = QTimer(self)
        self._collect.setInterval(90)
        self._collect.timeout.connect(self._receive)
        self._updates.start()
        self.refresh()

    def _layout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 14, 15, 12)
        layout.setSpacing(10)
        header = QWidget()
        header.setObjectName("managerBar")
        row = QHBoxLayout(header)
        title = _label("Portfolio Manager")
        title.setObjectName("managerTitle")
        row.addWidget(title)
        row.addStretch(1)
        self.mode = QComboBox()
        self.mode.setAccessibleName("Global operating mode")
        self.mode.addItem("AI Only (AFK)", "afk")
        self.mode.addItem("Human Available", "human")
        self.mode.activated.connect(self._set_mode)
        self.mode.setEnabled(False)
        row.addWidget(self.mode)
        self.stop_all = _button("Stop All", self._stop_all)
        row.addWidget(self.stop_all)
        self.resume = _button("Resume scheduling", self._resume_workers)
        self.resume.hide()
        row.addWidget(self.resume)
        row.addWidget(_button("Emergency Stop", self._emergency, "emergencyButton"))
        (self.header_layout if self.header_layout is not None else layout).addWidget(header)

        scope = QHBoxLayout()
        self.scope_label = _label("Worker folder · All projects", wrap=True)
        self.scope_label.setObjectName("folderScope")
        scope.addWidget(self.scope_label, 1)
        scope.addWidget(_button("Choose folder…", self._choose_folder))
        self.start = _button("Start worker", self._start_worker, "primaryWorkerButton")
        self.start.setEnabled(False)
        scope.addWidget(self.start)
        layout.addLayout(scope)
        self.summary = _label("Loading saved projects…", wrap=True)
        self.summary.setObjectName("managerSummary")
        layout.addWidget(self.summary)

        vertical = QSplitter(Qt.Orientation.Vertical)
        horizontal = QSplitter(Qt.Orientation.Horizontal)
        vertical.addWidget(horizontal)
        navigation = QWidget()
        navigation_layout = QVBoxLayout(navigation)
        navigation_layout.setContentsMargins(0, 0, 0, 0)
        self.search = QLineEdit()
        self.search.setAccessibleName("Search projects")
        self.search.setPlaceholderText("Find a project…")
        self.search.textChanged.connect(self._rebuild_tree)
        navigation_layout.addWidget(self.search)
        self.project_tree = _tree(["Projects and folders", "Status"])
        self.project_tree.setIndentation(13)
        self.project_tree.itemSelectionChanged.connect(self._tree_selection)
        navigation_layout.addWidget(self.project_tree, 1)
        horizontal.addWidget(navigation)

        details = QWidget()
        detail_layout = QVBoxLayout(details)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        self.detail_title = _label("Select a project", wrap=True)
        self.detail_title.setObjectName("detailTitle")
        detail_layout.addWidget(self.detail_title)
        self.detail = QTextBrowser()
        self.detail.setAccessibleName("Project overview")
        self.detail.setOpenLinks(False)
        self.detail.setOpenExternalLinks(False)
        detail_layout.addWidget(self.detail, 1)
        self.review_task = _button("Review interrupted task…", self._review_task)
        self.review_task.hide()
        detail_layout.addWidget(self.review_task, alignment=Qt.AlignmentFlag.AlignLeft)
        result_layout = QHBoxLayout()
        result_layout.addWidget(_label("Files and results"), 1)
        self.open_result = _button("View selected result", self._open_result)
        self.open_result.setEnabled(False)
        result_layout.addWidget(self.open_result)
        detail_layout.addLayout(result_layout)
        self.results = _tree(["Result", "Availability"])
        self.results.setRootIsDecorated(False)
        self.results.setMaximumHeight(126)
        self.results.itemSelectionChanged.connect(self._result_selection)
        self.results.itemDoubleClicked.connect(lambda *_: self._open_result())
        detail_layout.addWidget(self.results)
        self.history = QGroupBox("Saved instructions and checkpoint")
        self.history.setCheckable(True)
        self.history.setChecked(False)
        history_layout = QVBoxLayout(self.history)
        self.raw_record = QPlainTextEdit()
        self.raw_record.setReadOnly(True)
        self.raw_record.setMaximumHeight(170)
        self.raw_record.hide()
        self.history.toggled.connect(self._history_toggled)
        history_layout.addWidget(self.raw_record)
        detail_layout.addWidget(self.history)
        horizontal.addWidget(details)
        horizontal.setSizes([325, 660])
        horizontal.setStretchFactor(1, 1)

        self.activity = QTabWidget()
        self.workers = _tree(["Worker", "Folder", "Project", "Task", "Status"])
        self.workers.setRootIsDecorated(False)
        self.workers.itemSelectionChanged.connect(self._worker_selection)
        worker_panel = QWidget()
        worker_layout = QVBoxLayout(worker_panel)
        worker_layout.addWidget(self.workers, 1)
        worker_controls = QHBoxLayout()
        self.worker_notice = _label("", wrap=True)
        worker_controls.addWidget(self.worker_notice, 1)
        self.pause_worker = _button("Pause worker", lambda: self._worker_command("pause"))
        self.resume_worker = _button("Resume worker", lambda: self._worker_command("start"))
        self.stop_worker = _button("Stop worker", lambda: self._worker_command("stop"))
        for widget in (self.pause_worker, self.resume_worker, self.stop_worker):
            widget.setEnabled(False)
            worker_controls.addWidget(widget)
        worker_layout.addLayout(worker_controls)
        self.activity.addTab(worker_panel, "Workers")

        requests_panel = QWidget()
        request_layout = QVBoxLayout(requests_panel)
        self.request_tip = _label("Human requests appear here.", wrap=True)
        request_layout.addWidget(self.request_tip)
        self.requests = _tree(["Requested action", "Project", "Worker", "Status"])
        self.requests.setRootIsDecorated(False)
        self.requests.itemSelectionChanged.connect(self._request_selection)
        request_layout.addWidget(self.requests, 1)
        self.request_details = QPlainTextEdit()
        self.request_details.setAccessibleName("Exact human request details")
        self.request_details.setReadOnly(True)
        self.request_details.setMaximumHeight(100)
        self.request_details.hide()
        request_layout.addWidget(self.request_details)
        request_buttons = QHBoxLayout()
        request_buttons.addStretch()
        self.approve = _button("Approve", lambda: self._resolve("approve"))
        self.manual_done = _button("Complete manual step", lambda: self._resolve("complete"))
        self.deny = _button("Deny", lambda: self._resolve("deny"))
        self.later = _button("Leave for later", lambda: self._resolve("later"))
        for widget in (self.approve, self.manual_done, self.deny, self.later):
            widget.setEnabled(False)
            request_buttons.addWidget(widget)
        request_layout.addLayout(request_buttons)
        self.activity.addTab(requests_panel, "Requests")
        vertical.addWidget(self.activity)
        vertical.setSizes([490, 165])
        vertical.setStretchFactor(0, 1)
        layout.addWidget(vertical, 1)
        self.notice = _label("", wrap=True)
        self.notice.setObjectName("managerNotice")
        self.notice.setAccessibleName("Portfolio Manager notice")
        layout.addWidget(self.notice)

    def _read_state(self, epoch, folder, selected, with_history):
        state = self.coordinator.snapshot()
        if hasattr(self.supervisor, "status"):
            state["worker_runtime"] = self.supervisor.status()
        if folder == NICHE_ROOT.as_posix():
            counts = state.get("counts", {})
        else:
            counts = self.coordinator.snapshot(folder).get("counts", {})
        project = next((row for row in state.get("projects", []) if _project_id(row) == selected), None)
        if project is not None and with_history and hasattr(self.coordinator, "history"):
            project["recent_history"] = self.coordinator.history(selected, limit=30)
        results, files = self._results_for(project)
        return epoch, selected, state, counts, results, files

    def refresh(self):
        """Start a refresh without performing disk reads on the GUI thread."""
        if self._closed or self._future is not None:
            return
        self._future = self._pool.submit(
            self._read_state, self._epoch, self.folder, self._selected_project, self.history.isChecked()
        )
        self._collect.start()

    def _receive(self):
        if self._future is None or not self._future.done():
            return
        self._collect.stop()
        future, self._future = self._future, None
        try:
            epoch, selected, state, counts, results, files = future.result()
        except Exception as error:
            self.notice.setText(f"Portfolio status is temporarily unavailable. {_text(error)[:500]}")
            self.start.setEnabled(False)
            return
        if epoch != self._epoch:
            self.refresh()
            return
        self._apply_state(state, counts)
        if selected == self._selected_project:
            self._update_results(results, files)
        elif self._selected_project:
            self.refresh()

    def _apply_state(self, state, counts):
        self._state = state
        self._projects = {_project_id(row): row for row in state.get("projects", []) if _project_id(row)}
        if self.on_context:
            self._selected_project = next((key for key, row in self._projects.items()
                                           if row["record_path"] == self.context_record), None)
        self._workers = {row["id"]: row for row in state.get("workers", [])}
        self._requests = {row["id"]: row for row in state.get("requests", [])}
        mode = self.mode.findData(state.get("mode"))
        if mode >= 0:
            self.mode.setCurrentIndex(mode)
        self.mode.setEnabled(mode >= 0)
        stopped = state.get("stopped") or state.get("emergency")
        self.stop_all.setEnabled(not stopped)
        self.resume.setVisible(bool(stopped))
        scope_available = self.can_start_context is None or self.can_start_context()
        self.start.setEnabled(not stopped and scope_available and counts.get("eligible", 0) > 0)
        pieces = [f"{counts.get(key, 0)} {title}" for key, title in (
            ("eligible", "eligible"), ("active", "active"), ("completed", "completed"),
            ("blocked", "blocked"), ("remaining", "remaining"),
        )]
        if state.get("emergency"):
            pieces.append("Emergency Stop is active")
        elif state.get("stopped"):
            pieces.append("Workers stopped")
        self.summary.setText(" · ".join(pieces))
        self._rebuild_tree()
        self._update_worker_table()
        self._update_request_table()
        self._render_project()

    def _set_mode(self):
        self._act(self.coordinator.set_mode, self.mode.currentData(), success="Operating mode updated.")

    def _act(self, operation, *args, success="", **kwargs):
        try:
            result = operation(*args, **kwargs)
        except Exception as error:
            self.notice.setText(_text(error, "The action could not be completed.")[:600])
        else:
            if success:
                self.notice.setText(success)
            return result
        finally:
            self._epoch += 1
            self.refresh()

    def _stop_all(self):
        def stop():
            try:
                self.supervisor.stop_all()
            finally:
                if self.on_stop_all is not None:
                    self.on_stop_all()

        self._act(stop, success="Worker scheduling stopped.")

    def _emergency(self):
        self._act(self.on_emergency, success="Emergency Stop activated.")

    def _resume_workers(self):
        self._act(self.coordinator.resume, clear_emergency=bool(self._state.get("emergency")),
                  success="Worker scheduling resumed. Computer access is managed in its own tab.")

    def _start_worker(self):
        self.start.setEnabled(False)

        def start():
            if self.start_context_worker:
                return self.start_context_worker()
            worker = self.coordinator.register(self.folder, kind="background")
            try:
                self.supervisor.start(worker["id"])
            except Exception:
                self.coordinator.set_worker_state(worker["id"], "stopped")
                raise

        self._act(start, success="Worker assigned. Follow its progress below.")

    def _choose_folder(self):
        chosen = QFileDialog.getExistingDirectory(self, "Choose a portfolio project folder", str(self.repo / self.folder))
        if chosen:
            try:
                folder = _scope_path(self.repo, chosen)
            except (ValueError, OSError):
                self.notice.setText("Choose a real folder inside business_portfolio/niches.")
                return
            self._set_folder(folder)

    def _set_folder(self, folder, *, notify=True):
        if notify and self.on_context and not self.on_context(folder):
            return
        if folder == self.folder:
            return
        self.folder = folder
        relative = PurePosixPath(folder).relative_to(NICHE_ROOT)
        label = "All projects" if not relative.parts else " / ".join(relative.parts)
        self.scope_label.setText("Worker folder · " + label)
        self.scope_label.setToolTip(str(self.repo / folder))
        self.summary.setText("Checking the selected folder…")
        self.start.setEnabled(False)
        self._epoch += 1
        self.refresh()

    def _rebuild_tree(self):
        if not hasattr(self, "project_tree"):
            return
        query = self.search.text().strip().casefold()
        projects = [p for p in self._projects.values() if not query or query in (
            _text(p.get("title")) + " " + _text(_project_id(p)) + " " + _text(p.get("niche_path"))
        ).casefold()]
        niches = {
            row["path"]: row.get("title", row["path"]) for row in self._state.get("niches", [])
            if isinstance(row.get("path"), str) and row["path"]
        }
        signature = (
            query, tuple(niches.items()),
            tuple((_project_id(p), p.get("title"), p.get("niche_path"),
                   p.get("status") or p.get("work_state")) for p in projects),
            (self.folder, self.context_record) if self.on_context else None,
        )
        if signature == self._tree_signature:
            return
        old_selection = self.project_tree.currentItem()
        old_key = old_selection.data(0, ITEM_DATA) if old_selection is not None else None
        expanded = set()
        stack = [self.project_tree.topLevelItem(i) for i in range(self.project_tree.topLevelItemCount())]
        while stack:
            item = stack.pop()
            if item.isExpanded():
                expanded.add(item.data(0, ITEM_DATA))
            stack.extend(item.child(i) for i in range(item.childCount()))
        saved_scroll = self.project_tree.verticalScrollBar().value()
        first = self._tree_signature is None
        self._tree_signature = signature
        self.project_tree.blockSignals(True)
        try:
            self.project_tree.clear()
            root = QTreeWidgetItem(self.project_tree, ["All projects"])
            root.setData(0, ITEM_DATA, ("folder", NICHE_ROOT.as_posix()))
            root.setExpanded(True)
            folder_items = {"": root}
            keys = {root.data(0, ITEM_DATA): root}
            visible_folders = set(niches) if not query else set()
            for project in projects:
                path = PurePosixPath(project.get("niche_path", ""))
                if path.parts:
                    visible_folders.add(path.as_posix())
            for path in list(visible_folders):
                visible_folders.update(parent.as_posix() for parent in PurePosixPath(path).parents if parent.parts)
            for path in sorted(visible_folders, key=lambda value: (value.count("/"), niches.get(value, value).casefold())):
                parent_path, _, last = path.rpartition("/")
                parent = folder_items.get(parent_path, root)
                item = QTreeWidgetItem(parent, [niches.get(path, last.replace("-", " ").capitalize())])
                item.setToolTip(0, item.text(0))
                key = ("folder", (NICHE_ROOT / path).as_posix())
                item.setData(0, ITEM_DATA, key)
                item.setExpanded(bool(query) or key in expanded or (first and not parent_path))
                keys[key] = item
                folder_items[path] = item
            for project in sorted(projects, key=lambda row: _text(row.get("title")).casefold()):
                identifier = _project_id(project)
                parent = folder_items.get(project.get("niche_path", ""), root)
                item = QTreeWidgetItem(parent, [_text(project.get("title"), identifier),
                                               _status(project.get("status") or project.get("work_state"))])
                item.setToolTip(0, item.text(0))
                key = ("project", identifier)
                item.setData(0, ITEM_DATA, key)
                keys[key] = item
            if self.on_context:
                context_key = ("project", self._selected_project) if self._selected_project else ("folder", self.folder)
                selected = keys.get(context_key)
            else:
                selected = keys.get(old_key) or keys.get(("project", self._selected_project))
            if selected is not None:
                ancestor = selected.parent()
                while ancestor:
                    ancestor.setExpanded(True)
                    ancestor = ancestor.parent()
                self.project_tree.setCurrentItem(selected)
            elif not self.on_context and first and projects:
                identifier = _project_id(projects[0])
                self._selected_project = identifier
                selected = keys[("project", identifier)]
                ancestor = selected.parent()
                while ancestor:
                    ancestor.setExpanded(True)
                    ancestor = ancestor.parent()
                self.project_tree.setCurrentItem(selected)
            self.project_tree.verticalScrollBar().setValue(saved_scroll)
        finally:
            self.project_tree.blockSignals(False)

    def _tree_selection(self):
        item = self.project_tree.currentItem()
        if item is None:
            return
        kind, key = item.data(0, ITEM_DATA)
        if kind == "folder":
            self._set_folder(key)
        else:
            if self.on_context and not self.on_context(self._projects[key]["record_path"]):
                return
            self._selected_project = key
            self._render_project()
            self._update_results([], {})
            self._epoch += 1
            self.refresh()

    def _render_project(self):
        project = self._projects.get(self._selected_project)
        self.review_task.setVisible(bool(self._reviewable(project)))
        if project is None:
            self.detail_title.setText("Select a project")
            self.detail.clear()
            self.raw_record.clear()
            self._detail_signature = None
            return
        overview = _project_body(project, self._workers)
        checkpoint = _text(project.get("checkpoint"))
        raw = project.get("body", "")
        if checkpoint:
            raw += "\n\nCoordinator checkpoint\n" + checkpoint
        if project.get("recent_history"):
            raw += "\n\nRecent activity\n" + "\n".join(
                f"{datetime.fromtimestamp(row['created_at']):%Y-%m-%d %H:%M} · "
                f"{_status(row['kind'])} · {_text(row.get('detail'))}"
                for row in project["recent_history"]
            )
        signature = (_project_id(project), project.get("title"), overview, raw)
        if signature == self._detail_signature:
            return
        same_project = self._detail_signature and self._detail_signature[0] == signature[0]
        scroll = self.detail.verticalScrollBar().value() if same_project else 0
        self._detail_signature = signature
        self.detail_title.setText(_text(project.get("title"), signature[0]))
        self.detail.setHtml(overview)
        self.detail.verticalScrollBar().setValue(scroll)
        self.raw_record.setPlainText(raw)

    def _history_toggled(self, opened):
        self.raw_record.setVisible(opened)
        if opened:
            self._epoch += 1
            self.refresh()

    @staticmethod
    def _reviewable(project):
        return [task for task in (project or {}).get("milestones", [])
                if task.get("status") in {"blocked", "reconcile"}]

    def _review_task(self):
        project_id = self._selected_project
        tasks = self._reviewable(self._projects.get(project_id))
        if not tasks:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Review interrupted task")
        dialog.resize(620, 480)
        layout = QVBoxLayout(dialog)
        layout.addWidget(_label("Review the saved checkpoint and verify any outside activity before returning the task to the queue.", wrap=True))
        choices = QComboBox()
        choices.setAccessibleName("Interrupted task")
        layout.addWidget(choices)
        checkpoint = QPlainTextEdit()
        checkpoint.setReadOnly(True)
        checkpoint.setAccessibleName("Saved task checkpoint")
        layout.addWidget(checkpoint, 1)
        for task in tasks:
            choices.addItem(_text(task.get("title"), "Interrupted task"), task)

        def load_checkpoint():
            task = choices.currentData()
            checkpoint.setPlainText(_text(task.get("checkpoint"), "No checkpoint recorded."))

        choices.currentIndexChanged.connect(load_checkpoint)
        load_checkpoint()
        layout.addWidget(_label("What did you verify?"))
        note = QPlainTextEdit()
        note.setAccessibleName("Your verification note")
        note.setMaximumHeight(110)
        layout.addWidget(note)
        controls = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        accept = controls.addButton("Return to queue", QDialogButtonBox.ButtonRole.AcceptRole)
        accept.setEnabled(False)
        note.textChanged.connect(lambda: accept.setEnabled(bool(note.toPlainText().strip())))
        controls.accepted.connect(dialog.accept)
        controls.rejected.connect(dialog.reject)
        layout.addWidget(controls)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._act(self.coordinator.reconcile_task, project_id, choices.currentData()["id"],
                      note=note.toPlainText().strip(), success="Reviewed task returned to the queue.")

    def _results_for(self, project):
        if not project:
            return [], {}
        # Use the same explicit deliverable list and path guards as the project browser.
        row = dict(project)
        identifier = _project_id(project)
        row["id"] = identifier
        if not row.get("path") or PurePosixPath(row["path"]).parts[:1] == ("business_portfolio",):
            record = PurePosixPath(row.get("record_path") or row.get("path") or "")
            if record.parts and record.parts[0] == "business_portfolio":
                row["path"] = record.relative_to("business_portfolio").as_posix()
            else:
                return [], {}
        rows, files = public_results(self.repo / "business_portfolio", {"records": [row]})
        entries = rows.get(identifier, [])
        database = getattr(self.coordinator, "db_path", None)
        if database is not None:
            state_directory = Path(database).parent
            for task in row.get("milestones", []):
                evidence = task.get("evidence")
                if task.get("status") != "completed" or not evidence:
                    continue
                key = "worker:" + _text(task.get("id"))
                artifact = (_worker_artifact(state_directory, identifier, evidence)
                            if task.get("verified") is True else None)
                entries.append({
                    "label": "Worker result · " + _text(task.get("title"), "Saved local draft"),
                    "key": key,
                    "available": artifact is not None,
                    "note": "Verified local worker output. Preview opens as plain text." if artifact else
                            "The saved worker result could not be verified.",
                    "worker_evidence": evidence,
                })
        return entries, files

    def _update_results(self, rows, files):
        selected = self.results.currentItem()
        key = selected.data(0, ITEM_DATA) if selected is not None else None
        self._result_entries = {}
        self._result_files = files
        self.results.blockSignals(True)
        try:
            self.results.clear()
            for row in rows:
                result_key = row.get("key") or row.get("url")
                available = "Website" if row.get("url") else ("Available" if row.get("available") else "Unavailable")
                item = QTreeWidgetItem(self.results, [row["label"], available])
                item.setData(0, ITEM_DATA, result_key)
                item.setToolTip(0, row.get("note", ""))
                self._result_entries[result_key] = row
                if key == result_key:
                    self.results.setCurrentItem(item)
        finally:
            self.results.blockSignals(False)
        self._result_selection()

    def _result_selection(self):
        item = self.results.currentItem()
        row = self._result_entries.get(item.data(0, ITEM_DATA), {}) if item else {}
        self.open_result.setEnabled(bool(row.get("url") or row.get("available")))
        self.open_result.setText("Open website" if row.get("url") else "View selected result")

    def _open_result(self):
        item = self.results.currentItem()
        if not item:
            return
        key = item.data(0, ITEM_DATA)
        row = self._result_entries.get(key, {})
        url = row.get("url")
        if url:
            registered = PUBLIC_LINKS.get(self._selected_project)
            parsed = urlsplit(url)
            if registered and url == registered[1] and parsed.scheme == "https" and not parsed.username and not parsed.password:
                if not QDesktopServices.openUrl(QUrl(url)):
                    self.notice.setText("Windows could not open the approved website.")
            return
        if row.get("worker_evidence") and row.get("available"):
            artifact = _worker_artifact(Path(self.coordinator.db_path).parent, self._selected_project, row["worker_evidence"])
            if artifact is None:
                self.notice.setText("The worker result changed or is no longer available.")
                return
            checked, preview = artifact
            self._show_preview(row["label"], checked, preview[:250_000], truncated=len(preview) > 250_000)
            return
        entry = self._result_files.get(key)
        if not entry or not row.get("available"):
            return
        expected, relative, *scope = entry
        try:
            if scope:
                checked = result_file(self.repo / "business_portfolio", self._selected_project, relative)
            else:
                checked = safe_file(self.repo, relative)
            if checked is None or checked != expected or checked.suffix.lower() not in {".md", ".txt", ".csv", ".json"}:
                raise ValueError("This file is no longer available for preview.")
            with checked.open("rb") as handle:
                data = handle.read(250_001)
                observed = os.fstat(handle.fileno())
            if not os.path.samestat(observed, checked.stat()) or build_browser.linked_input(checked):
                raise ValueError("This file changed during preview. Refresh and try again.")
            preview = data[:250_000].decode("utf-8", errors="replace")
        except (OSError, ValueError) as error:
            self.notice.setText(_text(error)[:500])
            return
        self._show_preview(row["label"], checked, preview, truncated=len(data) > 250_000)

    def _show_preview(self, title, path, preview, *, truncated):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.resize(760, 570)
        layout = QVBoxLayout(dialog)
        layout.addWidget(_label(str(path), wrap=True))
        if truncated:
            layout.addWidget(_label("Preview shows the beginning of this file."))
        body = QPlainTextEdit()
        body.setReadOnly(True)
        body.setPlainText(preview)
        layout.addWidget(body, 1)
        layout.addWidget(_button("Close", dialog.accept))
        dialog.exec()

    @staticmethod
    def _populate(tree, rows):
        previous = tree.currentItem()
        selected = previous.data(0, ITEM_DATA) if previous else None
        tree.blockSignals(True)
        try:
            tree.clear()
            for identifier, columns in rows:
                item = QTreeWidgetItem(tree, columns)
                item.setData(0, ITEM_DATA, identifier)
                if identifier == selected:
                    tree.setCurrentItem(item)
        finally:
            tree.blockSignals(False)

    def _update_worker_table(self):
        rows = []
        for worker in self._workers.values():
            if self.context_worker and worker["id"] != self.context_worker():
                continue
            project = self._projects.get(worker.get("project_id"), {})
            task = project.get("current_task") or {}
            folder = _text(worker.get("folder"))
            if folder == NICHE_ROOT.as_posix():
                folder = "All projects"
            else:
                folder = folder.removeprefix(NICHE_ROOT.as_posix() + "/")
            rows.append((worker["id"], [_text(worker.get("label"), "Codex worker"), folder,
                                       _text(project.get("title"), "—"),
                                       _text(task.get("title") or task.get("objective"), "—"),
                                       _status(worker.get("status") or worker.get("state"))]))
        self._populate(self.workers, rows)
        self.activity.setTabText(0, f"Workers ({len(rows)})" if rows else "Workers")
        self._worker_selection()

    def _worker_selection(self):
        item = self.workers.currentItem()
        row = self._workers.get(item.data(0, ITEM_DATA), {}) if item else {}
        state = row.get("state")
        self.pause_worker.setEnabled(state == "running")
        self.resume_worker.setEnabled(state == "paused" and not self._state.get("stopped") and not self._state.get("emergency"))
        self.stop_worker.setEnabled(state in ("running", "paused"))
        runtime = self._state.get("worker_runtime", {}).get(row.get("id"), {})
        self.worker_notice.setText(_text(row.get("last_error") or runtime.get("detail"), "")[:480])

    def _worker_command(self, command):
        item = self.workers.currentItem()
        if not item:
            return
        identifier = item.data(0, ITEM_DATA)
        worker = self._workers.get(identifier, {})
        if worker.get("kind") == "background":
            operation = {"pause": self.supervisor.pause, "start": self.supervisor.start,
                         "stop": self.supervisor.stop}[command]
            self._act(operation, identifier)
        else:
            self._act(self.coordinator.set_worker_state, identifier,
                      {"pause": "paused", "start": "running", "stop": "stopped"}[command])

    def _update_request_table(self):
        rows = []
        for request in self._requests.values():
            project = self._projects.get(request.get("project_id"), {})
            worker = self._workers.get(request.get("worker_id"), {})
            rows.append((request["id"], [_text(request.get("action"), "Human input needed"),
                                       _text(project.get("title"), _text(request.get("project_id"), "—")),
                                       _text(worker.get("label"), "—"),
                                       "For later" if request.get("status") == "deferred" else "Pending"]))
        self._populate(self.requests, rows)
        if self._state.get("mode") == "human":
            self.request_tip.setText(f"{len(rows)} pending human requests." if rows else "No pending human requests.")
            self.activity.setTabText(1, f"Requests ({len(rows)})" if rows else "Requests")
        else:
            self.request_tip.setText("AI Only queues requests for later. Choose Human Available to review them.")
            self.activity.setTabText(1, "Requests")
        self._request_selection()

    def _request_selection(self):
        item = self.requests.currentItem()
        row = self._requests.get(item.data(0, ITEM_DATA), {}) if item else {}
        manual = row.get("kind") in {"login", "manual"}
        allowed = bool(row) and self._state.get("mode") == "human" and not self._state.get("emergency")
        self.approve.setVisible(not manual)
        self.manual_done.setVisible(manual)
        can_continue = allowed and not self._state.get("stopped")
        self.approve.setEnabled(can_continue and not manual)
        self.manual_done.setEnabled(can_continue and manual)
        self.deny.setEnabled(allowed)
        self.later.setEnabled(allowed)
        fields = (("Why", "reason"), ("Scope", "scope"), ("Cost in CAD", "cost_cad"),
                  ("Consequences", "consequences"), ("Afterward", "after"))
        self.request_details.setVisible(bool(row))
        self.request_details.setPlainText("\n".join(
            title + " · " + _text(row.get(key), "Unknown") for title, key in fields
        ) if row else "")

    def _resolve(self, decision):
        item = self.requests.currentItem()
        if item and self._state.get("mode") == "human" and not self._state.get("emergency"):
            self._act(self.coordinator.resolve_request, item.data(0, ITEM_DATA), decision,
                      success="Request updated.")

    def shutdown(self):
        """Stop polling when the containing bridge window closes."""
        self._closed = True
        self._updates.stop()
        self._collect.stop()
        self._pool.shutdown(wait=True, cancel_futures=True)
