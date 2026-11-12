"""Independent views of the shared Portfolio Manager controller."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path, PurePosixPath

from PySide6.QtCore import QSignalBlocker, Qt, QTimer
from PySide6.QtGui import QImageReader, QPixmap
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                               QPlainTextEdit, QPushButton, QScrollArea, QSplitter,
                               QTabWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

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
        self._search_view = False
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='workspace-files')
        label = workspace.get('label') or ('Chat ' + self.workspace_id[:8])
        self.setWindowTitle('Portfolio Manager | ' + label)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.resize(1120, 760)
        frame = QWidget(self)
        layout = QVBoxLayout(frame)
        controls = QVBoxLayout()
        layout.addLayout(controls)
        header = QHBoxLayout()
        self.selection_label = QLabel()
        self.selection_label.setTextFormat(Qt.TextFormat.PlainText)
        self.selection_label.setWordWrap(True)
        header.addWidget(self.selection_label, 1)
        self.stop_worker = QPushButton('Stop this chat’s worker')
        self.stop_worker.clicked.connect(self._stop_worker)
        header.addWidget(self.stop_worker)
        access = QPushButton('Computer Access')
        access.clicked.connect(on_access)
        header.addWidget(access)
        layout.addLayout(header)
        self.tabs = QTabWidget(frame)
        self.panel = ManagerPanel(host.coordinator, host.supervisor, on_emergency,
                                  on_stop_all=on_stop_all, on_context=self.select,
                                  start_context_worker=self._start_worker,
                                  can_start_context=self._is_worker_folder,
                                  header_layout=controls,
                                  context_worker=lambda: (self.workspace_state or {}).get('worker_id'))
        self.tabs.addTab(self.panel, 'Projects')
        self.tabs.addTab(self._make_explorer(), 'Files')
        layout.addWidget(self.tabs)
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
        self.find.setPlaceholderText('Search repository paths, then press Enter')
        self.find.returnPressed.connect(self._find_files)
        layout.addWidget(self.find)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Repository files'])
        self.tree.itemExpanded.connect(self._expand)
        self.tree.itemSelectionChanged.connect(self._select_file)
        layout.addWidget(self.tree)
        splitter.addWidget(navigator)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.image = QLabel()
        self.image.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidget(self.image)
        detail = QWidget()
        details = QVBoxLayout(detail)
        details.addWidget(self.preview)
        details.addWidget(self.image_scroll)
        self.image_scroll.hide()
        splitter.addWidget(detail)
        splitter.setStretchFactor(1, 2)
        self._root_node()
        return splitter

    def _node(self, parent, name, directory, *, full=False):
        label = name if full else PurePosixPath(name).name
        item = QTreeWidgetItem(parent, [label])
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

    def _focus_tree(self, selection):
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
                item.setExpanded(True)
                self._expand(item)
                item = next((item.child(i) for i in range(item.childCount())
                             if item.child(i).data(0, ROLE) == parent.as_posix()), None)
                if item is None:
                    return
            self.tree.setCurrentItem(item)
            self.tree.scrollToItem(item)

    def _expand(self, node):
        if node.childCount() or not node.data(0, ROLE + 1):
            return
        try:
            path = context_path(self.repo, node.data(0, ROLE))
            for name, directory in children(self.repo, path):
                self._node(node, name, directory)
        except (ValueError, OSError):
            return

    def _find_files(self):
        query = self.find.text().strip().casefold()
        if not query:
            self._search = None
            self._root_node()
            self._focus_tree(self.workspace_state['selection'])
        elif self._search is None or self._search.done():
            self._search = self._pool.submit(search_paths, self.repo, query)

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

    def _is_worker_folder(self):
        if not self.workspace_state:
            return False
        selection = self.workspace_state['selection']
        try:
            return PurePosixPath(selection).is_relative_to(NICHE_ROOT) and context_path(self.repo, selection).is_dir()
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
                with QSignalBlocker(self.tree):
                    self.tree.clear()
                    for name, directory in future.result():
                        self._node(self.tree, name, directory, full=True)
                self._search_view = True
                self._focus_tree(self.workspace_state['selection'])
        except (ValueError, OSError, RuntimeError) as error:
            self.panel.notice.setText(str(error)[:400])

    def apply_workspace(self, workspace):
        previous = self.workspace_state
        if previous and workspace['revision'] < previous['revision']:
            return
        self.workspace_state = workspace
        self.stop_worker.setEnabled(bool(workspace.get('worker_id')))
        if previous and previous['selection'] == workspace['selection']:
            return
        selection = workspace['selection']
        self.selection_label.setText(f'Chat {self.workspace_id[:8]} · {selection}')
        path = PurePosixPath(selection)
        is_record = path.is_relative_to(NICHE_ROOT) and path.parent.name == 'projects' and path.suffix == '.md'
        is_folder = self._is_worker_folder()
        self.panel.context_record = selection if is_record else None
        self.panel._epoch += 1
        if is_record:
            self.panel._set_folder(path.parent.parent.as_posix(), notify=False)
        elif is_folder:
            self.panel._set_folder(selection, notify=False)
        self.panel.refresh()
        self._focus_tree(selection)
        self._preview(selection)
        if not (is_record or is_folder):
            self.tabs.setCurrentIndex(1)

    def _preview(self, selection):
        self.image.clear()
        self.image_scroll.hide()
        self.preview.show()
        try:
            path = context_path(self.repo, selection)
            if path.is_dir():
                self.preview.setPlainText(selection + '\n\nFolder')
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
            self.preview.setPlainText('The selected path is unavailable.')

    def closeEvent(self, event):
        self._sync.stop()
        self.panel.shutdown()
        self._pool.shutdown(wait=False, cancel_futures=True)
        self.on_close(self.workspace_id)
        event.accept()
