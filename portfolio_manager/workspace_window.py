"""Independent views of the shared Portfolio Manager controller."""
from concurrent.futures import ThreadPoolExecutor
import os
import json
from pathlib import Path, PurePosixPath
import re

from PySide6.QtCore import QSignalBlocker, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QImageReader, QPixmap
from PySide6.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                               QMenu, QPlainTextEdit, QPushButton, QScrollArea, QSplitter,
                               QStyle, QTabWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

from .workspace import context_path


ROLE = int(Qt.ItemDataRole.UserRole)
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
    for name, _, _, _ in niches:
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
    priorities = {name: priority for name, _, _, priority in niches}
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
            rows.append((relative, meta['title'], count, meta.get('priority', 999)))
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
        self._entry_future = self._pool.submit(self._load_navigation_entries, self.repo)
        self._entries_ready = False
        self._tree_mode = 'projects'
        self._file_loads = {}
        self._folder_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        self._file_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
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
        self.tree.setHeaderLabels(['Projects'])
        self.tree.itemSelectionChanged.connect(self._select_file)
        self.tree.itemExpanded.connect(self._expand)
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

    def _node(self, parent, name, directory, *, full=False):
        label = name if full else PurePosixPath(name).name
        if not full and not directory and '/projects/' in name and name.lower().endswith('.md'):
            stem = PurePosixPath(name).stem
            match = re.match(r'([a-z]+-[0-9]+)-(.+)', stem, re.I)
            if match:
                label = match.group(1).upper() + ' · ' + match.group(2).replace('-', ' ').title()
        item = QTreeWidgetItem(parent, [label])
        item.setIcon(0, self._folder_icon if directory else self._file_icon)
        item.setData(0, ROLE, name)
        item.setData(0, ROLE + 1, directory)
        if directory:
            item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
        return item

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
            if not self._entries_ready and self._tree_mode != 'files':
                self._node(root, 'Loading navigation…', False, full=True)
                root.setExpanded(True)
                return
            if self._tree_mode == 'files':
                root.setExpanded(True)
                self._expand(root)
                return
            if self._tree_mode == 'niches':
                nodes = {'.': root}
                for name, title, count, _ in self._niche_entries:
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
                    node.setText(0, f'{title} · {count} {"project" if count == 1 else "projects"}')
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
                        nodes[name].setText(0, f'{niche[1]} · {count} {"project" if count == 1 else "projects"}')
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
            if not self._entries_ready and self._entry_future.done():
                try:
                    self._project_entries, self._history_entries, self._niche_entries = self._entry_future.result()
                    self._entries_ready = True
                    if self._tree_mode != 'files':
                        self._root_node()
                        self._focus_tree(self.workspace_state['selection'])
                except (OSError, ValueError, RuntimeError) as error:
                    self.search_status.setText('Could not load project navigation: ' + str(error)[:240])
                    self.search_status.show()
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
        self.preview.hide()

    def closeEvent(self, event):
        self._sync.stop()
        self._pool.shutdown(wait=False, cancel_futures=True)
        self.on_close(self.workspace_id)
        event.accept()
