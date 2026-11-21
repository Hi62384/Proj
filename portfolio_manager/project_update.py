"""Safely import a ChatGPT Phase 3a/3b ADDITIVE update to one selected project.

No release, publication or marketing actions happen here. The original Markdown
body and protected metadata must be preserved, and the source must match the
precise project snapshot passed to ChatGPT.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from business_portfolio.tools import build_browser
from .project_lifecycle import PHASE_3, PHASE_4, _atomic_text, _single_writer, project_phase, record_path


MAX_UPDATE_BYTES = 5_000_000
EDITABLE_FIELDS = {
    "next_action", "last_reviewed", "phase3_plan_status",
    "phase3_validation_status", "phase3_update_base_sha256",
}


def snapshot_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _body(raw: str) -> str:
    raw = raw.replace("\r\n", "\n")
    _, separator, body = raw.partition("\n---\n")
    if not separator:
        raise ValueError("The project Markdown has invalid JSON frontmatter.")
    return body


def replace_project_from_file(repo: Path, selection: str, source: str | Path) -> dict:
    """Validate lineage, safely back up, then atomically update the exact record.

    A researched 3a plan stays in Phase 3. A separately appended and explicitly
    approved 3b validation advances the project to Phase 4. Unapproved reviews
    remain in Phase 3 for further research.
    """
    repo = Path(repo).resolve(strict=True)
    target = record_path(repo, selection)
    source = Path(source)
    if source.suffix.lower() != ".md" or not source.is_file() or source.is_symlink():
        raise ValueError("Drop one regular Markdown project update file.")
    if source.stat().st_size > MAX_UPDATE_BYTES:
        raise ValueError("The updated project file exceeds the 5 MB limit.")
    if source.resolve() == target.resolve():
        raise ValueError("Select an external updated project file, not the active project itself.")
    incoming = source.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    portfolio = repo / "business_portfolio"

    with _single_writer(target.parent):
        original = target.read_text(encoding="utf-8").replace("\r\n", "\n")
        old_meta, _ = build_browser.parse_project(original, str(target))
        new_meta, _ = build_browser.parse_project(incoming, str(source))
        if project_phase(old_meta) != PHASE_3:
            raise ValueError("Only a Phase 3 project accepts ChatGPT planning updates.")
        if new_meta.get("phase3_update_base_sha256") != snapshot_sha256(original):
            raise ValueError("This update is stale or belongs to another project snapshot. Copy a fresh Phase 3 prompt.")
        if old_meta.get("id") != new_meta.get("id") or old_meta.get("niche_id") != new_meta.get("niche_id"):
            raise ValueError("The updated project ID or niche does not match the selected project.")
        for key, value in old_meta.items():
            if key not in new_meta:
                raise ValueError(f"The update removed existing project metadata: {key}.")
            if key not in EDITABLE_FIELDS and new_meta[key] != value:
                raise ValueError(f"The update modified protected project metadata: {key}.")
        for key in new_meta.keys() - old_meta.keys():
            if key not in EDITABLE_FIELDS:
                raise ValueError(f"The update added unsupported metadata: {key}. Keep research details in Markdown.")
        old_body, updated_body = _body(original), _body(incoming)
        if not updated_body.startswith(old_body) or len(updated_body) <= len(old_body):
            raise ValueError("The update must preserve the entire original Markdown body unchanged and append a new section.")
        appended = updated_body[len(old_body):]
        if not re.search(r"https?://\S+", appended):
            raise ValueError("The appended research must include direct source URLs.")
        if old_meta.get("phase3_plan_status") != "researched":
            if new_meta.get("phase3_plan_status") != "researched" or "## Phase 3a" not in appended:
                raise ValueError("First append a Phase 3a researched plan before validation.")
            if "phase3_validation_status" in new_meta:
                raise ValueError("Phase 3b approval must come from a subsequent independent update.")
            stage = "3a"
            new_meta["project_phase"] = PHASE_3
        else:
            if "## Phase 3b" not in appended:
                raise ValueError("Append a distinct Phase 3b independent validation section.")
            verdict = new_meta.get("phase3_validation_status")
            if verdict not in {"approved", "needs_revision"}:
                raise ValueError("Phase 3b must explicitly set approved or needs_revision.")
            if verdict == "approved" and "VERDICT: APPROVED" not in appended:
                raise ValueError("An approved Phase 3b update must contain the actual final approval verdict.")
            stage = "3b"
            new_meta["project_phase"] = PHASE_4 if verdict == "approved" else PHASE_3
        new_meta.pop("phase3_update_base_sha256", None)
        new_meta["last_reviewed"] = datetime.now(timezone.utc).date().isoformat()
        contents = "---\n" + json.dumps(new_meta, ensure_ascii=False, indent=2) + "\n---\n" + updated_body
        if target.read_text(encoding="utf-8").replace("\r\n", "\n") != original:
            raise ValueError("The project was edited concurrently; copy a fresh prompt.")

        # Preserve the pre-update version outside the public project index.
        backup_dir = portfolio / ".local" / "phase3_backups" / str(old_meta["id"])
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / (snapshot_sha256(original) + ".md")
        if not backup.exists():
            with backup.open("x", encoding="utf-8", newline="\n") as out:
                out.write(original)
        _atomic_text(target, contents)
        try:
            build_browser.build(portfolio)
        except Exception:
            _atomic_text(target, original)
            try:
                build_browser.build(portfolio)
            except Exception:
                # Preserve the original exception; the prior record is restored.
                pass
            raise

        return {
            "id": old_meta["id"],
            "import_stage": stage,
            "project_phase": new_meta["project_phase"],
            "backup": str(backup),
        }
