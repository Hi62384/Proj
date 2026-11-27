"""Independent views of the shared Portfolio Manager controller."""
from concurrent.futures import ThreadPoolExecutor
import os
import json
import html
import hashlib
from pathlib import Path, PurePosixPath
import re
import time

from PySide6.QtCore import QEvent, QRect, QSignalBlocker, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QIcon, QImageReader, QPainter, QPixmap, QTextOption
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout, QInputDialog, QLabel, QLineEdit, QMainWindow,
                               QMenu, QMessageBox, QPlainTextEdit, QPushButton, QScrollArea, QSplitter, QTextBrowser,
                               QStyle, QTabWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

from .workspace import context_path


ROLE = int(Qt.ItemDataRole.UserRole)
PHASE_LABELS = {
    'working_phase_1': 'Phase 1 · Product research',
    'working_phase_2': 'Phase 2 · Release platform research',
    'working_phase_3': 'Phase 3 · Marketing research',
    'working_phase_4': 'Phase 4 · Build & test',
    'working_phase_5': 'Phase 5 · Release',
    'working_phase_6': 'Phase 6 · Marketing',
    'complete': 'Complete · Verified',
}
PROMPTS = {
    'research': ('working_phase_1', 'PHASE_1_RESEARCH_MEGAPROMPT.md', 'Product research'),
    'idea': ('working_phase_1', 'PHASE_1_IDEA_MEGAPROMPT.md', 'Research my idea'),
    'recheck': ('working_phase_1', 'PHASE_1_RECHECK_REPLACE_MEGAPROMPT.md', 'Product research recheck'),
    'phase2': ('working_phase_2', 'PHASE_2_RELEASE_RESEARCH_MEGAPROMPT.md', 'Release platform research'),
    'phase2_recheck': ('working_phase_2', 'PHASE_2_RECHECK_MEGAPROMPT.md', 'Release platform recheck'),
    'phase3': ('working_phase_3', 'PHASE_3_MARKETING_RESEARCH_MEGAPROMPT.md', 'Marketing research'),
    'phase3_recheck': ('working_phase_3', 'PHASE_3_RECHECK_MEGAPROMPT.md', 'Marketing research recheck'),
    'phase4': ('working_phase_4', 'PHASE_4_BUILD_MEGAPROMPT.md', 'Build'),
    'phase5': ('working_phase_5', 'PHASE_5_RELEASE_MEGAPROMPT.md', 'Release'),
    'phase6': ('working_phase_6', 'PHASE_6_MARKETING_MEGAPROMPT.md', 'Marketing'),
}


def configure_project_day_limit(prompt, days):
    """Update the template's shared project window without changing a record snapshot."""
    replacements = (
        ('2 days to 3 weeks (2–21 calendar days total)', f'up to {days} calendar days total'),
        ('2 days to 3 weeks total', f'up to {days} calendar days total'),
        ('2–21-day', f'{days}-day'),
        ('2–21 days', f'up to {days} days'),
        ('another three weeks for each phase', 'a new full window for each phase'),
        ('{ "minimum": 2, "maximum": 21 }',
         '{ "minimum": ' + str(min(2, days)) + ', "maximum": ' + str(days) + ' }'),
    )
    for old, new in replacements:
        prompt = prompt.replace(old, new)
    return prompt

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


def folder_preview(repo, selection):
    """Read a folder preview off the UI thread."""
    path = context_path(repo, selection)
    entries = children(repo, path)
    names = [PurePosixPath(name).name + ('/' if directory else '') for name, directory in entries[:50]]
    contents = '\n'.join(names) if names else 'This folder has no visible items.'
    if (path / 'NICHE.json').is_file():
        contents = 'Create a project here with New project, or add a child with New niche folder.\n\n' + contents
    if len(entries) > 50:
        contents += f'\n… and {len(entries) - 50} more items.'
    summary, readme_name, readme_signature = '', None, ()
    for name, directory in entries:
        if not directory and PurePosixPath(name).name.casefold() in {'readme', 'readme.md', 'readme.txt'}:
            try:
                readme = context_path(repo, name)
                with readme.open('rb') as file:
                    data = file.read(4001)
                if b'\x00' not in data:
                    info = readme.stat()
                    readme_name = name
                    readme_signature = (info.st_mtime_ns, info.st_ctime_ns, info.st_size)
                    summary = '\n\n' + data[:4000].decode('utf-8', errors='replace').strip()
                    if len(data) > 4000:
                        summary += '\n…'
            except (ValueError, OSError):
                pass
            break
    return f'{selection}{summary}\n\n{contents}', readme_name, readme_signature


def search_paths(repo, query):
    return [(name, directory) for name, directory in project_entries(repo)
            if query in name.casefold()][:100]


def project_record_leaf(name):
    item = PurePosixPath(name)
    return (item.name == 'project.md' or
            (item.parent.name == 'projects' and item.suffix.lower() == '.md'))


def tree_parent(name):
    item = PurePosixPath(name)
    if item.name == 'project.md':
        parent = item.parent.parent
        return (parent.parent if parent.name == 'projects' else parent).as_posix()
    if project_record_leaf(name):
        return item.parent.parent.as_posix()
    return item.parent.as_posix()


def navigation_files(repo):
    """Find niche metadata and records without traversing any project work tree."""
    base = repo / 'business_portfolio/niches'
    metadata, records = [], []
    if not base.is_dir():
        return metadata, records
    for folder, dirs, files in os.walk(base, followlinks=False):
        here = Path(folder)
        dirs[:] = [name for name in dirs if not name.startswith('.') and
                   name not in {'private', '__pycache__'} and not (here / name).is_symlink()]
        if here.name == 'projects':
            records.extend(here / name for name in files if name.lower().endswith('.md'))
            records.extend(here / name / 'project.md' for name in dirs
                           if (here / name / 'project.md').is_file())
            dirs[:] = []
        elif 'project.md' in files and (here.parent / 'NICHE.json').is_file():
            records.append(here / 'project.md')
            dirs[:] = []
        elif 'NICHE.json' in files:
            metadata.append(here / 'NICHE.json')
    return metadata, records


def project_entries(repo, niches=None):
    """Keep project.md visible as the leaf, hiding its enclosing project folder."""
    base = repo / 'business_portfolio' / 'niches'
    visible = set()
    niches = niche_entries(repo) if niches is None else niches
    for name, *_ in niches:
        visible.add((name, True))
        for parent in PurePosixPath(name).parents:
            if parent.as_posix() != '.':
                visible.add((parent.as_posix(), True))
    if not base.is_dir():
        return sorted(visible)
    _, records = navigation_files(repo)
    for item in records:
        try:
            name = context_path(repo, item).relative_to(repo).as_posix()
        except (ValueError, OSError):
            continue
        visible.add((name, False))
        parent = PurePosixPath(tree_parent(name))
        for ancestor in (parent, *parent.parents):
            if ancestor.as_posix() != '.':
                visible.add((ancestor.as_posix(), True))
    priorities = {row[0]: row[3] for row in niches}
    return sorted(visible, key=lambda item: (item[0].count('/'),
                                            priorities.get(item[0], 999), item[0].casefold()))


def completed_entries(repo):
    """The completed-project navigation is independent of source project files."""
    from .project_lifecycle import read_completions
    base = 'business_portfolio/completed_projects'
    visible = {(base, True), ('business_portfolio', True)}
    for record in read_completions(repo):
        visible.add((base + '/' + record['id'] + '.json', False))
    return sorted(visible, key=lambda item: (item[0].count('/'), item[0].casefold()))


def navigation_signature(repo):
    """Detect imports and phase changes without scanning project work trees."""
    rows = []
    metadata, records = navigation_files(repo)
    for target in [repo / 'business_portfolio/niches', *metadata, *records]:
        try:
            info = target.stat()
            rows.append((str(target), info.st_mtime_ns, info.st_size))
        except OSError:
            pass
    completed = repo / 'business_portfolio/completed_projects'
    if completed.is_dir():
        for target in (completed, *completed.glob('*.json')):
            try:
                info = target.stat()
                rows.append((str(target), info.st_mtime_ns, info.st_size))
            except OSError:
                pass
    return tuple(sorted(rows))

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
    metadata_paths, records = navigation_files(repo)
    project_folders = [repo / tree_parent(record.relative_to(repo).as_posix())
                       for record in records if not record.is_symlink()]
    for metadata in metadata_paths:
        folder = metadata.parent
        try:
            relative = context_path(repo, folder).relative_to(repo).as_posix()
            meta = json.loads(metadata.read_text(encoding='utf-8'))
            if meta.get('path') != folder.relative_to(base).as_posix():
                continue
            count = sum(parent.is_relative_to(folder) for parent in project_folders)
            rows.append((relative, meta['title'], count, meta.get('priority', 999),
                         meta['id'], meta.get('working', False), meta.get('parent')))
        except (ValueError, OSError, KeyError, TypeError):
            continue
    return sorted(rows, key=lambda row: (row[0].count('/'), row[3], row[1].casefold()))


class WorkspaceWindow(QMainWindow):
    def __init__(self, host, workspace, *, on_emergency, on_stop_all, on_access, on_close, on_resume=None):
        super().__init__()
        self.host = host
        self.repo = Path(host.repo).resolve()
        self.workspace_id = workspace['id']
        self.workspace_state = None
        self._closing = False
        self.on_close = on_close
        self._search = None
        self._search_query = None
        self._pending_search = None
        self._search_view = False
        self._preview_signature = None
        self._preview_readme = None
        self._preview_future = None
        self._pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix='workspace-files')
        # Browser/index generation can take seconds on Windows. Keep writes off
        # the Qt event loop and separate from navigation/preview workers.
        self._creation_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='workspace-create')
        self._project_creation = None
        self._project_deletion = None
        self._project_entries = []
        self._history_entries = []
        self._completed_entries = []
        self._niche_entries = []
        self._working_signature = None
        self._signature_future = None
        self._next_signature_check = 0.0
        self._research_prompt = None
        self._budget_setting = self.repo / 'business_portfolio' / '.research_prompt_budget'
        self._days_setting = self.repo / 'business_portfolio' / '.research_prompt_days'
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
        self._phase_icons = {}
        for phase, symbol, color in (('working_phase_1', '1', '#526e7a'),
                                      ('working_phase_2', '2', '#3377ad'),
                                      ('working_phase_3', '3', '#ad722a'),
                                      ('working_phase_4', '4', '#8753a7'),
                                      ('working_phase_5', '5', '#256c75'),
                                      ('working_phase_6', '6', '#b44e7a'),
                                      ('complete', '✓', '#20865a')):
            pixmap = self._file_icon.pixmap(32, 32)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QColor('#ffffff'))
            painter.setBrush(QColor(color))
            painter.drawEllipse(17, 1, 14, 14)
            font = painter.font()
            font.setBold(True)
            font.setPixelSize(10)
            painter.setFont(font)
            painter.drawText(QRect(17, 1, 14, 14), Qt.AlignmentFlag.AlignCenter, symbol)
            painter.end()
            self._phase_icons[phase] = QIcon(pixmap)
        self.setWindowTitle('Portfolio Manager | Chat ' + self.workspace_id)
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
        self.chat_label = QLabel('Chat ' + self.workspace_id)
        self.chat_label.setTextFormat(Qt.TextFormat.PlainText)
        self.chat_label.setAccessibleName('Current project or chat')
        header.addWidget(self.chat_label)
        self.mode = QComboBox()
        self.mode.setAccessibleName('Global availability')
        self.mode.addItem('AI Only (AFK)', 'afk')
        self.mode.addItem('Human Available', 'human')
        self.mode.activated.connect(self._set_mode)
        header.addWidget(self.mode)
        self.resume_after_stop = QPushButton('Resume after stop')
        self.resume_after_stop.setAccessibleName('Resume after stop')
        self.resume_after_stop.setToolTip('Clear the Computer Bridge stopped state without starting background workers.')
        self.resume_after_stop.setEnabled(on_resume is not None)
        if on_resume is not None:
            self.resume_after_stop.clicked.connect(on_resume)
        header.addWidget(self.resume_after_stop)
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
        panels = (self.project_overview, self.project_files, self.project_results,
                  self.project_tasks, self.project_record)
        self._drop_targets = (frame, self.tree, self.tree.viewport(), self.preview,
                              self.preview.viewport(), self.project_tabs, self.image_scroll,
                              *panels, *(panel.viewport() for panel in panels))
        self.setAcceptDrops(True)
        for widget in self._drop_targets:
            widget.setAcceptDrops(True)
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
        self.view_mode.addItem('Completed Projects', 'completed')
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
        self.tree.setHeaderLabels(['Projects'])
        self.tree.itemSelectionChanged.connect(self._select_file)
        self.tree.itemExpanded.connect(self._expand)
        self.tree.itemChanged.connect(self._niche_working_changed)
        layout.addWidget(self.tree)
        splitter.addWidget(navigator)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setAccessibleName('Selected file or folder preview')
        self.completed_detail = QTextBrowser()
        self.completed_detail.setAccessibleName('Completed project details and links')
        self.completed_detail.setOpenExternalLinks(True)
        self.completed_detail.hide()
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
        self.niche_tools = QWidget()
        niche_layout = QHBoxLayout(self.niche_tools)
        niche_layout.setContentsMargins(0, 0, 0, 0)
        self.new_project = QPushButton('New project')
        self.new_project.clicked.connect(self._new_project)
        self.new_niche = QPushButton('New niche folder')
        self.new_niche.clicked.connect(self._new_niche)
        self.delete_niche = QPushButton('Delete niche')
        self.delete_niche.clicked.connect(self._delete_niche)
        for button in (self.new_project, self.new_niche, self.delete_niche):
            niche_layout.addWidget(button)
        details.addWidget(self.niche_tools)
        self.research_tools = QWidget()
        research_layout = QFormLayout(self.research_tools)
        self.research_budget = QLineEdit(self._load_research_budget())
        self.research_budget.setAccessibleName('Budget ceiling in CAD')
        self.research_budget.setPlaceholderText('100')
        self.research_budget.textChanged.connect(self._save_research_budget)
        self.copy_prompt = QPushButton('Copy research prompt')
        self.copy_prompt.setAccessibleName('Copy research prompt')
        self.prompt_menu = QMenu(self.copy_prompt)
        self.copy_prompt.setMenu(self.prompt_menu)
        self._prompt_menu_state = None
        self.budget_label = QLabel('Budget ceiling (CAD)')
        research_layout.addRow(self.budget_label, self.research_budget)
        self.project_days = QLineEdit(self._load_project_days())
        self.project_days.setAccessibleName('Project day limit')
        self.project_days.setPlaceholderText('21')
        self.project_days.textChanged.connect(self._save_project_days)
        self.project_days_label = QLabel('Project day limit')
        research_layout.addRow(self.project_days_label, self.project_days)
        research_layout.addRow(self.copy_prompt)
        self.paste_project = QPushButton('Paste project text')
        self.paste_project.setToolTip('Replace this research record with copied text. The phase stays unchanged.')
        self.paste_project.clicked.connect(self._paste_project)
        research_layout.addRow(self.paste_project)
        details.addWidget(self.research_tools)
        self.phase_controls = QWidget()
        phase_layout = QHBoxLayout(self.phase_controls)
        phase_layout.setContentsMargins(0, 0, 0, 0)
        phase_layout.addWidget(QLabel('Project phase'))
        self.phase_selector = QComboBox()
        self.phase_selector.setAccessibleName('Project phase')
        for phase, label in PHASE_LABELS.items():
            self.phase_selector.addItem(label, phase)
        self.phase_selector.activated.connect(self._phase_choice_changed)
        phase_layout.addWidget(self.phase_selector, 1)
        self.phase_apply = QPushButton('Advance phase')
        self.phase_apply.clicked.connect(self._apply_project_phase)
        phase_layout.addWidget(self.phase_apply)
        self.delete_project = QPushButton('Delete project')
        self.delete_project.setAccessibleName('Delete project')
        self.delete_project.setToolTip('Recoverably delete only this project and its work/ folder.')
        self.delete_project.clicked.connect(self._delete_project)
        phase_layout.addWidget(self.delete_project)
        self.phase_controls.hide()
        self._phase_project = None
        details.addWidget(self.phase_controls)
        details.addWidget(self.project_tabs)
        details.addWidget(self.completed_detail)
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
        signature = navigation_signature(repo)
        niches = niche_entries(repo)
        return project_entries(repo, niches), history_entries(repo), completed_entries(repo), niches, signature

    def _set_mode(self):
        try:
            self.host.coordinator.set_mode(self.mode.currentData())
            self.notice.hide()
        except (ValueError, OSError, RuntimeError) as error:
            self.notice.setText(str(error)[:400])
            self.notice.show()
        self.sync()



    def _node(self, parent, name, directory, *, full=False):
        label = name if full else PurePosixPath(name).name
        icon = self._folder_icon if directory else self._file_icon
        tooltip = ''
        if not directory and self._tree_mode == 'projects' and project_record_leaf(name):
            try:
                from business_portfolio.tools.build_browser import parse_project
                from .project_lifecycle import project_phase
                record = context_path(self.repo, name)
                meta, _ = parse_project(record.read_text(encoding='utf-8'), name)
                label = meta.get('id', record.stem.upper()) + ' · ' + meta.get('title', record.stem)
                stage = project_phase(meta)
                icon = self._phase_icons[stage]
                tooltip = PHASE_LABELS[stage]
            except (OSError, ValueError, KeyError, TypeError):
                label = PurePosixPath(name).stem.replace('-', ' ').title()
        if not directory and self._tree_mode == 'completed' and '/completed_projects/' in name:
            try:
                record = json.loads(context_path(self.repo, name).read_text(encoding='utf-8'))
                label = record['id'] + ' · ' + record['title']
                icon = self._phase_icons['complete']
                tooltip = 'Durable completion receipt'
            except (OSError, ValueError, KeyError, TypeError):
                pass
        item = QTreeWidgetItem(parent, [label])
        item.setIcon(0, icon)
        if tooltip:
            item.setToolTip(0, tooltip)
        item.setData(0, ROLE, name)
        item.setData(0, ROLE + 1, directory)
        if directory:
            item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
        return item

    def _root_node(self):
        self._search_view = False
        self._file_loads.clear()  # Tree items are about to be destroyed.
        self.tree.setUpdatesEnabled(False)
        try:
            self._populate_root_node()
        finally:
            self.tree.setUpdatesEnabled(True)

    def _populate_root_node(self):
        with QSignalBlocker(self.tree):
            self.tree.clear()
            root = self._node(self.tree, '.', True, full=True)
            root.setText(0, 'Completed Projects' if self._tree_mode == 'completed' else self.repo.name)
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
            entries = (self._history_entries if self._tree_mode == 'history' else
                       self._completed_entries if self._tree_mode == 'completed' else self._project_entries)
            for name, directory in entries:
                parent = tree_parent(name) if self._tree_mode == 'projects' else PurePosixPath(name).parent.as_posix()
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
        self._refresh_prompt_menu()
        if self._tree_mode != 'projects':
            self.phase_controls.hide()
        if self._tree_mode == 'completed' and not any(not entry[1] for entry in self._completed_entries):
            self.preview.setPlainText('No completed projects yet. Verified Phase 6 completions will appear here.')
            self.preview.show()
            self.project_tabs.hide()
            self.completed_detail.hide()

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
        if self._closing:
            return False
        if event.type() in (QEvent.Type.DragEnter, QEvent.Type.DragMove, QEvent.Type.Drop):
            return self._project_drop_event(event, watched)
        return super().eventFilter(watched, event)

    def dragEnterEvent(self, event):
        self._project_drop_event(event)

    def dragMoveEvent(self, event):
        self._project_drop_event(event)

    def dropEvent(self, event):
        self._project_drop_event(event)

    def _drop_niche_from_item(self, item):
        """Choose the hovered niche, not a stale selection from another window."""
        while item is not None:
            if item.data(0, NICHE_ID_ROLE):
                return item.data(0, ROLE)
            item = item.parent()
        return None

    def _project_drop_event(self, event, watched=None):
        urls = event.mimeData().urls()
        if not urls or not all(url.isLocalFile() and url.toLocalFile().lower().endswith('.md') for url in urls):
            event.ignore()
            return False
        if event.type() != QEvent.Type.Drop:
            event.acceptProposedAction()
            return True
        from .project_import import import_projects
        try:
            destination = self.workspace_state['selection']
            if watched in (self.tree, self.tree.viewport()) and self._tree_mode in {'projects', 'niches'}:
                location = event.position().toPoint()
                if watched is self.tree:
                    location = self.tree.viewport().mapFrom(self.tree, location)
                item = self.tree.itemAt(location)
                hovered = item.data(0, ROLE) if item is not None else None
                if hovered and project_record_leaf(hovered):
                    if hovered != self.workspace_state['selection']:
                        raise ValueError('Select that exact project before replacing its file.')
                    destination = hovered
                else:
                    destination = self._drop_niche_from_item(item)
            if not destination:
                raise ValueError('Drop onto a selected project or active niche folder.')
            if project_record_leaf(destination) and self._tree_mode == 'projects':
                if destination != self.workspace_state['selection']:
                    raise ValueError('Select the exact project before replacing its file.')
                if len(urls) != 1:
                    raise ValueError('Drop exactly one Markdown update onto the selected project.')
                from .project_update import replace_project_from_file
                outcome = replace_project_from_file(self.repo, destination, urls[0].toLocalFile())
                self.notice.setText('Project updated: ' + outcome['id'] + '. Phase: ' + outcome['project_phase']
                                    + '. Previous version backed up locally.')
                self._preview(destination)
                self._refresh_project_phase_rows()
            else:
                ids = import_projects(self.repo, destination, [url.toLocalFile() for url in urls])
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
            if self._tree_mode == 'projects' and project_record_leaf(selection):
                niche = PurePosixPath(tree_parent(selection))
                ancestry = (*reversed(niche.parents), niche, PurePosixPath(selection))
            else:
                ancestry = (*reversed(PurePosixPath(selection).parents), PurePosixPath(selection))
            for parent in ancestry:
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

    def reveal_selected_project(self):
        """When opening a project workspace, show its actual tree selection."""
        selection = self.workspace_state.get('selection') if self.workspace_state else None
        if not self._current_project(selection):
            return
        if self._tree_mode != 'projects' or self._search_view or self._search is not None:
            self.view_mode.setCurrentIndex(self.view_mode.findData('projects'))
            self._change_view()
            self._preview(selection)
        self._focus_tree(selection)

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
            entries = (self._history_entries if self._tree_mode == 'history' else
                       self._completed_entries if self._tree_mode == 'completed' else self._project_entries)
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

    def _finish_project_creation(self):
        """Collect completed project creation on the GUI thread only."""
        pending = self._project_creation
        if pending is None or not pending[1].done():
            return
        original_selection, future = pending
        self._project_creation = None
        self.new_project.setEnabled(True)
        try:
            result = future.result()
        except (OSError, ValueError, RuntimeError) as error:
            self.notice.setText('Could not create project: ' + str(error)[:400])
            self.notice.show()
            return
        # User navigation during the build must be respected, not hijacked.
        if (self.workspace_state and
                self.workspace_state.get('selection') == original_selection and
                self._tree_mode == 'projects'):
            self._refresh_after_edit(result['path'])
        else:
            self._entry_future = self._pool.submit(self._load_navigation_entries, self.repo)
            self._entries_ready = False
        self.notice.setText('Empty project created in Phase 1. '
                            'Select it to copy a research prompt.')
        self.notice.show()

    def _finish_project_deletion(self):
        """Apply a completed deletion to this window without changing another selection."""
        pending = self._project_deletion
        if pending is None or not pending[2].done():
            return
        original_selection, parent_selection, future = pending
        self._project_deletion = None
        self.delete_project.setEnabled(True)
        try:
            result = future.result()
        except (OSError, ValueError, RuntimeError) as error:
            self.notice.setText('Could not delete project: ' + str(error)[:400])
            self.notice.show()
            return
        if self.workspace_state and self.workspace_state.get('selection') == original_selection:
            self._refresh_after_edit(parent_selection)
        else:
            self._entry_future = self._pool.submit(self._load_navigation_entries, self.repo)
            self._entries_ready = False
        self.notice.setText('Project deleted. Recoverable backup: ' + result['trash_path'])
        self.notice.show()

    def sync(self):
        try:
            self._finish_project_creation()
            self._finish_project_deletion()
            if self._entries_ready and self._tree_mode in {'projects', 'niches', 'completed'}:
                if self._signature_future is not None and self._signature_future.done():
                    future, self._signature_future = self._signature_future, None
                    signature = future.result()
                    if self._working_signature is not None and signature != self._working_signature:
                        self._entries_ready = False
                        self._entry_future = self._pool.submit(self._load_navigation_entries, self.repo)
                    self._working_signature = signature
                if self._signature_future is None and time.monotonic() >= self._next_signature_check:
                    self._signature_future = self._pool.submit(self._current_working_signature, self.repo)
                    self._next_signature_check = time.monotonic() + 0.4
            if not self._entries_ready and self._entry_future.done():
                try:
                    projects, history, completed, niches, signature = self._entry_future.result()
                    old_structure = [(r[0], r[1], r[2], r[3], r[4], r[6]) for r in self._niche_entries]
                    new_structure = [(r[0], r[1], r[2], r[3], r[4], r[6]) for r in niches]
                    rebuild = (not self._niche_entries or old_structure != new_structure or
                               projects != self._project_entries or history != self._history_entries or
                               completed != self._completed_entries)
                    self._project_entries, self._history_entries, self._completed_entries, self._niche_entries = projects, history, completed, niches
                    self._entries_ready = True
                    self._working_signature = signature
                    self._update_working_count()
                    if rebuild and self._tree_mode != 'files':
                        self._root_node()
                        self._focus_tree(self.workspace_state['selection'])
                    else:
                        self._refresh_working_rows()
                        self._refresh_project_phase_rows()
                except (OSError, ValueError, RuntimeError) as error:
                    self.search_status.setText('Could not load project navigation: ' + str(error)[:240])
                    self.search_status.show()
            self.apply_workspace(self.host.get_workspace(self.workspace_id))
            if self._preview_future and self._preview_future[1].done():
                selection, future = self._preview_future
                self._preview_future = None
                if self.workspace_state['selection'] == selection:
                    try:
                        contents, readme, signature = future.result()
                        self._preview_readme = readme
                        if self._preview_signature is not None:
                            self._preview_signature = self._preview_signature[:4] + signature
                        self.preview.setPlainText(contents)
                    except (OSError, ValueError, RuntimeError) as error:
                        self.preview.setPlainText('Could not read folder: ' + str(error)[:240])
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
                    entries = (self._history_entries if self._tree_mode == 'history' else
                               self._completed_entries if self._tree_mode == 'completed' else self._project_entries)
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
            pending = [self.tree.topLevelItem(index) for index in range(self.tree.topLevelItemCount())]
            while pending:
                item = pending.pop()
                pending.extend(item.child(index) for index in range(item.childCount()))
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

    def _refresh_project_phase_rows(self):
        """Update icons and names after another chat advances a project phase."""
        if self._tree_mode != 'projects':
            return
        from business_portfolio.tools.build_browser import parse_project
        from .project_lifecycle import project_phase
        with QSignalBlocker(self.tree):
            pending = [self.tree.topLevelItem(index) for index in range(self.tree.topLevelItemCount())]
            while pending:
                item = pending.pop()
                pending.extend(item.child(index) for index in range(item.childCount()))
                name = item.data(0, ROLE)
                directory = item.data(0, ROLE + 1)
                if not directory and isinstance(name, str) and project_record_leaf(name):
                    try:
                        path = context_path(self.repo, name)
                        meta, _ = parse_project(path.read_text(encoding='utf-8'), name)
                        stage = project_phase(meta)
                        item.setIcon(0, self._phase_icons[stage])
                        item.setText(0, meta.get('id', path.stem.upper()) + ' · ' + meta.get('title', path.stem))
                        item.setToolTip(0, PHASE_LABELS[stage])
                    except (OSError, ValueError, KeyError, TypeError):
                        pass
        if self.workspace_state:
            self._refresh_prompt_menu(self.workspace_state.get('selection'))

    @staticmethod
    def _current_working_signature(repo):
        # Background jobs must not keep a QWidget alive on their worker thread.
        return navigation_signature(repo)

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

    def _load_project_days(self):
        try:
            value = self._days_setting.read_text(encoding='utf-8').strip()
            return value if re.fullmatch(r'[1-9][0-9]{0,5}', value) else '21'
        except OSError:
            return '21'

    def _save_project_days(self, value):
        value = value.strip()
        if not re.fullmatch(r'[1-9][0-9]{0,5}', value):
            return
        try:
            self._days_setting.write_text(value, encoding='utf-8')
        except OSError:
            self.notice.setText('Could not save the project day limit.')
            self.notice.show()

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
        if not isinstance(selection, str) or not selection.startswith(prefix):
            return None
        candidate = PurePosixPath(selection)
        metadata = self.repo / candidate / 'NICHE.json'
        try:
            path = context_path(self.repo, metadata)
            meta = json.loads(path.read_text(encoding='utf-8'))
            return meta.get('title')
        except (OSError, ValueError, TypeError):
            return None

    def _current_project(self, selection=None):
        """Read the complete selected canonical project, never a truncated preview."""
        selection = selection if selection is not None else (
            self.workspace_state.get('selection') if self.workspace_state else '')
        if not isinstance(selection, str) or not project_record_leaf(selection):
            return None
        if not selection.startswith('business_portfolio/niches/'):
            return None
        try:
            from .project_lifecycle import record_path, project_phase
            from business_portfolio.tools.build_browser import parse_project
            path = record_path(self.repo, selection)
            raw = path.read_text(encoding='utf-8')
            meta, _ = parse_project(raw, selection)
            return path, raw, meta, project_phase(meta)
        except (ValueError, OSError, TypeError):
            return None

    def _refresh_prompt_menu(self, selection=None):
        """Offer research on a project, and creation tools on a niche."""
        selection = selection if selection is not None else (
            self.workspace_state.get('selection') if self.workspace_state else '')
        current = self._current_project(selection) if self._tree_mode == 'projects' else None
        niche = (self._selected_niche(selection)
                 if not current and self._tree_mode in {'projects', 'niches'} else None)
        key = ('project', selection, current[3]) if current else (
            ('niche', selection) if niche else ('none', selection))
        self.niche_tools.setVisible(bool(niche))
        active = current is not None and current[3] != 'complete'
        self.research_tools.setVisible(active)
        research = active and current[3] in {'working_phase_1', 'working_phase_2', 'working_phase_3'}
        self.research_budget.setVisible(bool(active))
        self.budget_label.setVisible(bool(active))
        self.paste_project.setVisible(bool(research))
        if key == self._prompt_menu_state:
            return
        self._prompt_menu_state = key
        self.prompt_menu.clear()
        if not active:
            return
        phase = current[3]
        choices = {
            'working_phase_1': ('Copy research prompt', (
                ('Research a product for this niche', 'research'),
                ('Research a project from my idea', 'idea'),
                ('Recheck product research', 'recheck'))),
            'working_phase_2': ('Copy release research prompt', (
                ('Research release platforms and compatible versions', 'phase2'),
                ('Recheck release platform research', 'phase2_recheck'))),
            'working_phase_3': ('Copy marketing research prompt', (
                ('Research the marketing plan', 'phase3'),
                ('Recheck marketing research', 'phase3_recheck'))),
            'working_phase_4': ('Copy build prompt', (('Build and test the project · /goal', 'phase4'),)),
            'working_phase_5': ('Copy release prompt', (('Release the project · /goal', 'phase5'),)),
            'working_phase_6': ('Copy marketing prompt', (('Carry out the marketing plan · /goal', 'phase6'),)),
        }
        label, options = choices[phase]
        self.copy_prompt.setText(label)
        self.copy_prompt.setAccessibleName(label)
        for title, option in options:
            self.prompt_menu.addAction(title, lambda checked=False, chosen=option: self._copy_megaprompt(chosen))

    def _ask_idea(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Research my idea')
        dialog.resize(560, 360)
        layout = QVBoxLayout(dialog)
        label = QLabel('Describe your product idea:')
        layout.addWidget(label)
        text = QPlainTextEdit()
        text.setAccessibleName('Product idea')
        text.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        text.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        label.setBuddy(text)
        layout.addWidget(text)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        accepted = dialog.exec() == QDialog.DialogCode.Accepted
        return text.toPlainText(), accepted

    def _copy_megaprompt(self, option):
        config = PROMPTS.get(option)
        current = self._current_project()
        if config is None:
            return
        phase, filename, description = config
        if current is None or current[3] != phase:
            self.notice.setText('Select a project in the matching phase before copying its prompt.')
            self.notice.show()
            return
        _, raw, meta, _ = current
        try:
            prompt = (self.repo / filename).read_text(encoding='utf-8')
            if not prompt.strip():
                raise ValueError('The prompt template is empty.')
            days_text = self.project_days.text().strip()
            if not re.fullmatch(r'[1-9][0-9]{0,5}', days_text):
                raise ValueError('Enter a project day limit of at least 1 whole day.')
            days = int(days_text)
            budget = self.research_budget.text().strip()
            if not re.fullmatch(r'\d+(?:\.\d{1,2})?', budget):
                raise ValueError('Enter a valid non-negative planning budget in CAD.')
            prompt = configure_project_day_limit(prompt, days)
            selection = self.workspace_state['selection']
            if phase in {'working_phase_4', 'working_phase_5', 'working_phase_6'}:
                if not prompt.startswith('/goal '):
                    raise ValueError('The execution prompt must start with /goal.')
                prompt += ('\n\nSelected canonical project: ' + selection +
                           '\nStable project ID: ' + meta['id'] +
                           '\nPlanning budget ceiling (CAD): ' + budget +
                           '. Apply any lower existing budget or spending authorization; this planning ceiling does not authorize spending.' +
                           '\nTotal project day limit across all six phases: ' + days_text + ' calendar days.' +
                           '\nWhen asked to open Portfolio Manager, pass this project ID or canonical project path to portfolio_open, together with this chat’s reconnect key.' +
                           '\nRead the complete current file and its sibling work/ before starting.\n')
            else:
                idea = ''
                if option == 'idea':
                    idea, accepted = self._ask_idea()
                    if not accepted:
                        return
                    if not idea.strip():
                        raise ValueError('Enter the idea to include in the research prompt.')
                from .project_update import snapshot_sha256
                niche = self._selected_niche('business_portfolio/niches/' + meta['niche_path']) or meta['niche_path']
                # The complete record is intentionally read from disk; previews may be shorter.
                fence = '`' * (max([len(t) for t in re.findall(r'`+', raw)] + [4]) + 1)
                prompt += ('\n\n## Selected project context\nBUSINESS_NICHE: ' + niche +
                           '\nBUDGET_CEILING_CAD: ' + budget +
                           '\nTOTAL_PROJECT_WINDOW: Up to ' + days_text + ' calendar days across all six phases.\n'
                           'Use this current owner-selected limit for delivery_window_days even if the record below contains an older limit; preserve historical facts.\n'
                           'CANONICAL_PROJECT_PATH: ' + selection +
                           '\nBASE_SHA256: ' + snapshot_sha256(raw) +
                           '\nKeep the ID, niche and current project_phase exactly as supplied. '
                           'Return complete copyable text for Paste project text; the owner advances phases.\n')
                if idea:
                    prompt += '\nPROJECT_IDEA:\n' + idea.strip() + '\n'
                prompt += ('\n## Complete current project record\n' + fence + 'markdown\n' +
                           raw + '\n' + fence + '\n')
            QApplication.clipboard().setText(prompt)
            self.notice.setText(description + ' prompt copied.')
        except (OSError, UnicodeError, ValueError, TypeError, KeyError) as error:
            self.notice.setText('Could not copy prompt: ' + str(error)[:400])
        self.notice.show()

    def _refresh_after_edit(self, selection):
        self._prompt_menu_state = None
        self._preview_signature = None
        self._entry_future = self._pool.submit(self._load_navigation_entries, self.repo)
        self._entries_ready = False
        if self.select(selection):
            self._preview(selection)
        else:
            self._preview(self.workspace_state['selection'])

    def _new_project(self):
        """Schedule the expensive index rebuild without freezing the GUI."""
        if self._project_creation is not None:
            return  # Ignore repeated clicks while the first creation is running.
        selection = self.workspace_state.get('selection') or ''
        if not self._selected_niche(selection):
            return
        self.new_project.setEnabled(False)
        try:
            from .project_management import create_project
            future = self._creation_pool.submit(create_project, self.repo, selection)
            self._project_creation = (selection, future)
            self.notice.setText('Creating project… Other controls remain usable.')
        except (OSError, ValueError, RuntimeError) as error:
            self.new_project.setEnabled(True)
            self.notice.setText('Could not start project creation: ' + str(error)[:400])
        self.notice.show()

    def _new_niche(self):
        selection = self.workspace_state.get('selection') or ''
        if not self._selected_niche(selection):
            return
        title, accepted = QInputDialog.getText(self, 'New niche folder', 'Name for the subniche:')
        if not accepted:
            return
        try:
            from .project_management import create_niche
            outcome = create_niche(self.repo, selection, title)
            self._refresh_after_edit(outcome['path'])
            self.notice.setText('Created subniche: ' + outcome['title'] + '.')
        except (OSError, ValueError, RuntimeError) as error:
            self.notice.setText('Could not create niche: ' + str(error)[:400])
        self.notice.show()

    def _delete_niche(self):
        selection = self.workspace_state.get('selection') or ''
        title = self._selected_niche(selection)
        if not title:
            return
        descendants = [row for row in self._niche_entries if row[0].startswith(selection + '/')]
        projects = sum(not directory and name.startswith(selection + '/')
                       for name, directory in self._project_entries)
        answer = QMessageBox.question(
            self, 'Delete niche',
            f'Delete “{title}”, including {len(descendants)} subniche(s) and {projects} project(s)? '
            'The entire folder and its work will be moved to a recoverable local backup. '
            'Completed project receipts are kept.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            from .project_management import delete_niche
            outcome = delete_niche(self.repo, selection)
            self._refresh_after_edit(PurePosixPath(selection).parent.as_posix())
            self.notice.setText('Niche deleted. Recoverable backup: ' + outcome['trash_path'])
        except (OSError, ValueError, RuntimeError) as error:
            self.notice.setText('Could not delete niche: ' + str(error)[:400])
        self.notice.show()

    def _delete_project(self):
        if self._project_deletion is not None:
            return
        current = self._current_project()
        if current is None or self._tree_mode != 'projects':
            return
        path, _, meta, _ = current
        selection = path.relative_to(self.repo).as_posix()
        try:
            expected_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as error:
            self.notice.setText('Could not read project: ' + str(error)[:400])
            self.notice.show()
            return
        answer = QMessageBox.question(
            self, 'Delete project',
            'Delete “' + meta['title'] + '” (' + meta['id'] + ')?\n\n'
            'The entire project directory, including project.md and work/, '
            'will be moved into a recoverable local backup. '
            'Other projects and completed-project receipts remain intact.\n\n'
            'This does not stop any independently running external Codex process.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            from .project_management import delete_project
            self.delete_project.setEnabled(False)
            future = self._creation_pool.submit(delete_project, self.repo, selection,
                                                expected_sha256=expected_sha256)
            self._project_deletion = (selection, path.parent.parent.relative_to(self.repo).as_posix(), future)
            self.notice.setText('Deleting project and preparing its recovery backup…')
        except (OSError, ValueError, RuntimeError) as error:
            self.delete_project.setEnabled(True)
            self.notice.setText('Could not delete project: ' + str(error)[:400])
        self.notice.show()

    def _paste_project(self):
        current = self._current_project()
        if not current or current[3] not in {'working_phase_1', 'working_phase_2', 'working_phase_3'}:
            return
        from .project_update import replace_project_text, snapshot_sha256
        path, raw, meta, phase = current
        selection = path.relative_to(self.repo).as_posix()
        dialog = QDialog(self)
        dialog.setWindowTitle('Paste project text · ' + meta['title'])
        dialog.resize(760, 560)
        layout = QVBoxLayout(dialog)
        label = QLabel('Paste the complete project text, including its JSON metadata. '
                       'This replaces the research record and keeps the current phase. '
                       'The previous version is backed up; work/ is preserved.')
        label.setWordWrap(True)
        layout.addWidget(label)
        editor = QPlainTextEdit()
        editor.setAccessibleName('Project text to paste')
        editor.setPlaceholderText('Paste the complete project record here…')
        clipboard = QApplication.clipboard().text()
        if clipboard.lstrip().startswith(('---', '```', '~~~~')):
            editor.setPlainText(clipboard)
        layout.addWidget(editor, 1)
        error_label = QLabel()
        error_label.setWordWrap(True)
        error_label.setStyleSheet('color: #9a3535;')
        layout.addWidget(error_label)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText('Replace project text')
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        saved = []
        def save():
            try:
                saved.append(replace_project_text(self.repo, selection, editor.toPlainText(),
                             expected_sha256=snapshot_sha256(raw)))
            except (OSError, ValueError, RuntimeError) as error:
                error_label.setText(str(error)[:600])
                return
            dialog.accept()
        buttons.accepted.connect(save)
        try:
            result = dialog.exec()
        finally:
            # Disconnect closures before Qt destroys the parent window. Keeping
            # a closed dialog's Python/Qt reference cycle can defer destruction
            # into an unrelated garbage collection while another window opens.
            buttons.accepted.disconnect(save)
            buttons.rejected.disconnect(dialog.reject)
            dialog.deleteLater()
        if result == QDialog.DialogCode.Accepted and saved:
            self._refresh_after_edit(selection)
            self.notice.setText('Project text updated. ' + PHASE_LABELS[phase] +
                                ' is unchanged; recheck it before advancing.')
            self.notice.show()

    def _set_workspace_label(self, title=None):
        label = title.strip() if isinstance(title, str) and title.strip() else 'Chat ' + self.workspace_id
        self.chat_label.setText(label)
        self.chat_label.setToolTip(label)
        self.setWindowTitle('Portfolio Manager | ' + label)

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
        self._set_workspace_label()
        self._refresh_prompt_menu(selection)
        self._phase_project = None
        self.phase_controls.hide()
        self.image.clear()
        self.image_scroll.hide()
        self.project_tabs.hide()
        self.completed_detail.hide()
        self.preview.show()
        self._preview_readme = None
        self._preview_future = None
        try:
            path = context_path(self.repo, selection)
            stat = path.stat()
            self._preview_signature = (stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size, path.is_dir())
            if path.is_dir():
                self.preview.setPlainText(f'{selection}\n\nLoading folder…')
                self._preview_future = (selection, self._pool.submit(folder_preview, self.repo, selection))
                return
            if (path.parent == self.repo / 'business_portfolio/completed_projects'
                    and path.suffix.lower() == '.json'):
                record = json.loads(path.read_text(encoding='utf-8'))
                if record.get('project_phase') != 'complete' or record.get('id') != path.stem:
                    raise ValueError('Invalid completion receipt.')
                self._set_workspace_label(record.get('title'))
                title = html.escape(str(record.get('title', path.stem)))
                description = html.escape(str(record.get('description', 'No description provided.')))
                rows = [f'<h2>{title}</h2><p>{description}</p>']
                for heading, field in (('Where to buy or download', 'sale_links'),
                                       ('Where it is marketed', 'marketing_links'),
                                       ('Other useful links', 'other_links')):
                    links = record.get(field, [])
                    if not isinstance(links, list):
                        continue
                    safe = [str(link) for link in links if isinstance(link, str)
                            and link.startswith(('https://', 'http://'))]
                    rows.append(f'<h3>{heading}</h3>')
                    if safe:
                        rows.extend(f'<p><a href="{html.escape(link, quote=True)}">{html.escape(link)}</a></p>'
                                    for link in safe)
                    else:
                        rows.append('<p>Not recorded.</p>')
                rows.append('<p><small>Saved completion record · remains after the work folder is deleted</small></p>')
                self.completed_detail.setHtml(''.join(rows))
                self.completed_detail.show()
                self.preview.hide()
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
                is_project = (suffix == '.md' and project_record_leaf(selection) and
                              (path.is_relative_to(self.repo/'business_portfolio/niches') or
                               path.is_relative_to(self.repo/'business_portfolio/archive/2026-11-15-legacy/niches') or
                               path.is_relative_to(self.repo/'business_portfolio/archive/2026-11-15-taxonomy-view-v1/niches')))
                limit = 5_000_000 if is_project else MAX_PREVIEW
                with path.open('rb') as file:
                    data = file.read(limit + 1)
                if b'\x00' not in data:
                    self.preview.setPlainText(data[:MAX_PREVIEW].decode('utf-8', errors='replace') +
                                              ('\n\nPreview shortened.' if len(data) > MAX_PREVIEW else ''))
                    if is_project and len(data) <= limit:
                        self._project_detail(data.decode('utf-8', errors='replace'), selection,
                                             archived='/archive/' in '/'+selection)
                    return
            self.preview.setPlainText(f'{path.name}\n{size:,} bytes\nPreview unavailable for this file.')
        except (ValueError, OSError):
            self._preview_signature = None
            self.preview.setPlainText('The selected path is unavailable.')

    def _project_detail(self, raw, selection, *, archived):
        from business_portfolio.tools.build_browser import parse_project
        from .project_lifecycle import project_phase
        try:
            meta, body = parse_project(raw, selection)
        except ValueError:
            return
        self._set_workspace_label(meta.get('title'))
        purpose = re.search(r'^\*\*Purpose:\*\*\s*(.+)$', body, re.M)
        overview = [meta['title'], '', 'Preserved history' if archived else 'Current project',
                    'Niche: ' + meta['niche_path'].replace('-', ' '),
                    'Phase: ' + (meta.get('project_phase', 'Historical') if archived else PHASE_LABELS[project_phase(meta)]),
                    'Work status: ' + meta['work_state'].replace('_', ' '),
                    'Evidence: ' + meta['commercial_validation'].replace('_', ' '),
                    'Supported platforms: ' + (', '.join(meta.get('platforms_supported', [])) or 'None verified'),
                    'Proposed platforms: ' + (', '.join(meta.get('platforms_proposed', [])) or 'Not specified'),
                    '', purpose.group(1) if purpose else 'See the complete record for scope and evidence.',
                    '', 'Next step:', meta['next_action']]
        if archived:
            overview += ['', 'Review the latest private checkpoint and external state before restoring.']
        self.project_overview.setPlainText('\n'.join(overview))
        work_folder = str(PurePosixPath(selection).parent / 'work') if PurePosixPath(selection).name == 'project.md' else 'Legacy file; migrate to project-folder layout for new work.'
        self.project_files.setPlainText('Project record:\n' + selection +
            '\n\nOwned work folder:\n' + work_folder +
            '\n\nKeep code, assets, drafts and tests under work/.')
        results = meta.get('public_results', [])
        self.project_results.setPlainText('\n'.join(r['label'] + ' — ' + r['path'] for r in results)
            if results else 'No verified public results are declared for this project.')
        done = re.findall(r'^\s*- \[[xX]\] (.+)$', body, re.M)
        remaining = re.findall(r'^\s*- \[ \] (.+)$', body, re.M)
        stage = meta.get('project_phase', 'working_phase_2') if archived else project_phase(meta)
        label = stage[-1] if stage in {'working_phase_4', 'working_phase_5', 'working_phase_6'} else ''
        guesses = [value for value in re.findall(r'Phase\s*' + (label or '[456]') +
                             r'\s*completion estimate:\s*(\d{1,3})\s*%', body, re.I) if int(value) <= 100]
        estimate = ('Phase ' + label + ' completion estimate: ' + guesses[-1] + '% (best guess)'
                    if guesses and label and int(guesses[-1]) <= 100
                    else 'Progress percentage: not measured.')
        self.project_tasks.setPlainText('Completed\n' + ('\n'.join('• ' + item for item in done) if done else
            'No completed tasks recorded.') + '\n\nRemaining\n' +
            ('\n'.join('• ' + item for item in remaining) if remaining else
             'No remaining checklist recorded; see the next step.') +
            '\n\n' + estimate)
        self.project_record.setPlainText(raw)
        if not archived and project_record_leaf(selection) and self._tree_mode == 'projects':
            stage = project_phase(meta)
            self._phase_project = selection
            self._displayed_phase = stage
            phase_number = int(stage[-1]) if stage != 'complete' else 7
            for index in range(self.phase_selector.count()):
                value = self.phase_selector.itemData(index)
                number = int(value[-1]) if value != 'complete' else 7
                self.phase_selector.model().item(index).setEnabled(
                    number <= 6 and (number <= phase_number or number == phase_number + 1))
            self.phase_selector.setCurrentIndex(self.phase_selector.findData(stage))
            self.phase_selector.setEnabled(True)
            self._phase_choice_changed()
            self.phase_controls.show()
        self.project_tabs.setCurrentIndex(0)
        self.project_tabs.show()
        self.preview.hide()

    def _phase_choice_changed(self):
        current = getattr(self, '_displayed_phase', None)
        target = self.phase_selector.currentData()
        if target and target != current:
            if current in {'working_phase_4', 'working_phase_5'} and target == (
                    'working_phase_' + str(int(current[-1]) + 1)):
                self.phase_apply.setText('Manually advance to Phase ' + str(int(current[-1]) + 1))
                self.phase_apply.setEnabled(True)
            else:
                self.phase_apply.setText('Update phase')
                self.phase_apply.setEnabled(target in {'working_phase_1', 'working_phase_2',
                                                       'working_phase_3', 'working_phase_4',
                                                       'working_phase_5', 'working_phase_6'} and
                                            (current == 'complete' or int(target[-1]) < int(current[-1])))
        elif current in {'working_phase_1', 'working_phase_2', 'working_phase_3'}:
            self.phase_apply.setText('Advance to Phase ' + str(int(current[-1]) + 1))
            self.phase_apply.setEnabled(True)
        elif current in {'working_phase_4', 'working_phase_5'}:
            self.phase_apply.setText('Manually advance to Phase ' + str(int(current[-1]) + 1))
            self.phase_apply.setEnabled(True)
        else:
            self.phase_apply.setText('Codex verifies completion')
            self.phase_apply.setEnabled(False)

    def _apply_project_phase(self):
        """Allow owner research advances and explicitly unverified execution fallbacks."""
        selection = self._phase_project
        if not selection:
            return
        from .project_lifecycle import set_phase, project_phase, record_path
        from business_portfolio.tools.build_browser import parse_project
        target = self.phase_selector.currentData()
        try:
            path = record_path(self.repo, selection)
            metadata, _ = parse_project(path.read_text(encoding='utf-8'), selection)
            current = project_phase(metadata)
            if target == current:
                if current not in {'working_phase_1', 'working_phase_2', 'working_phase_3',
                                   'working_phase_4', 'working_phase_5'}:
                    raise ValueError('Only Codex can verify completion after Phase 6.')
                target = 'working_phase_' + str(int(current[-1]) + 1)
            if target not in {'working_phase_1', 'working_phase_2', 'working_phase_3',
                              'working_phase_4', 'working_phase_5', 'working_phase_6'}:
                raise ValueError('Only Codex can verify completion after Phase 6.')
            backwards = current == 'complete' or int(target[-1]) < int(current[-1])
            override = not backwards and current in {'working_phase_4', 'working_phase_5'}
            if override and QMessageBox.question(
                    self, 'Manually advance unverified phase',
                    f'Advance from {PHASE_LABELS[current]} to {PHASE_LABELS[target]} '
                    'without verified completion of the current phase?\n\n'
                    'This is a recovery override, NOT proof that build, release or marketing '
                    'was finished. Any unfinished tasks and blockers must be checked '
                    'before the next phase performs release or promotion.',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                self._preview(selection)
                return
            if backwards and QMessageBox.question(
                    self, 'Change project phase',
                    f'Move this project from {PHASE_LABELS[current]} back to {PHASE_LABELS[target]}?'
                    + (' This removes its verified Completed Projects receipt until Codex verifies completion again.' if current == 'complete' else '')
                    + ' The canonical record will be updated.') != QMessageBox.StandardButton.Yes:
                self._preview(selection)
                return
            set_phase(self.repo, selection, target, actor='user')
            self.notice.setText(('Manual override recorded as NOT VERIFIED. ' if override else '') +
                                PHASE_LABELS[target] + ' is ready. Copy its prompt to continue.')
            self.notice.show()
            self._preview(selection)
            self._refresh_project_phase_rows()
        except (OSError, ValueError, TypeError) as error:
            self.notice.setText('Could not update project phase: ' + str(error)[:300])
            self.notice.show()
            self._preview(selection)

    def closeEvent(self, event):
        if self._project_deletion is not None:
            self._finish_project_deletion()
            if self._project_deletion is not None:
                self.notice.setText('Project deletion is still in progress. Please wait until it finishes.')
                self.notice.show()
                event.ignore()
                return
        self._closing = True
        self._sync.stop()
        # Qt owns these children. Remove Python event filters and callbacks
        # before native deferred deletion, rather than leaving reference cycles
        # to be collected while another workspace is being constructed.
        for widget in self._drop_targets:
            widget.removeEventFilter(self)
        self._drop_targets = ()
        self.prompt_menu.clear()
        self._pool.shutdown(wait=False, cancel_futures=True)
        self._creation_pool.shutdown(wait=False, cancel_futures=True)
        self.on_close(self.workspace_id)
        event.accept()
