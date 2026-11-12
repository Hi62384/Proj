"""Own exactly two disposable AppContainer profiles for one acceptance case.

This is test-only. It does not perform recovery after controller termination.
"""
import ctypes
import re
import uuid
from pathlib import Path


class OwnedProfiles:
    def __init__(self, *, _api=None, _identifier=None):
        real_api = _api is None
        if _api is None:
            from portfolio_manager.tests.live_windows_isolation import u, a
        else:
            u, a = _api
        self._u = u
        self._a = a
        self.identifier = _identifier if _identifier is not None else uuid.uuid4().hex
        if not re.fullmatch(r'[0-9a-f]{32}', self.identifier):
            raise ValueError('Invalid generated profile identifier')
        self._created = []
        self._journal = None
        try:
            if real_api:
                from portfolio_manager.tests.windows_profile_journal import ProfileJournal
                repo = Path(__file__).resolve().parents[2]
                root = repo / '.tmp' / 'portfolio-acceptance-profile-journals'
                root.mkdir(parents=True, exist_ok=True)
                if not root.resolve().is_relative_to(repo) or root.is_symlink():
                    raise ValueError('Acceptance journal must stay inside the checkout')
                self._journal = ProfileJournal(root, self.identifier)
            for suffix in ('model', 'test'):
                name = 'PortfolioManager.A.' + self.identifier + '.' + suffix
                if self._journal is not None:
                    self._journal.update(pending=name, created=self._created)
                sid = ctypes.c_void_p()
                result = self._u.CreateAppContainerProfile(name, name, 'Owned synthetic acceptance probe',
                                                           None, 0, ctypes.byref(sid))
                if result:
                    if self._journal is not None:
                        self._journal.update(pending=None, created=self._created)
                    raise OSError('Could not create owned test profile: 0x%08x' % (result & 0xffffffff))
                self._created.append(name)
                self._a.FreeSid(sid)
                if self._journal is not None:
                    self._journal.update(pending=None, created=self._created)
        except BaseException:
            self.close()
            raise

    def close(self):
        failures = []
        # Only names whose creation succeeded in this object can be removed.
        remaining = []
        for name in reversed(self._created):
            if self._journal is not None:
                self._journal.update(pending=name, created=self._created)
            result = self._u.DeleteAppContainerProfile(name)
            if result:
                failures.append(result & 0xffffffff)
                remaining.append(name)
            else:
                self._created.remove(name)
            if self._journal is not None:
                self._journal.update(pending=None, created=self._created)
        self._created = list(reversed(remaining))
        if not failures and self._journal is not None:
            self._journal.finish()
            self._journal = None
        if failures:
            raise RuntimeError('Owned test-profile cleanup failed: ' + ', '.join('0x%08x' % code for code in failures))

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()
