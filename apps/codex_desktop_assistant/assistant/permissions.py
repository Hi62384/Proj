"""Owner-only, process-local grants. Retrieved content cannot modify these grants."""
import threading
from contextlib import contextmanager
from urllib.parse import urlsplit


class Denied(PermissionError):
    pass


def origin(url):
    p = urlsplit(url)
    if p.scheme not in ('http','https') or not p.hostname or p.username or p.password:
        raise Denied('Only explicit HTTP(S) origins are supported')
    port = p.port or (443 if p.scheme == 'https' else 80)
    host=p.hostname.lower()
    if ':' in host:host='['+host+']'
    return f'{p.scheme}://{host}:{port}'


class Permissions:
    def __init__(self):
        self.lock = threading.RLock()
        self.halted = threading.Event()
        self.halted.set()
        self.generation = 0
        self.windows = {}
        self.origins = set()
        self.files = {}
        self.observe = False
        self.desktop = False
        self.browser = False
        self.owner = None
        self.routine_labels = set()
        self.capture_bounds = None
        self.applications = {}
        self.safety_check=None
        from .file_policy import FilePolicy
        self.file_policy=FilePolicy()
        self.desktop_mode='Selected Window'
        self.desktop_target_name=''
        self.monitor_layout=None
        self.allow_launches=False
        self.input_check=None
        self.desktop_suspended=False

    def halt(self):
        # Immediate signal is independent of AI/Qt/Playwright and any pending approval.
        self.halted.set()
        self.generation += 1

    def revoke(self):
        self.halt()
        with self.lock:
            self.windows.clear(); self.origins.clear(); self.files.clear()
            self.routine_labels.clear()
            self.capture_bounds=None
            self.applications.clear()
            self.file_policy.session.clear()
            self.allow_launches=False
            self.monitor_layout=None
            self.desktop_target_name=''
            self.observe = self.desktop = self.browser = False

    def resume(self, conversation):
        with self.lock:
            self.owner = conversation
            self.desktop_suspended=False
            self.generation += 1
            self.halted.clear()

    @contextmanager
    def action(self, conversation, generation=None):
        with self.lock:
            if self.halted.is_set() or self.owner != conversation or (generation is not None and generation != self.generation):
                raise Denied('Control is paused, revoked, or belongs to another conversation')
            if self.safety_check and not self.safety_check():
                self.halt();raise Denied('Desktop locked or resumed from sleep; review before resuming input')
            yield

    def check_origin(self, url):
        if origin(url) not in self.origins:
            raise Denied('Website origin has not been approved locally')

    def snapshot(self):
        return {'paused':self.halted.is_set(),'observation':self.observe,'desktop':self.desktop,
                'browser':self.browser,'windows':list(self.windows),'origins':sorted(self.origins),
                'mode':self.desktop_mode,'launches':self.allow_launches}
