"""Read-only inspection of one explicit test-profile journal; never deletes profiles."""
import json
import msvcrt
import os
from pathlib import Path
import re
import stat


def windows_owner_state(pid):
    """Conservatively inspect a PID; reuse is treated as live, never as stale."""
    import pywintypes
    import win32api
    import win32con
    import win32event
    try:
        process = win32api.OpenProcess(win32con.SYNCHRONIZE, False, pid)
    except pywintypes.error as error:
        return 'dead' if error.winerror == 87 else 'unknown'
    try:
        status = win32event.WaitForSingleObject(process, 0)
        if status == win32event.WAIT_OBJECT_0:
            return 'dead'
        if status == win32event.WAIT_TIMEOUT:
            return 'alive'
        return 'unknown'
    except pywintypes.error:
        return 'unknown'
    finally:
        process.Close()


def inspect_record(root, identifier, *, owner_state):
    """Return a conservative status; this is not an authorization to recover.

    owner_state(pid) must return 'dead', 'alive', or 'unknown'. All filesystem
    objects, journal provenance, profile-token activity and PID reuse remain
    untrusted until independently verified by a real controller.
    """
    if not re.fullmatch(r'[0-9a-f]{32}', identifier):
        raise ValueError('Invalid journal identifier')
    root = Path(root)
    paths = (root, root / (identifier + '.lock'), root / (identifier + '.json'))
    try:
        for index, path in enumerate(paths):
            info = path.lstat()
            if (stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400 or
                    (index == 0 and not stat.S_ISDIR(info.st_mode)) or
                    (index != 0 and not stat.S_ISREG(info.st_mode))):
                return {'status': 'ambiguous', 'reason': 'unsafe record path'}
        if paths[2].stat().st_size > 16384:
            return {'status': 'ambiguous', 'reason': 'record too large'}
        with paths[1].open('r+b') as lock:
            try:
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                return {'status': 'busy', 'reason': 'owner lock held'}
            try:
                record = json.loads(paths[2].read_text(encoding='utf-8'))
                if not isinstance(record, dict) or set(record) != {'version','id','owner_pid','pending','created'}:
                    return {'status': 'ambiguous', 'reason': 'invalid record schema'}
                expected = {'PortfolioManager.A.' + identifier + '.model',
                            'PortfolioManager.A.' + identifier + '.test'}
                created = record['created']
                pid = record['owner_pid']
                if (record['version'] != 2 or record['id'] != identifier or
                        not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0 or
                        not isinstance(created, list) or not all(isinstance(name, str) for name in created) or
                        len(set(created)) != len(created) or not set(created).issubset(expected)):
                    return {'status': 'ambiguous', 'reason': 'invalid record content'}
                if record['pending'] is not None:
                    return {'status': 'ambiguous', 'reason': 'profile operation was interrupted'}
                state = owner_state(pid)
                if state != 'dead':
                    return {'status': 'busy' if state == 'alive' else 'ambiguous', 'reason': 'owner not proven stopped'}
                # No deletion is possible here: root provenance and every
                # profile process must still be independently established.
                return {'status': 'requires_proof', 'reason': 'journal provenance and profile activity unverified',
                        'created_count': len(created)}
            finally:
                lock.seek(0); msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
    except (OSError, ValueError, TypeError):
        return {'status': 'ambiguous', 'reason': 'record unavailable or invalid'}
