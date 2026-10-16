from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def data_directory() -> Path:
    return Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local/share"))) / "CodexRelay"


@dataclass
class Config:
    workspace: Path = ROOT
    data_dir: Path = field(default_factory=data_directory)
    repository: str = "Hi62384/Proj"
    owner_id: int = 0
    trusted_ids: list[int] = field(default_factory=list)
    poll_seconds: int = 60
    port: int = 8766
    codex_binary: str = ""
    model: str = ""

    def validate(self):
        self.workspace = Path(self.workspace).resolve()
        self.data_dir = Path(self.data_dir).resolve()
        if self.repository != "Hi62384/Proj":
            raise ValueError("This relay is restricted to Hi62384/Proj")
        if self.data_dir.is_relative_to(self.workspace):
            raise ValueError("Runtime data must be outside the repository")
        if not (self.workspace / "AGENTS.md").is_file():
            raise ValueError("Workspace must contain AGENTS.md")
        if not 15 <= self.poll_seconds <= 3600 or not 1024 <= self.port <= 65535:
            raise ValueError("Invalid polling interval or port")
        if type(self.owner_id) is not int or self.owner_id < 0:
            raise ValueError("Owner must be a numeric GitHub account ID")
        if any(type(i) is not int or i <= 0 for i in self.trusted_ids):
            raise ValueError("Trusted accounts must be positive numeric IDs")
        return self

    @classmethod
    def load(cls, directory=None):
        directory = Path(directory or data_directory()).resolve()
        path = directory / "config.json"
        if not path.exists():
            return cls(data_dir=directory).validate()
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls(**{**raw, "data_dir": directory}).validate()

    def save(self):
        self.validate()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        raw = {k: str(v) if isinstance(v, Path) else v for k, v in vars(self).items()}
        path = self.data_dir / "config.json"
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(raw, indent=2), encoding="utf-8")
        temp.replace(path)


def safe_path(root: Path, value: str) -> Path:
    """Exact relative file names only; no symlinks, junctions, ADS or secrets."""
    if not isinstance(value, str) or not value or len(value) > 220:
        raise ValueError("Invalid relative file name")
    parts = value.replace("\\", "/").split("/")
    blocked = {".git", ".codex", ".agents", ".aws", ".ssh", ".github", ".local",
               "node_modules", "__pycache__", "codex_relay"}
    if any(p in ("", ".", "..") or p.lower() in blocked or p.endswith((" ", ".")) or
           ":" in p or re.search(r'[<>"|?*\x00-\x1f]', p) or
           p.lower().startswith((".env", "credentials", "auth.json")) or
           re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(\..*)?", p)
           for p in parts):
        raise ValueError("Protected or invalid file name")
    if parts[-1].lower().endswith((".pem", ".key", ".pfx", ".db", ".sqlite")):
        raise ValueError("Sensitive file type")
    target = root.joinpath(*parts)
    current = target
    while current != root:
        reparse = os.name == "nt" and current.exists() and bool(current.stat().st_file_attributes & 0x400)
        if current.is_symlink() or reparse:
            raise ValueError("Links and reparse points are not allowed")
        current = current.parent
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError("File is outside the workspace")
    if target.exists() and (not target.is_file() or target.stat().st_nlink != 1):
        raise ValueError("Only ordinary, unlinked files are allowed")
    return target
