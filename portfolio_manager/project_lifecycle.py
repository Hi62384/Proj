"""Persistent project-phase transitions and independent completion receipts.

Use through normal Codex chats, not automatic background execution. This CLI
changes local files only. It never publishes, pays, advertises or pushes to GitHub.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit

from business_portfolio.tools.build_browser import parse_project, project_record_path
from .workspace import context_path

PHASE_2 = "working_phase_2"
PHASE_3 = "working_phase_3"
PHASE_4 = "working_phase_4"
COMPLETE = "complete"
PHASES = (PHASE_2, PHASE_3, PHASE_4, COMPLETE)


def project_phase(metadata: dict) -> str:
    """Legacy canonical records enter Phase 2 without rewriting history."""
    value = metadata.get("project_phase", PHASE_2)
    if value not in PHASES:
        raise ValueError("Invalid project_phase in project record.")
    return value


def record_path(repo: Path, selection: str | Path) -> Path:
    repo = Path(repo).resolve(strict=True)
    candidate = context_path(repo, selection)
    if candidate.is_dir():
        candidate = context_path(repo, candidate / "project.md")
    if not candidate.is_file() or not project_record_path(candidate):
        raise ValueError("Select a canonical project.md or legacy projects/*.md record.")
    if not candidate.is_relative_to(repo / "business_portfolio" / "niches"):
        raise ValueError("Project record must be inside the active business niches.")
    return candidate


def _url(value: str) -> str:
    if not isinstance(value, str) or len(value) > 2048 or any(c.isspace() for c in value):
        raise ValueError("Links must be public HTTP(S) URLs without whitespace.")
    parts = urlsplit(value)
    if parts.scheme not in {"https", "http"} or not parts.hostname or parts.username or parts.password:
        raise ValueError("Links must use HTTP(S) without embedded credentials.")
    return value


def _urls(values) -> list[str]:
    result = []
    for value in values:
        cleaned = _url(value)
        if cleaned not in result:
            result.append(cleaned)
    return result


@contextmanager
def _single_writer(folder: Path):
    lock = folder / ".project-phase.lock"
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise ValueError("Project phase is being updated by another chat.") from error
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink(missing_ok=True)


def _atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    candidate = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n",
                                         dir=path.parent, delete=False) as stream:
            candidate = Path(stream.name)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(candidate, path)
    finally:
        if candidate is not None:
            candidate.unlink(missing_ok=True)


def read_completions(repo: Path) -> list[dict]:
    """Snapshots are independent of the original project directory."""
    base = Path(repo).resolve() / "business_portfolio" / "completed_projects"
    results = []
    if not base.is_dir():
        return results
    for path in sorted(base.glob("*.json")):
        if path.is_symlink() or not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if (not isinstance(data, dict) or data.get("id") != path.stem or
                    data.get("project_phase") != COMPLETE or not isinstance(data.get("title"), str)):
                continue
            results.append({**data, "path": path.as_posix()})
        except (OSError, ValueError, TypeError):
            continue
    return results


def set_phase(repo: Path, selection: str | Path, phase: str, *,
              description: str | None = None, sale_urls=(),
              marketing_urls=(), other_urls=()) -> dict:
    """Change project phase; completion stores a receipt and demotion revokes it."""
    if phase not in PHASES:
        raise ValueError("Choose working_phase_2, working_phase_3, working_phase_4, or complete.")
    repo = Path(repo).resolve(strict=True)
    path = record_path(repo, selection)
    with _single_writer(path.parent):
        raw = path.read_text(encoding="utf-8")
        meta, _ = parse_project(raw, str(path))
        old = project_phase(meta)
        allowed = {PHASE_2: {PHASE_2, PHASE_3},
                   PHASE_3: {PHASE_2, PHASE_3, PHASE_4},
                   PHASE_4: {PHASE_2, PHASE_3, PHASE_4, COMPLETE},
                   COMPLETE: {PHASE_2, PHASE_3, PHASE_4, COMPLETE}}
        if phase not in allowed[old]:
            raise ValueError(f"Invalid phase transition from {old} to {phase}.")
        completion = repo / "business_portfolio" / "completed_projects" / (meta["id"] + ".json")
        if old == COMPLETE and phase != COMPLETE:
            # A demoted project must no longer appear in Completed Projects.
            # Only revoke a receipt that belongs to the exact canonical record.
            if not completion.is_file() or completion.is_symlink():
                raise ValueError("Completion receipt is missing or unsafe; cannot demote.")
            existing = json.loads(completion.read_text(encoding="utf-8"))
            if (existing.get("id") != meta["id"] or
                    existing.get("source_project") != path.relative_to(repo).as_posix() or
                    existing.get("project_phase") != COMPLETE):
                raise ValueError("Completion receipt does not match the selected project.")
        if phase == COMPLETE:
            if old not in {PHASE_4, COMPLETE}:
                raise ValueError("Completion requires verified Phase 4 execution.")
            if not isinstance(description, str) or not description.strip():
                raise ValueError("Completion requires a short, factual project description.")
            sale = _urls(sale_urls)
            marketing = _urls(marketing_urls)
            other = _urls(other_urls)
            if not sale and not other:
                raise ValueError("Completion requires at least one verified sale, download or delivery link.")
            if not marketing:
                raise ValueError("Completion requires at least one verified marketing link.")
            if completion.exists():
                raise ValueError("Completed project already has a snapshot; edit its JSON on disk if necessary.")
            receipt = {
                "schema_version": 1,
                "id": meta["id"],
                "title": meta["title"],
                "description": description.strip()[:2000],
                "project_phase": COMPLETE,
                "completed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "sale_links": sale,
                "marketing_links": marketing,
                "other_links": other,
                "source_project": path.relative_to(repo).as_posix(),
            }
        else:
            receipt = None
        meta["project_phase"] = phase
        before, sep, body = raw.replace("\r\n", "\n").partition("\n---\n")
        if not sep:
            raise ValueError("Project frontmatter is malformed.")
        updated = "---\n" + json.dumps(meta, ensure_ascii=False, indent=2) + "\n---\n" + body
        if path.read_text(encoding="utf-8") != raw:
            raise ValueError("Project was edited by another chat; reload before changing phase.")
        if receipt is not None:
            # Create snapshot first, never overwrite an existing completed receipt.
            completion.parent.mkdir(parents=True, exist_ok=True)
            with completion.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
        try:
            _atomic_text(path, updated)
            if old == COMPLETE and phase != COMPLETE:
                try:
                    completion.unlink()
                except OSError:
                    _atomic_text(path, raw)
                    raise
        except BaseException:
            if receipt is not None:
                completion.unlink(missing_ok=True)
            raise
        return {"id": meta["id"], "project_phase": phase, "snapshot": str(completion) if receipt else None}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("set-phase", "list-completed"))
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--project", help="project.md path (or its project folder) relative to the checkout")
    parser.add_argument("--phase", choices=PHASES)
    parser.add_argument("--description", help="Required factual description when completing")
    parser.add_argument("--sale-url", action="append", default=[], help="Public store or purchase URL")
    parser.add_argument("--marketing-url", action="append", default=[], help="Public promotion URL")
    parser.add_argument("--other-url", action="append", default=[], help="Other relevant public URL")
    args = parser.parse_args(argv)
    try:
        if args.command == "list-completed":
            result = read_completions(args.repo)
        elif not args.project or not args.phase:
            parser.error("set-phase requires --project and --phase")
        else:
            result = set_phase(args.repo, args.project, args.phase,
                               description=args.description, sale_urls=args.sale_url,
                               marketing_urls=args.marketing_url, other_urls=args.other_url)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as error:
        parser.exit(1, f"Project phase update failed: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
