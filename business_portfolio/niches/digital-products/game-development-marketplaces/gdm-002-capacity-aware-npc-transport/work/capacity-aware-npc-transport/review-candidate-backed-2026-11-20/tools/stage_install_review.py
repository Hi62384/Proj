"""Create a local install-review folder; this is not a licensed release."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
GUIDES = ("API.md", "COMPATIBILITY.md", "SUPPORT_DRAFT.md", "PROVENANCE_DRAFT.md")


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].startswith("install-review-") or not all(
        c.isascii() and (c.isalnum() or c in "-_") for c in sys.argv[1]
    ):
        raise SystemExit("Usage: python tools/stage_install_review.py install-review-NAME")
    target = (ROOT / sys.argv[1]).resolve()
    if target.parent != ROOT or target.exists():
        raise SystemExit("Destination already exists or is outside the project")
    addon = ROOT / "addons" / "transit_coordinator"
    if not addon.is_dir() or addon.is_symlink() or any(p.is_symlink() for p in addon.rglob("*")):
        raise SystemExit("Add-on missing or contains a symbolic link")
    if any(not (ROOT / name).is_file() or (ROOT / name).is_symlink() for name in GUIDES):
        raise SystemExit("A required guide is missing or is a symbolic link")
    target.mkdir()
    shutil.copytree(addon, target / "addons" / "transit_coordinator",
                    ignore=shutil.ignore_patterns(".godot", "__pycache__", "*.pyc", "*.uid"))
    for name in GUIDES:
        shutil.copy2(ROOT / name, target / name)
    (target / "README.md").write_text(
        "# Local add-on install review\n\n"
        "Copy `addons/transit_coordinator` into a Godot 4 project's `addons` folder. "
        "See `API.md` for configuration, movement callbacks and trusted snapshot handling.\n\n"
        "This folder omits the development demo, examples, tests, engine and research. "
        "References to them in the copied guides describe the broader development project. "
        "The support and provenance documents are drafts. This review copy has no approved license "
        "and is not authorized for distribution.\n",
        encoding="utf-8",
    )
    (target / "LOCAL_REVIEW_ONLY.txt").write_text(
        "Unpublished local install review. No license or distribution approval has been granted.\n"
        "Examples, demo, tests, engine binaries and research are not included in this folder.\n"
        "Some guides reference the broader development project and support terms are a draft.\n",
        encoding="utf-8",
    )
    entries = []
    for path in sorted(target.rglob("*")):
        if path.is_file():
            entries.append({"path": path.relative_to(target).as_posix(), "bytes": path.stat().st_size,
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (target / "MANIFEST.json").write_text(json.dumps({"status": "local_review_only", "files": entries}, indent=2) + "\n", encoding="utf-8")
    print(f"Staged {len(entries)} local install-review files at {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
