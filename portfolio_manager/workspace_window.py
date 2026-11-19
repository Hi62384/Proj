"""Independent views of the shared Portfolio Manager controller."""
from concurrent.futures import ThreadPoolExecutor
import os
import json
import hashlib
from pathlib import Path, PurePosixPath
import re

from PySide6.QtCore import QEvent, QSize, QSignalBlocker, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QIcon, QImageReader, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox,
                               QMenu, QPlainTextEdit, QPushButton, QScrollArea, QSplitter,
                               QStyle, QTabWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

from .workspace import context_path


ROLE = int(Qt.ItemDataRole.UserRole)
WORK_PROMPT = (
    '/goal Complete the project currently selected in this chat’s Portfolio Manager workspace.\n\n'
    'First, read the current selection, its full project record, relevant project instructions, and the latest authorized checkpoint. Preserve existing work and identify the next actionable tasks.\n\n'
    'Work autonomously through all remaining tasks that can be completed with the available access, resources, and existing authorization. Continue across turns until the project is complete or no further authorized work can be performed. Do not stop merely because you completed one task, produced a checkpoint, sent a progress update, or several minutes have passed.\n\n'
    'Make reasonable decisions within the project’s stated scope. Implement, verify, fix problems, document evidence, update the appropriate project checkpoint, and proceed to the next actionable task. Give brief progress updates without ending the work.\n\n'
    'Respect the project’s budget, privacy, permissions, and approval requirements. Do not invent results or repeat uncertain external actions. If an action requires my approval, payment, access, another person, or an external change, complete all independent authorized work first. Then clearly report the blocker, what is already prepared, and the exact action needed from me.\n\n'
    'Mark the goal complete only when the project’s required outcomes are actually achieved and verified. If the project is ongoing by nature, continue until the currently authorized work is finished, then report what remains for future operation.'
)
NICHE_ID_ROLE = ROLE + 2
WORKING_ROLE = ROLE + 3
MAX_PREVIEW = 128_000
IMAGE_FORMATS = {'.png': b'png', '.jpg': b'jpeg', '.jpeg': b'jpeg', '.bmp': b'bmp',
                 '.gif': b'gif', '.webp': b'webp', '.ico': b'ico'}
TEXT_SUFFIXES = {'.txt', '.md', '.py', '.js', '.jsx', '.ts', '.tsx', '.css', '.html',
                 '.json', '.csv', '.tsv', '.yaml', '.yml', '.toml', '.ini', '.ps1', '.cmd',
                 '.sql', '.xml', '.rst', '.bat', '.sh', '.svg', '.go', '.rs', '.java', '.cs'}


def children(repo, parent):
    """List visible entries without following aliases or exposing blocked paths."""
    found = []
    for child in parent.iterdir():
        name = child.relative_to(repo).as_posix()
        try:
            path = context_path(repo, name)
        except (ValueError, OSError):
            continue
        found.append((name, path.is_dir()))
    return sorted(found, key=lambda item: (not item[1], item[0].casefold()))


def search_paths(repo, query):
    return [(name, directory) for name, directory in project_entries(repo)
            if query in name.casefold()][:100]


def project_entries(repo, niches=None):
    """Canonical project records, all active niches, and their parent folders."""
    niche_root = repo / 'business_portfolio' / 'niches'
    visible = set()
    niches = niche_entries(repo) if niches is None else niches
    for name, *_ in niches:
        visible.add((name, True))
        for parent in PurePosixPath(name).parents:
            if parent.as_posix() != '.':
                visible.add((parent.as_posix(), True))
    for folder, dirs, files in os.walk(niche_root, followlinks=False):
        dirs[:] = [name for name in dirs if not name.startswith('.') and
                   not (Path(folder) / name).is_symlink()]
        if Path(folder).name != 'projects':
            continue
        for file in files:
            if not file.lower().endswith('.md'):
                continue
            path = Path(folder) / file
            try:
                relative = context_path(repo, path).relative_to(repo)
            except (ValueError, OSError):
                continue
            visible.add((relative.as_posix(), False))
            for parent in relative.parents:
                if parent.as_posix() != '.':
                    visible.add((parent.as_posix(), True))
    priorities = {row[0]: row[3] for row in niches}
    return sorted(visible, key=lambda item: (item[0].count('/'),
                                            priorities.get(item[0], 999), item[0].casefold()))


def history_entries(repo):
    """Archived canonical records remain selectable without a repository-wide scan."""
    visible = set()
    archive = repo / 'business_portfolio' / 'archive'
    for snapshot in ('2026-11-15-legacy', '2026-11-15-taxonomy-view-v1'):
        base = archive / snapshot / 'niches'
        if not base.is_dir():
            continue
        for folder, dirs, files in os.walk(base, followlinks=False):
            dirs[:] = [name for name in dirs if not name.startswith('.') and
                       not (Path(folder) / name).is_symlink()]
            if Path(folder).name != 'projects':
                continue
            for file in files:
                if not file.lower().endswith('.md'):
                    continue
                try:
                    relative = context_path(repo, Path(folder) / file).relative_to(repo)
                except (ValueError, OSError):
                    continue
                visible.add((relative.as_posix(), False))
                for parent in relative.parents:
                    if parent.as_posix() != '.':
                        visible.add((parent.as_posix(), True))
    return sorted(visible, key=lambda item: (item[0].count('/'), item[0].casefold()))


def niche_entries(repo):
    """Show the complete active category/niche hierarchy in declared order."""
    base = repo / 'business_portfolio' / 'niches'
    rows = []
    if not base.is_dir():
        return rows
    for metadata in base.rglob('NICHE.json'):
        folder = metadata.parent
        if not folder.is_dir() or folder.is_symlink():
            continue
        try:
            relative = context_path(repo, folder).relative_to(repo).as_posix()
            meta = json.loads(metadata.read_text(encoding='utf-8'))
            if meta.get('path') != folder.relative_to(base).as_posix():
                continue
            count = sum(1 for p in folder.rglob('projects/*.md') if p.is_file())
            rows.append((relative, meta['title'], count, meta.get('priority', 999),
                         meta['id'], meta.get('working', False), meta.get('parent')))
        except (ValueError, OSError, KeyError, TypeError):
            continue
    return sorted(rows, key=lambda row: (row[0].count('/'), row[3], row[1].casefold()))


class WorkspaceWindow(QMainWindow):
    def __init__(self, host, workspace, *, on_emergency, on_stop_all, on_access, on_close):
        super().__init__()
        self.host = host
        self.repo = Path(host.repo).resolve()
        self.workspace_id = workspace['id']
        self.workspace_state = None
        self.on_close = on_close
        self._search = None
        self._search_query = None
        self._pending_search = None
        self._search_view = False
        self._preview_signature = None
        self._preview_readme = None
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='workspace-files')
        self._project_entries = []
        self._history_entries = []
        self._niche_entries = []
        self._working_signature = None
        self._research_prompt = None
        self._budget_setting = self.repo / 'business_portfolio' / '.research_prompt_budget'
        self._entry_future = self._pool.submit(self._load_navigation_entries, self.repo)
        self._entries_ready = False
        self._tree_mode = 'projects'
        self._file_loads = {}
        self._folder_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        marked = self._folder_icon.pixmap(32, 32)
        painter = QPainter(marked)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor('white'))
        painter.setBrush(QColor('#16835d'))
        painter.drawEllipse(20, 1, 10, 10)
        painter.end()
        self._working_folder_icon = QIcon(marked)
        self._file_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        completed = QPixmap(32, 32)
        completed.fill(Qt.GlobalColor.transparent)
        painter = QPainter(completed)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor('#16835d'))
        painter.drawEllipse(1, 1, 30, 30)
        pen = QPen(QColor('white'), 4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(8, 16, 13, 21)
        painter.drawLine(13, 21, 24, 10)
        painter.end()
        self._completed_file_icon = QIcon(completed)
        self.setWindowTitle('Portfolio Manager | Chat ' + self.workspace_id[:8])
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.resize(1080, 720)
        self.setMinimumSize(620, 440)
        frame = QWidget(self)
        frame.setObjectName('workspaceFrame')
        frame.setStyleSheet('''
            QWidget#workspaceFrame { background: #f5f7f8; color: #1a2930; font-family: "Segoe UI"; font-size: 10pt; }
            QLineEdit, QTreeWidget, QPlainTextEdit { background: white; border: 1px solid #d7e1df; border-radius: 5px; padding: 6px; selection-background-color: #cce8df; selection-color: #12382e; }
            QPushButton { background: white; border: 1px solid #c8d6d2; border-radius: 5px; padding: 7px 12px; }
            QPushButton:hover { background: #eaf3f0; }
            QPushButton:focus { border: 2px solid #20594b; }
            QTabBar::tab { padding: 8px 15px; }
            QTabBar::tab:selected { color: #20594b; font-weight: 600; }
        ''')
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)
        header = QHBoxLayout()
        self.selection_label = QLabel('Portfolio Manager')
        self.selection_label.setTextFormat(Qt.TextFormat.PlainText)
        self.selection_label.setStyleSheet('font-size: 22px; font-weight: 600; color: #183a32;')
        header.addWidget(self.selection_label, 1)
        self.working_count = QLabel('0 working niches')
        self.working_count.setAccessibleName('Working niche count')
        header.addWidget(self.working_count)
        header.addWidget(QLabel('Chat ' + self.workspace_id[:8]))
        self.mode = QComboBox()
        self.mode.setAccessibleName('Global availability')
        self.mode.addItem('AI Only (AFK)', 'afk')
        self.mode.addItem('Human Available', 'human')
        self.mode.activated.connect(self._set_mode)
        header.addWidget(self.mode)
        more = QPushButton('⋯')
        more.setAccessibleName('More options')
        menu = QMenu(more)
        menu.addAction('Computer Access', on_access)
        menu.addAction('Emergency Stop', on_emergency)
        more.setMenu(menu)
        header.addWidget(more)
        layout.addLayout(header)
        self.notice = QLabel()
        self.notice.setWordWrap(True)
        self.notice.hide()
        layout.addWidget(self._make_explorer(), 1)
        layout.addWidget(self.notice)
        self.setCentralWidget(frame)
        for widget in (self, frame, self.tree, self.tree.viewport(), self.preview,
                       self.preview.viewport(), self.project_tabs, self.image_scroll):
            widget.setAcceptDrops(True)
            if widget is not self:
                widget.installEventFilter(self)
        self._sync = QTimer(self)
        self._sync.setInterval(400)
        self._sync.timeout.connect(self.sync)
        self.apply_workspace(workspace)
        self.sync()
        self._sync.start()

    def _make_explorer(self):
        splitter = QSplitter()
        navigator = QWidget()
        navigator.setMinimumWidth(300)
        layout = QVBoxLayout(navigator)
        self.view_mode = QComboBox()
        self.view_mode.setAccessibleName('Workspace section')
        self.view_mode.addItem('Projects', 'projects')
        self.view_mode.addItem('Niches', 'niches')
        self.view_mode.addItem('History & Existing Work', 'history')
        self.view_mode.addItem('Repository files', 'files')
        self.view_mode.activated.connect(self._change_view)
        layout.addWidget(self.view_mode)
        self.find = QLineEdit()
        self.find.setAccessibleName('Search projects')
        self.find.setPlaceholderText('Search projects, then press Enter')
        self.find.returnPressed.connect(self._find_files)
        layout.addWidget(self.find)
        self.search_status = QLabel()
        self.search_status.setWordWrap(True)
        self.search_status.hide()
        layout.addWidget(self.search_status)
        self.tree = QTreeWidget()
        self.tree.setIconSize(QSize(24, 24))
        self.tree.setHeaderLabels(['Projects'])
        self.tree.itemSelectionChanged.connect(self._select_file)
        self.tree.itemExpanded.connect(self._expand)
        self.tree.itemChanged.connect(self._niche_working_changed)
        layout.addWidget(self.tree)
        splitter.addWidget(navigator)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setAccessibleName('Selected file or folder preview')
        self.project_tabs = QTabWidget()
        self.project_tabs.setAccessibleName('Project details')
        self.project_overview = QPlainTextEdit()
        self.project_files = QPlainTextEdit()
        self.project_results = QPlainTextEdit()
        self.project_tasks = QPlainTextEdit()
        self.project_record = QPlainTextEdit()
        for title, panel in [('Overview', self.project_overview), ('Files', self.project_files),
                             ('Results', self.project_results), ('Tasks & Progress', self.project_tasks),
                             ('Complete record', self.project_record)]:
            panel.setReadOnly(True)
            self.project_tabs.addTab(panel, title)
        self.project_tabs.hide()
        self.image = QLabel()
        self.image.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidget(self.image)
        detail = QWidget()
        details = QVBoxLayout(detail)
        self.path_label = QLabel()
        self.path_label.setWordWrap(True)
        self.path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details.addWidget(self.path_label)
        self.research_tools = QWidget()
        research_layout = QFormLayout(self.research_tools)
        self.research_budget = QLineEdit(self._load_research_budget())
        self.research_budget.setAccessibleName('Budget ceiling in CAD')
        self.research_budget.setPlaceholderText('100')
        self.research_budget.textChanged.connect(self._save_research_budget)
        self.copy_research_prompt = QPushButton('Copy Megaprompt')
        self.copy_research_prompt.setAccessibleName('Copy Megaprompt')
        prompt_menu = QMenu(self.copy_research_prompt)
        prompt_menu.addAction('Research a Business Opportunity', lambda: self._copy_megaprompt('research'))
        prompt_menu.addAction('Develop My Business Idea', lambda: self._copy_megaprompt('idea'))
        self.copy_research_prompt.setMenu(prompt_menu)
        research_layout.addRow('Budget ceiling (CAD)', self.research_budget)
        research_layout.addRow(self.copy_research_prompt)
        self.copy_work_prompt = QPushButton('Copy Work Prompt')
        self.copy_work_prompt.setAccessibleName('Copy Work Prompt')
        self.copy_work_prompt.clicked.connect(self._copy_work_prompt)
        research_layout.addRow(self.copy_work_prompt)
        details.addWidget(self.research_tools)
        self.project_actions = QWidget()
        actions = QHBoxLayout(self.project_actions)
        actions.setContentsMargins(0, 0, 0, 0)
        self.complete_project_button = QPushButton('Mark Complete')
        self.complete_project_button.clicked.connect(lambda: self._project_action(
            'reopen' if self.complete_project_button.property('is_complete') else 'complete'))
        self.delete_project_button = QPushButton('Delete Project')
        self.delete_project_button.clicked.connect(lambda: self._project_action('delete'))
        actions.addWidget(self.complete_project_button)
        actions.addWidget(self.delete_project_button)
        actions.addStretch()
        self.project_actions.hide()
        details.addWidget(self.project_actions)
        details.addWidget(self.project_tabs)
        details.addWidget(self.preview)
        details.addWidget(self.image_scroll)
        self.image_scroll.hide()
        splitter.addWidget(detail)
        splitter.setChildrenCollapsible(False)
        splitter.setSizes([320, 760])
        splitter.setStretchFactor(1, 2)
        self._root_node()
        return splitter

    @staticmethod
    def _load_navigation_entries(repo):
        niches = niche_entries(repo)
        return project_entries(repo, niches), history_entries(repo), niches

    def _set_mode(self):
        try:
            self.host.coordinator.set_mode(self.mode.currentData())
            self.notice.hide()
        except (ValueError, OSError, RuntimeError) as error:
            self.notice.setText(str(error)[:400])
            self.notice.show()
        self.sync()

    def _copy_work_prompt(self):
        QApplication.clipboard().setText(WORK_PROMPT)
        self.notice.setText('Work prompt copied to the clipboard.')
        self.notice.show()

    def _node(self, parent, name, directory, *, full=False):
        label = name if full else PurePosixPath(name).name
        if not full and not directory and '/projects/' in name and name.lower().endswith('.md'):
            stem = PurePosixPath(name).stem
            match = re.match(r'([a-z]+-[0-9]+)-(.+)', stem, re.I)
            if match:
                label = match.group(1).upper() + ' · ' + match.group(2).replace('-', ' ').title()
        item = QTreeWidgetItem(parent, [label])
        item.setIcon(0, self._folder_icon if directory else self._file_icon)
        if not directory and '/projects/' in name:
            self._set_project_icon(item, name)
        item.setData(0, ROLE, name)
        item.setData(0, ROLE + 1, directory)
        if directory:
            item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
        return item

    def _set_project_icon(self, item, name):
        try:
            from business_portfolio.tools.build_browser import parse_project
            path = context_path(self.repo, name)
            meta, _ = parse_project(path.read_text(encoding='utf-8'))
            complete = meta.get('work_state') == 'completed'
            item.setIcon(0, self._completed_file_icon if complete else self._file_icon)
            item.setToolTip(0, 'Completed project' if complete else 'Project record')
        except (OSError, ValueError, UnicodeError):
            pass

    def _project_action(self, action):
        selection = self.workspace_state['selection']
        try:
            path = context_path(self.repo, selection)
            raw = path.read_bytes()
            expected = hashlib.sha256(raw).hexdigest()
            if action == 'delete':
                answer = QMessageBox.question(self, 'Delete project',
                    f'Move {path.name} to the local project trash? Project source files are not deleted.',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No)
                if answer != QMessageBox.StandardButton.Yes:
                    return
            from .project_actions import update_project
            saved = update_project(self.host, selection, expected, action)
            if action == 'delete':
                self.select(path.parent.parent.relative_to(self.repo).as_posix())
                self.notice.setText(f'Project moved to local trash: {saved.name}')
            else:
                self.notice.setText('Project reopened.' if action == 'reopen' else 'Project marked complete.')
                self._preview(selection)
            self.notice.show()
            self._entry_future = self._pool.submit(self._load_navigation_entries, self.repo)
            self._entries_ready = False
            self._refresh_project_icons()
        except (OSError, ValueError, RuntimeError) as error:
            self.notice.setText('Could not update project: ' + str(error)[:500])
            self.notice.show()

    def _refresh_project_icons(self):
        def visit(item):
            name = item.data(0, ROLE)
            if isinstance(name, str) and '/projects/' in name and not item.data(0, ROLE + 1):
                self._set_project_icon(item, name)
            for i in range(item.childCount()):
                visit(item.child(i))
        if self.tree.topLevelItemCount():
            visit(self.tree.topLevelItem(0))

    def _root_node(self):
        self._search_view = False
        self.tree.setUpdatesEnabled(False)
        try:
            self._populate_root_node()
        finally:
            self.tree.setUpdatesEnabled(True)

    def _populate_root_node(self):
        with QSignalBlocker(self.tree):
            self.tree.clear()
            root = self._node(self.tree, '.', True, full=True)
            root.setText(0, self.repo.name)
            if not self._entries_ready and not self._niche_entries and self._tree_mode != 'files':
                self._node(root, 'Loading navigation…', False, full=True)
                root.setExpanded(True)
                return
            if self._tree_mode == 'files':
                root.setExpanded(True)
                self._expand(root)
                return
            if self._tree_mode == 'niches':
                nodes = {'.': root}
                for name, title, count, _, ident, working, parent_id in self._niche_entries:
                    parent = PurePosixPath(name).parent.as_posix()
                    missing = []
                    ancestor = parent
                    while ancestor not in nodes:
                        missing.append(ancestor)
                        ancestor = PurePosixPath(ancestor).parent.as_posix()
                    for ancestor in reversed(missing):
                        above = PurePosixPath(ancestor).parent.as_posix()
                        nodes[ancestor] = self._node(nodes[above], ancestor, True)
                    node = self._node(nodes[parent], name, True)
                    nodes[name] = node
                    if parent_id is None:
                        node.setText(0, f'{title} · {self._category_working_count(name)} working · {"Working" if working else "Not Working"}')
                    else:
                        node.setText(0, f'{title} · {count} {"project" if count == 1 else "projects"} · {"Working" if working else "Not Working"}')
                    node.setData(0, NICHE_ID_ROLE, ident)
                    node.setData(0, WORKING_ROLE, working)
                    node.setIcon(0, self._working_folder_icon if working else self._folder_icon)
                    node.setFlags(node.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    node.setCheckState(0, Qt.CheckState.Checked if working else Qt.CheckState.Unchecked)
                    node.setToolTip(0, 'Working marks this niche and its parents. It does not start a worker.')
                    if not count:
                        node.setForeground(0, QBrush(QColor('#87938f')))
                        node.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.DontShowIndicatorWhenChildless)
                root.setExpanded(True)
                return
            nodes = {'.': root}
            entries = self._history_entries if self._tree_mode == 'history' else self._project_entries
            for name, directory in entries:
                parent = PurePosixPath(name).parent.as_posix()
                nodes[name] = self._node(nodes[parent], name, directory)
                if self._tree_mode == 'history':
                    labels = {
                        '2026-11-15-legacy': 'Earlier projects',
                        '2026-11-15-taxonomy-view-v1': 'Previous niche layout',
                    }
                    if PurePosixPath(name).name in labels:
                        nodes[name].setText(0, labels[PurePosixPath(name).name])
                if self._tree_mode == 'projects':
                    niche = next((row for row in self._niche_entries if row[0] == name), None)
                    if niche:
                        count = niche[2]
                        is_category = niche[6] is None
                        summary = self._category_working_count(name) if is_category else None
                        label = (f'{niche[1]} · {summary} working · {"Working" if niche[5] else "Not Working"}' if is_category else
                                 f'{niche[1]} · {count} {"project" if count == 1 else "projects"} · {"Working" if niche[5] else "Not Working"}')
                        nodes[name].setText(0, label)
                        nodes[name].setData(0, NICHE_ID_ROLE, niche[4])
                        nodes[name].setData(0, WORKING_ROLE, niche[5])
                        nodes[name].setIcon(0, self._working_folder_icon if niche[5] else self._folder_icon)
                        nodes[name].setFlags(nodes[name].flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        nodes[name].setCheckState(0, Qt.CheckState.Checked if niche[5] else Qt.CheckState.Unchecked)
                        nodes[name].setToolTip(0, 'Working marks this niche and its parents. It does not start a worker.')
                        if count == 0:
                            nodes[name].setForeground(0, QBrush(QColor('#87938f')))
                            nodes[name].setChildIndicatorPolicy(
                                QTreeWidgetItem.ChildIndicatorPolicy.DontShowIndicatorWhenChildless)
            root.setExpanded(True)

    def _change_view(self):
        self._tree_mode = self.view_mode.currentData()
        self.find.clear()
        self._search = None
        self._pending_search = None
        self.search_status.hide()
        self.tree.setHeaderLabels([self.view_mode.currentText()])
        self._root_node()

    def _niche_working_changed(self, item, column):
        if column != 0 or not item.data(0, NICHE_ID_ROLE):
            return
        value = item.checkState(0) == Qt.CheckState.Checked
        if value == item.data(0, WORKING_ROLE):
            return
        from business_portfolio.tools.niche_settings import set_working
        try:
            set_working(self.repo / 'business_portfolio', item.data(0, NICHE_ID_ROLE), value)
            target = next(row for row in self._niche_entries if row[4] == item.data(0, NICHE_ID_ROLE))
            target_path = target[0]
            self._niche_entries = [(*row[:5], value, *row[6:]) if
                row[4] == target[4] or (value and target_path.startswith(row[0] + '/')) else row
                for row in self._niche_entries]
            self._refresh_working_rows()
            self._update_working_count()
            self.notice.setText(('Working' if value else 'Not Working') + ' focus setting saved for ' +
                                item.text(0).split(' · ', 1)[0] + '.')
            self.notice.show()
        except (OSError, ValueError, TimeoutError) as error:
            with QSignalBlocker(self.tree):
                item.setCheckState(0, Qt.CheckState.Checked if item.data(0, WORKING_ROLE) else Qt.CheckState.Unchecked)
            self.notice.setText(str(error)[:300])
            self.notice.show()

    def eventFilter(self, watched, event):
        if event.type() in (QEvent.Type.DragEnter, QEvent.Type.DragMove, QEvent.Type.Drop):
            return self._project_drop_event(event)
        return super().eventFilter(watched, event)

    def dragEnterEvent(self, event):
        self._project_drop_event(event)

    def dragMoveEvent(self, event):
        self._project_drop_event(event)

    def dropEvent(self, event):
        self._project_drop_event(event)

    def _project_drop_event(self, event):
        urls = event.mimeData().urls()
        if not urls or not all(url.isLocalFile() and url.toLocalFile().lower().endswith('.md') for url in urls):
            event.ignore()
            return False
        if event.type() != QEvent.Type.Drop:
            event.acceptProposedAction()
            return True
        from .project_import import import_projects
        try:
            ids = import_projects(self.repo, self.workspace_state['selection'],
                                  [url.toLocalFile() for url in urls])
            self.notice.setText('Imported: ' + ', '.join(ids))
            self.notice.show()
            self._entry_future = self._pool.submit(self._load_navigation_entries, self.repo)
            self._entries_ready = False
            event.acceptProposedAction()
        except (OSError, ValueError, RuntimeError) as error:
            self.notice.setText('Import failed: ' + str(error)[:600])
            self.notice.show()
            event.ignore()
        return True
    def _focus_tree(self, selection, *, reveal=True):
        with QSignalBlocker(self.tree):
            if self._search_view:
                for index in range(self.tree.topLevelItemCount()):
                    item = self.tree.topLevelItem(index)
                    if item.data(0, ROLE) == selection:
                        self.tree.setCurrentItem(item)
                        return
                self.tree.setCurrentItem(None)
                return
            item = self.tree.topLevelItem(0)
            for parent in (*reversed(PurePosixPath(selection).parents), PurePosixPath(selection)):
                if parent.as_posix() == '.':
                    continue
                if reveal:
                    item.setExpanded(True)
                item = next((item.child(i) for i in range(item.childCount())
                             if item.child(i).data(0, ROLE) == parent.as_posix()), None)
                if item is None:
                    return
            if self.tree.currentItem() is not item:
                self.tree.setCurrentItem(item)
                if reveal:
                    self.tree.scrollToItem(item)

    def _expand(self, node):
        if self._tree_mode != 'files' or not node.data(0, ROLE + 1):
            return
        name = node.data(0, ROLE)
        if name in self._file_loads or node.childCount():
            return
        try:
            folder = context_path(self.repo, name)
        except (ValueError, OSError):
            return
        self._file_loads[name] = (node, self._pool.submit(children, self.repo, folder))

    def _find_files(self):
        query = self.find.text().strip().casefold()
        if not query:
            self._search = None
            self._search_query = None
            self._pending_search = None
            self.search_status.hide()
            self._root_node()
            self._focus_tree(self.workspace_state['selection'])
        elif self._search is None:
            self.search_status.setText('Searching files…')
            self.search_status.show()
            self._search_query = query
            entries = self._history_entries if self._tree_mode == 'history' else self._project_entries
            self._search = self._pool.submit(lambda: [(name, directory) for name, directory
                                                       in entries if query in name.casefold()][:100])
        else:
            self.search_status.setText('Searching files…')
            self.search_status.show()
            self._pending_search = query

    def _select_file(self):
        item = self.tree.currentItem()
        if item:
            if not self.select(item.data(0, ROLE)):
                self._focus_tree(self.workspace_state['selection'])

    def select(self, path):
        try:
            update = self.host.select(self.workspace_id, path, revision=self.workspace_state['revision'])
        except (ValueError, OSError, RuntimeError) as error:
            self.notice.setText(str(error)[:400])
            self.notice.show()
            self.sync()
            return False
        self.apply_workspace(update)
        return True

    def sync(self):
        try:
            if self._entries_ready and self._tree_mode in {'projects', 'niches'}:
                signature = self._current_working_signature()
                if signature != self._working_signature:
                    self._working_signature = signature
                    self._entries_ready = False
                    self._entry_future = self._pool.submit(self._load_navigation_entries, self.repo)
            if not self._entries_ready and self._entry_future.done():
                try:
                    projects, history, niches = self._entry_future.result()
                    old_structure = [(r[0], r[1], r[2], r[3], r[4], r[6]) for r in self._niche_entries]
                    new_structure = [(r[0], r[1], r[2], r[3], r[4], r[6]) for r in niches]
                    rebuild = not self._niche_entries or old_structure != new_structure or projects != self._project_entries or history != self._history_entries
                    self._project_entries, self._history_entries, self._niche_entries = projects, history, niches
                    self._entries_ready = True
                    self._working_signature = self._current_working_signature()
                    self._update_working_count()
                    if rebuild and self._tree_mode != 'files':
                        self._root_node()
                        self._focus_tree(self.workspace_state['selection'])
                    else:
                        self._refresh_working_rows()
                        self._refresh_project_icons()
                except (OSError, ValueError, RuntimeError) as error:
                    self.search_status.setText('Could not load project navigation: ' + str(error)[:240])
                    self.search_status.show()
            else:
                self._refresh_working_rows()
            self.apply_workspace(self.host.get_workspace(self.workspace_id))
            mode = self.host.control()['mode']
            index = self.mode.findData(mode)
            if index >= 0:
                with QSignalBlocker(self.mode):
                    self.mode.setCurrentIndex(index)
            for name, (node, future) in list(self._file_loads.items()):
                if not future.done():
                    continue
                del self._file_loads[name]
                try:
                    rows = future.result()
                except (ValueError, OSError):
                    rows = []
                if self._tree_mode == 'files':
                    with QSignalBlocker(self.tree):
                        for child, directory in rows:
                            self._node(node, child, directory)
                        node.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.DontShowIndicatorWhenChildless)
            if self._search and self._search.done():
                future, self._search = self._search, None
                results = future.result()
                pending, self._pending_search = self._pending_search, None
                if pending and pending != self._search_query:
                    self._search_query = pending
                    entries = self._history_entries if self._tree_mode == 'history' else self._project_entries
                    self._search = self._pool.submit(lambda: [(name, directory) for name, directory
                                                               in entries if pending in name.casefold()][:100])
                else:
                    with QSignalBlocker(self.tree):
                        self.tree.clear()
                        for name, directory in results:
                            self._node(self.tree, name, directory, full=True)
                    self._search_view = True
                    if not results:
                        message = 'No matches found in the folders searched.'
                    elif len(results) == 100:
                        message = 'Showing the first 100 matches. Refine your search for more.'
                    else:
                        message = f'{len(results)} matching files and folders.'
                    self.search_status.setText(message)
                    self.search_status.show()
                    self._focus_tree(self.workspace_state['selection'])
        except (ValueError, OSError, RuntimeError) as error:
            self.notice.setText(str(error)[:400])
            self.notice.show()

    def apply_workspace(self, workspace):
        previous = self.workspace_state
        if previous and workspace['revision'] < previous['revision']:
            return
        self.workspace_state = workspace
        if previous and previous['selection'] == workspace['selection']:
            self._refresh_preview_if_changed(workspace['selection'])
            # Refresh the visible ancestry as other chats create or remove files.
            # Re-selecting also restores the highlight if a refreshed parent
            # rebuilt its children.
            self._focus_tree(workspace['selection'], reveal=False)
            return
        selection = workspace['selection']
        self.path_label.setText(str(self.repo / selection))
        self._focus_tree(selection)
        self._preview(selection)

    def _refresh_working_rows(self):
        """Refresh focus states from canonical metadata across connected windows."""
        if self._search_view or self._tree_mode not in {'projects', 'niches'}:
            return
        current = {row[4]: row for row in self._niche_entries}
        with QSignalBlocker(self.tree):
            def visit(parent):
                for index in range(parent.childCount()):
                    item = parent.child(index)
                    ident = item.data(0, NICHE_ID_ROLE)
                    if ident in current:
                        row = current[ident]
                        value = row[5]
                        item.setData(0, WORKING_ROLE, value)
                        item.setIcon(0, self._working_folder_icon if value else self._folder_icon)
                        item.setCheckState(0, Qt.CheckState.Checked if value else Qt.CheckState.Unchecked)
                        status = 'Working' if value else 'Not Working'
                        if row[6] is None:
                            item.setText(0, f'{row[1]} · {self._category_working_count(row[0])} working · {status}')
                        else:
                            item.setText(0, f'{row[1]} · {row[2]} {"project" if row[2] == 1 else "projects"} · {status}')
                    visit(item)
            if self.tree.topLevelItemCount():
                visit(self.tree.topLevelItem(0))

    def _current_working_signature(self):
        rows = []
        base = self.repo / 'business_portfolio/niches'
        for path in (*base.rglob('NICHE.json'), *base.rglob('projects/*.md')):
            try:
                stat = path.stat()
                rows.append((str(path), stat.st_mtime_ns, stat.st_size))
            except OSError:
                continue
        return tuple(sorted(rows))

    def _category_working_count(self, category_path):
        descendants = [row for row in self._niche_entries
                       if row[0].startswith(category_path + '/') and row[5]]
        leaves = [row for row in descendants if not any(
            other[0].startswith(row[0] + '/') for other in descendants)]
        return len(leaves)

    def _update_working_count(self):
        working = [row for row in self._niche_entries if row[5]]
        leaf_count = sum(not any(other[0].startswith(row[0] + '/') for other in self._niche_entries)
                         for row in working)
        self.working_count.setText(f'{leaf_count} working {"niche" if leaf_count == 1 else "niches"}')

    def _load_research_budget(self):
        try:
            value = self._budget_setting.read_text(encoding='utf-8').strip()
            return value if re.fullmatch(r'\d+(?:\.\d{1,2})?', value) else '100'
        except OSError:
            return '100'

    def _save_research_budget(self, value):
        value = value.strip()
        if not re.fullmatch(r'\d+(?:\.\d{1,2})?', value):
            return
        try:
            self._budget_setting.write_text(value, encoding='utf-8')
        except OSError:
            self.notice.setText('Could not save the research ceiling setting.')
            self.notice.show()

    def _selected_niche(self, selection):
        prefix = 'business_portfolio/niches/'
        if not selection.startswith(prefix):
            return None
        candidate = PurePosixPath(selection)
        if candidate.name == 'projects' or candidate.parent.name == 'projects':
            return None
        metadata = self.repo / selection / 'NICHE.json'
        try:
            meta = json.loads(metadata.read_text(encoding='utf-8'))
            return meta.get('title')
        except (OSError, ValueError, TypeError):
            return None

    def _copy_megaprompt(self, option):
        niche = None
        if option == 'research':
            niche = self._selected_niche(self.workspace_state['selection'])
            if not niche:
                self.notice.setText('Select an active niche folder to copy the research prompt.')
                self.notice.show()
                return
            filename = 'BUSINESS_OPPORTUNITY_RESEARCH_MEGAPROMPT.md'
        elif option == 'idea':
            filename = 'BUSINESS_IDEA_TO_PROJECT_MEGAPROMPT.md'
        else:
            return
        source = self.repo / filename
        try:
            with source.open('r', encoding='utf-8', newline='') as stream:
                prompt = stream.read()
        except (OSError, UnicodeError):
            self.notice.setText(f'Could not read {filename}.')
            self.notice.show()
            return
        budget = self.research_budget.text().strip()
        if not re.fullmatch(r'\d+(?:\.\d{1,2})?', budget):
            self.notice.setText('Enter a valid non-negative CAD ceiling, such as 50 or 50.00.')
            self.notice.show()
            return
        budget_pattern = r'(?m)^(\*\*BUDGET_CEILING_CAD:\*\*[ \t]*)([^\r\n]*?\S)([ \t]*)(?=\r?$)'
        niche_pattern = r'(?m)^(\*\*BUSINESS_NICHE:\*\*[ \t]*)([^\r\n]*?\S)([ \t]*)(?=\r?$)'
        idea_pattern = r'(?m)^\*\*PROJECT_IDEA:\*\*[ \t]*\r?\n\r?\n```text\r?\n[\s\S]*?\r?\n```[ \t]*\r?$'
        if (len(re.findall(budget_pattern, prompt)) != 1 or
                (option == 'research' and len(re.findall(niche_pattern, prompt)) != 1) or
                (option == 'idea' and len(re.findall(idea_pattern, prompt)) != 1)):
            self.notice.setText(f'{filename} has missing or invalid setting markers; nothing copied.')
            self.notice.show()
            return
        prompt = re.sub(budget_pattern, lambda match: match.group(1) + budget + match.group(3), prompt, count=1)
        if niche is not None:
            prompt = re.sub(niche_pattern, lambda match: match.group(1) + niche + match.group(3), prompt, count=1)
        QApplication.clipboard().setText(prompt)
        self.notice.setText(f'{"Research prompt for " + niche if niche else "Business idea prompt"} copied (CAD {budget} ceiling).')
        self.notice.show()

    def _refresh_preview_if_changed(self, selection):
        try:
            path = context_path(self.repo, selection)
            stat = path.stat()
            signature = (stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size, path.is_dir())
            if path.is_dir() and self._preview_readme:
                readme = context_path(self.repo, self._preview_readme)
                info = readme.stat()
                signature += (info.st_mtime_ns, info.st_ctime_ns, info.st_size)
        except (ValueError, OSError):
            signature = None
        if signature != self._preview_signature:
            self._preview(selection)

    def _preview(self, selection):
        self.image.clear()
        self.image_scroll.hide()
        self.project_tabs.hide()
        self.project_actions.hide()
        self.preview.show()
        self._preview_readme = None
        try:
            path = context_path(self.repo, selection)
            stat = path.stat()
            self._preview_signature = (stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size, path.is_dir())
            if path.is_dir():
                entries = children(self.repo, path)
                names = [PurePosixPath(name).name + ('/' if directory else '')
                         for name, directory in entries[:50]]
                contents = '\n'.join(names) if names else 'This folder has no visible items.'
                if path.is_relative_to(self.repo / 'business_portfolio/niches') and path.name != 'projects':
                    direct_projects = path / 'projects'
                    if not direct_projects.is_dir():
                        contents = ('No projects directly in this niche; browse its subniches.\n\n'
                            if any(directory for _, directory in entries) else 'No active projects.\n\n') + contents
                if len(entries) > 50:
                    contents += f'\n… and {len(entries) - 50} more items.'
                summary = ''
                for name, directory in entries:
                    if not directory and PurePosixPath(name).name.casefold() in {'readme', 'readme.md', 'readme.txt'}:
                        try:
                            readme = context_path(self.repo, name)
                            with readme.open('rb') as file:
                                data = file.read(4001)
                        except (ValueError, OSError):
                            continue
                        if b'\x00' not in data:
                            info = readme.stat()
                            self._preview_readme = name
                            self._preview_signature += (info.st_mtime_ns, info.st_ctime_ns, info.st_size)
                            summary = '\n\n' + data[:4000].decode('utf-8', errors='replace').strip()
                            if len(data) > 4000:
                                summary += '\n…'
                        break
                self.preview.setPlainText(f'{selection}{summary}\n\n{contents}')
                return
            suffix = path.suffix.lower()
            size = path.stat().st_size
            if suffix in IMAGE_FORMATS and size <= 12_000_000:
                reader = QImageReader(str(path), IMAGE_FORMATS[suffix])
                reader.setAutoDetectImageFormat(False)
                dimensions = reader.size()
                if dimensions.isValid() and dimensions.width() * dimensions.height() <= 12_000_000:
                    image = reader.read()
                    if not image.isNull():
                        self.image.setPixmap(QPixmap.fromImage(image))
                        self.image.adjustSize()
                        self.preview.hide()
                        self.image_scroll.show()
                        return
            if suffix in TEXT_SUFFIXES or path.name in {'README', 'LICENSE', 'Makefile'}:
                with path.open('rb') as file:
                    data = file.read(MAX_PREVIEW + 1)
                if b'\x00' not in data:
                    self.preview.setPlainText(data[:MAX_PREVIEW].decode('utf-8', errors='replace') +
                                              ('\n\nPreview shortened.' if len(data) > MAX_PREVIEW else ''))
                    if (suffix == '.md' and path.parent.name == 'projects' and
                            (path.is_relative_to(self.repo/'business_portfolio/niches') or
                             path.is_relative_to(self.repo/'business_portfolio/archive/2026-11-15-legacy/niches') or
                             path.is_relative_to(self.repo/'business_portfolio/archive/2026-11-15-taxonomy-view-v1/niches'))):
                        self._project_detail(data[:MAX_PREVIEW].decode('utf-8', errors='replace'), selection,
                                             archived='/archive/' in '/'+selection)
                    return
            self.preview.setPlainText(f'{path.name}\n{size:,} bytes\nPreview unavailable for this file.')
        except (ValueError, OSError):
            self._preview_signature = None
            self.preview.setPlainText('The selected path is unavailable.')

    def _project_detail(self, raw, selection, *, archived):
        from business_portfolio.tools.build_browser import parse_project
        try:
            meta, body = parse_project(raw, selection)
        except ValueError:
            return
        purpose = re.search(r'^\*\*Purpose:\*\*\s*(.+)$', body, re.M)
        overview = [meta['title'], '', 'Preserved history' if archived else 'Current project',
                    'Niche: ' + meta['niche_path'].replace('-', ' '),
                    'Status: ' + meta['work_state'].replace('_', ' '),
                    'Evidence: ' + meta['commercial_validation'].replace('_', ' '),
                    'Supported platforms: ' + (', '.join(meta.get('platforms_supported', [])) or 'None verified'),
                    'Proposed platforms: ' + (', '.join(meta.get('platforms_proposed', [])) or 'Not specified'),
                    '', purpose.group(1) if purpose else 'See the complete record for scope and evidence.',
                    '', 'Next step:', meta['next_action']]
        if archived:
            overview += ['', 'Review the latest private checkpoint and external state before restoring.']
        self.project_overview.setPlainText('\n'.join(overview))
        self.project_files.setPlainText('Saved project record:\n' + selection +
            '\n\nThis record is planning documentation. Protected customer packages are not shown here.')
        results = meta.get('public_results', [])
        self.project_results.setPlainText('\n'.join(r['label'] + ' — ' + r['path'] for r in results)
            if results else 'No verified public results are declared for this project.')
        done = re.findall(r'^\s*- \[[xX]\] (.+)$', body, re.M)
        remaining = re.findall(r'^\s*- \[ \] (.+)$', body, re.M)
        self.project_tasks.setPlainText('Completed\n' + ('\n'.join('• ' + item for item in done) if done else
            'No completed tasks recorded.') + '\n\nRemaining\n' +
            ('\n'.join('• ' + item for item in remaining) if remaining else
             'No remaining checklist recorded; see the next step.') +
            '\n\nProgress percentage: not measured.')
        self.project_record.setPlainText(raw)
        self.project_tabs.setCurrentIndex(0)
        self.project_tabs.show()
        self.project_actions.setVisible(not archived)
        completed = meta.get('work_state') == 'completed'
        self.complete_project_button.setProperty('is_complete', completed)
        self.complete_project_button.setText('Mark Not Complete' if completed else 'Mark Complete')
        self.complete_project_button.setEnabled(True)
        self.preview.hide()

    def closeEvent(self, event):
        self._sync.stop()
        self._pool.shutdown(wait=False, cancel_futures=True)
        self.on_close(self.workspace_id)
        event.accept()
