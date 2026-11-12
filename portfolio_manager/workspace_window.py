"""Independent views of the shared Portfolio Manager controller."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path, PurePosixPath

from PySide6.QtCore import QSignalBlocker, Qt, QTimer
from PySide6.QtGui import QImageReader, QPixmap
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                               QPlainTextEdit, QPushButton, QScrollArea, QSplitter,
                               QStackedWidget, QStyle, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

from .ui import ManagerPanel, NICHE_ROOT
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
    queue = [repo]
    hits = []
    remaining = 6000
    while queue and len(hits) < 100 and remaining > 0:
        folder = queue.pop()
        try:
            entries = children(repo, folder)
        except OSError:
            continue
        remaining -= max(len(entries), 1)
        for name, directory in entries:
            if query in name.casefold():
                hits.append((name, directory))
                if len(hits) == 100:
                    break
            if directory:
                queue.append(repo / name)
    return hits


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
        label = workspace.get('label') or ('Workspace ' + self.workspace_id[:8])
        self.setWindowTitle('Portfolio Manager | ' + label)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.resize(1120, 760)
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
        controls = QVBoxLayout()
        layout.addLayout(controls)
        header = QHBoxLayout()
        self.selection_label = QLabel()
        self.selection_label.setTextFormat(Qt.TextFormat.PlainText)
        self.selection_label.setWordWrap(True)
        header.addWidget(self.selection_label, 1)
        self.stop_worker = QPushButton('Stop worker')
        self.stop_worker.clicked.connect(self._stop_worker)
        header.addWidget(self.stop_worker)
        access = QPushButton('Computer Access')
        access.clicked.connect(on_access)
        header.addWidget(access)
        self.activity_button = QPushButton('Projects and activity')
        self.activity_button.setCheckable(True)
        self.activity_button.toggled.connect(self._show_activity)
        header.addWidget(self.activity_button)
        layout.addLayout(header)
        self.panel = ManagerPanel(host.coordinator, host.supervisor, on_emergency,
                                  on_stop_all=on_stop_all, on_context=self.select,
                                  start_context_worker=self._start_worker,
                                  can_start_context=self._is_worker_selection,
                                  header_layout=controls,
                                  candidate_host=host,
                                  prepare_context_development=self._prepare_development,
                                  context_worker=lambda: (self.workspace_state or {}).get('worker_id'))
        layout.addWidget(self._make_explorer(), 1)
        # Keep notices visible while the file preview is selected as well.
        layout.addWidget(self.panel.notice)
        self.setCentralWidget(frame)
        self._sync = QTimer(self)
        self._sync.setInterval(400)
        self._sync.timeout.connect(self.sync)
        self.apply_workspace(workspace)
        self._sync.start()

    def _make_explorer(self):
        splitter = QSplitter()
        navigator = QWidget()
        layout = QVBoxLayout(navigator)
        self.find = QLineEdit()
        self.find.setAccessibleName('Search repository files')
        self.find.setPlaceholderText('Search repository paths, then press Enter')
        self.find.returnPressed.connect(self._find_files)
        layout.addWidget(self.find)
        self.search_status = QLabel()
        self.search_status.setWordWrap(True)
        self.search_status.hide()
        layout.addWidget(self.search_status)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Repository files'])
        self.tree.itemExpanded.connect(self._expand)
        self.tree.itemSelectionChanged.connect(self._select_file)
        layout.addWidget(self.tree)
        splitter.addWidget(navigator)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setAccessibleName('Selected file or folder preview')
        self.image = QLabel()
        self.image.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidget(self.image)
        detail = QWidget()
        details = QVBoxLayout(detail)
        self.detail_stack = QStackedWidget()
        file_details = QWidget()
        file_layout = QVBoxLayout(file_details)
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.addWidget(self.preview)
        file_layout.addWidget(self.image_scroll)
        self.detail_stack.addWidget(file_details)
        self.detail_stack.addWidget(self.panel)
        details.addWidget(self.detail_stack)
        self.image_scroll.hide()
        splitter.addWidget(detail)
        splitter.setStretchFactor(1, 2)
        self._root_node()
        return splitter

    def _show_activity(self, visible):
        self.detail_stack.setCurrentIndex(1 if visible else 0)
        self.activity_button.setText('File preview' if visible else 'Projects and activity')

    def _node(self, parent, name, directory, *, full=False):
        label = name if full else PurePosixPath(name).name
        item = QTreeWidgetItem(parent, [label])
        icon = QStyle.StandardPixmap.SP_DirIcon if directory else QStyle.StandardPixmap.SP_FileIcon
        item.setIcon(0, self.style().standardIcon(icon))
        item.setData(0, ROLE, name)
        item.setData(0, ROLE + 1, directory)
        if directory:
            item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
        return item

    def _root_node(self):
        self._search_view = False
        with QSignalBlocker(self.tree):
            self.tree.clear()
            root = self._node(self.tree, '.', True, full=True)
            root.setText(0, self.repo.name)
            root.setExpanded(True)
            self._expand(root)

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
                self._expand(item)
                item = next((item.child(i) for i in range(item.childCount())
                             if item.child(i).data(0, ROLE) == parent.as_posix()), None)
                if item is None:
                    return
            if self.tree.currentItem() is not item:
                self.tree.setCurrentItem(item)
                if reveal:
                    self.tree.scrollToItem(item)

    def _expand(self, node):
        if not node.data(0, ROLE + 1):
            return
        try:
            path = context_path(self.repo, node.data(0, ROLE))
            stat = path.stat()
            signature = (stat.st_mtime_ns, stat.st_ctime_ns)
            if node.data(0, ROLE + 2) == signature:
                return
            entries = children(self.repo, path)
            with QSignalBlocker(self.tree):
                desired = {name: directory for name, directory in entries}
                for index in reversed(range(node.childCount())):
                    item = node.child(index)
                    name = item.data(0, ROLE)
                    if name not in desired or item.data(0, ROLE + 1) != desired[name]:
                        node.takeChild(index)
                for index, (name, directory) in enumerate(entries):
                    if index < node.childCount() and node.child(index).data(0, ROLE) == name:
                        continue
                    item = self._node(node, name, directory)
                    node.takeChild(node.indexOfChild(item))
                    node.insertChild(index, item)
                node.setData(0, ROLE + 2, signature)
        except (ValueError, OSError):
            return

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
            self._search = self._pool.submit(search_paths, self.repo, query)
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
            self.panel.notice.setText(str(error)[:400])
            self.sync()
            return False
        self.apply_workspace(update)
        return True

    def _start_worker(self):
        result = self.host.start_workspace_worker(self.workspace_id)
        self.sync()
        return result

    def _prepare_development(self):
        selected = dict(self.workspace_state)
        chosen = QFileDialog.getExistingDirectory(self, 'Choose the project source folder', str(self.repo))
        if not chosen:
            return
        folder = context_path(self.repo, chosen)
        if not folder.is_dir():
            raise ValueError('Choose a source folder inside this repository.')
        result = self.host.prepare_selected_development(
            self.workspace_id, folder.relative_to(self.repo).as_posix(),
            expected_selection=selected['selection'], expected_revision=selected['revision'])
        self.sync()
        self.panel.notice.setText('Project worker started. Follow its progress in Projects and activity.')
        return result

    def _is_worker_folder(self):
        if not self.workspace_state:
            return False
        selection = self.workspace_state['selection']
        try:
            return PurePosixPath(selection).is_relative_to(NICHE_ROOT) and context_path(self.repo, selection).is_dir()
        except (ValueError, OSError):
            return False

    def _is_worker_selection(self):
        if self._is_worker_folder():
            return True
        if not self.workspace_state:
            return False
        selection = self.workspace_state['selection']
        try:
            path = context_path(self.repo, selection)
            return (path.is_file() and path.parent.name == 'projects' and
                    path.suffix.lower() == '.md' and path.is_relative_to(self.host.coordinator.niches))
        except (ValueError, OSError):
            return False

    def _stop_worker(self):
        try:
            self.host.stop_workspace_worker(self.workspace_id)
            self.sync()
        except (ValueError, OSError, RuntimeError) as error:
            self.panel.notice.setText(str(error)[:400])

    def sync(self):
        try:
            self.apply_workspace(self.host.get_workspace(self.workspace_id))
            mode = self.host.control()['mode']
            index = self.panel.mode.findData(mode)
            if index >= 0:
                self.panel.mode.setCurrentIndex(index)
            if self._search and self._search.done():
                future, self._search = self._search, None
                results = future.result()
                pending, self._pending_search = self._pending_search, None
                if pending and pending != self._search_query:
                    self._search_query = pending
                    self._search = self._pool.submit(search_paths, self.repo, pending)
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
            self.panel.notice.setText(str(error)[:400])

    def apply_workspace(self, workspace):
        previous = self.workspace_state
        if previous and workspace['revision'] < previous['revision']:
            return
        self.workspace_state = workspace
        worker_id = workspace.get('worker_id')
        try:
            worker = self.host.coordinator.worker(worker_id) if worker_id else None
        except (ValueError, KeyError):
            worker = None
        self.stop_worker.setVisible(bool(worker and worker.get('state') in ('running', 'paused')))
        if previous and previous['selection'] == workspace['selection']:
            self._refresh_preview_if_changed(workspace['selection'])
            # Refresh the visible ancestry as other chats create or remove files.
            # Re-selecting also restores the highlight if a refreshed parent
            # rebuilt its children.
            self._focus_tree(workspace['selection'], reveal=False)
            return
        selection = workspace['selection']
        self.selection_label.setText(f'Workspace {self.workspace_id[:8]} · {selection}')
        path = PurePosixPath(selection)
        is_record = path.is_relative_to(NICHE_ROOT) and path.parent.name == 'projects' and path.suffix.lower() == '.md'
        is_folder = self._is_worker_folder()
        self.panel.context_record = selection if is_record else None
        self.panel._epoch += 1
        # The previous project's actions and results must not remain available
        # while the asynchronous state refresh resolves the new selection.
        self.panel._selected_project = None
        self.panel._render_project()
        self.panel._update_results([], {})
        if is_record:
            self.panel._set_folder(path.parent.parent.as_posix(), notify=False)
        elif is_folder:
            self.panel._set_folder(selection, notify=False)
        self.panel.refresh()
        self._focus_tree(selection)
        self._preview(selection)
        self.activity_button.setChecked(is_record)
        self._show_activity(is_record)

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
                    return
            self.preview.setPlainText(f'{path.name}\n{size:,} bytes\nPreview unavailable for this file.')
        except (ValueError, OSError):
            self._preview_signature = None
            self.preview.setPlainText('The selected path is unavailable.')

    def closeEvent(self, event):
        self._sync.stop()
        self.panel.shutdown()
        self._pool.shutdown(wait=False, cancel_futures=True)
        self.on_close(self.workspace_id)
        event.accept()
