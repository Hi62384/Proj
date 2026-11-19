"""Create an unpublished, non-overwriting local review directory with hashes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "project.godot", "README.md", "API.md", "COMPATIBILITY.md", "VISUAL_QA.md", "TEST_EVIDENCE.md",
    "RELEASE_CHECKLIST.md", "SUPPORT_DRAFT.md", "STOREFRONT_DRAFT.md", "PROVENANCE_DRAFT.md",
]
DIRECTORIES = ["addons", "demo", "examples", "tests", "tools"]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python tools/stage_review.py review-candidate-NAME", file=sys.stderr)
        return 2
    name = sys.argv[1]
    if not name.startswith("review-candidate-") or not all(c.isascii() and (c.isalnum() or c in "-_") for c in name):
        raise SystemExit("Destination must be a simple review-candidate-NAME within the project")
    target = (ROOT / name).resolve()
    if target.parent != ROOT or target.exists():
        raise SystemExit("Destination is outside the project or already exists; nothing overwritten")
    target.mkdir()
    for name in FILES:
        shutil.copy2(ROOT / name, target / name)
    for name in DIRECTORIES:
        shutil.copytree(ROOT / name, target / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".godot"))
    (target / "REVIEW_ONLY.txt").write_text(
        "Unpublished development snapshot for local review only. Not a licensed or approved release.\n"
        "Complete RELEASE_CHECKLIST.md and obtain separate owner approval before publication or spending.\n",
        encoding="utf-8",
    )
    entries = []
    for path in sorted(target.rglob("*")):
        if path.is_file():
            entries.append({"path": path.relative_to(target).as_posix(), "bytes": path.stat().st_size,
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (target / "REVIEW_MANIFEST.json").write_text(json.dumps({"status": "unpublished_review_only", "files": entries}, indent=2) + "\n", encoding="utf-8")
    print(f"Staged {len(entries)} files for local review at {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
