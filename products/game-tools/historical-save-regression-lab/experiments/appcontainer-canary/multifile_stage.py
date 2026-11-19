"""Experimental multi-file save staging; not an execution sandbox."""
from pathlib import Path
import hashlib
import re
import tempfile

NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\Z")
HASH = re.compile(r"[0-9a-f]{64}\Z")

def stage(source, scratch, expected):
    """Copy pinned bytes into a fresh temporary directory; caller owns cleanup."""
    source, scratch = Path(source), Path(scratch)
    if not isinstance(expected, dict) or not expected or len(expected) > 64:
        raise ValueError('invalid fixture map')
    if not source.is_dir() or source.is_symlink() or not scratch.is_dir() or scratch.is_symlink():
        raise ValueError('invalid root')
    folded = set()
    content = {}
    for name, digest in expected.items():
        if not isinstance(name, str) or not NAME.fullmatch(name) or name.endswith('.') or name.lower() in folded:
            raise ValueError('invalid fixture name')
        folded.add(name.lower())
        if not isinstance(digest, str) or not HASH.fullmatch(digest):
            raise ValueError('invalid fixture hash')
        path = source / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('invalid fixture file')
        data = path.read_bytes()
        if len(data) > 1024 * 1024 or hashlib.sha256(data).hexdigest() != digest:
            raise ValueError('fixture hash or size mismatch')
        content[name] = data
    directory = tempfile.TemporaryDirectory(prefix='gdm-multifile-', dir=scratch)
    try:
        for name, data in content.items():
            (Path(directory.name) / name).write_bytes(data)
    except BaseException:
        directory.cleanup()
        raise
    return directory
