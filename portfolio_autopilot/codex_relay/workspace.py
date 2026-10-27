"""Capability-based file tools. No shell, subprocess, deletion or network tools."""
import ast
import hashlib
import json
from pathlib import Path
import threading

from .config import safe_path


TOOL = {"type": "function", "name": "relay_workspace",
        "description": "Owner-approved host capability: read/write exact approved UTF-8 files, list paths, or check Python/JSON syntax. The Windows relay performs these operations outside your intentionally read-only command sandbox. Writes through this capability are already authorized; do not request broader OS permissions. A read of an absent approved file returns exists=false, sha256='new'. Use that hash for creation or the current read hash for an overwrite. No shell execution.",
        "inputSchema": {"type": "object", "properties": {
            "operation": {"type": "string", "enum": ["list", "read", "write", "check"]},
            "path": {"type": "string"}, "content": {"type": "string"},
            "sha256": {"type": "string"}},
            "required": ["operation", "path", "content", "sha256"], "additionalProperties": False}}


class Workspace:
    def __init__(self, root, paths, active, record, backup_dir):
        self.root = Path(root).resolve()
        self.paths = frozenset(paths)
        self.active, self.record = active, record
        self.backup_dir = Path(backup_dir)
        self.lock = threading.RLock()
        for p in paths:
            safe_path(self.root, p)

    def call(self, args):
        with self.lock:
            if not self.active():
                raise ValueError("Task is paused or cancelled")
            if set(args) != {"operation", "path", "content", "sha256"} or not all(isinstance(v, str) for v in args.values()):
                raise ValueError("Invalid tool arguments")
            op, name = args["operation"], args["path"]
            if op == "list":
                return {"paths": sorted(self.paths), "policy": "Only these exact files are available"}
            if name not in self.paths and not (op == "read" and name == "AGENTS.md"):
                raise ValueError("File is outside locally approved scope")
            path = safe_path(self.root, name)
            if path.exists() and path.stat().st_size > 500_000:
                raise ValueError("File exceeds 500 KB tool limit")
            if op == "read":
                if not path.exists():
                    return {'exists': False, 'content': '', 'sha256': 'new'}
                raw = path.read_bytes()
                return {"exists": True, "content": raw.decode('utf-8'), "sha256": hashlib.sha256(raw).hexdigest()}
            if op == "write":
                if len(args["content"].encode()) > 500_000:
                    raise ValueError("File exceeds 500 KB tool limit")
                old = path.read_bytes() if path.exists() else None
                expected = hashlib.sha256(old).hexdigest() if old is not None else "new"
                if args["sha256"] != expected:
                    raise ValueError("File changed; read it again before writing")
                # Preserve the original once, outside the repository, before any overwrite.
                backup = self.backup_dir / hashlib.sha256(name.encode()).hexdigest()
                backup.parent.mkdir(parents=True, exist_ok=True)
                if not backup.exists():
                    backup.write_bytes(old if old is not None else b"")
                path.parent.mkdir(parents=True, exist_ok=True)
                safe_path(self.root, name)
                path.write_text(args["content"], encoding="utf-8", newline="")
                self.record("FILE_CHANGED", name)
                return {"written": name}
            if op == "check":
                content = path.read_text(encoding="utf-8")
                if path.suffix == ".py":
                    ast.parse(content, filename=name)
                elif path.suffix == ".json":
                    json.loads(content)
                else:
                    raise ValueError("Only Python and JSON syntax checks are supported")
                self.record("TEST_RESULT", f"PASS syntax check: {name} (code not executed)")
                return {"result": "PASS syntax check; code not executed"}
            raise ValueError("Unknown operation")
