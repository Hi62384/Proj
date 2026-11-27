"""Move active projects directly beneath niches and adopt the six-phase workflow.

The migration is explicit, idempotent and local. It never changes historical
archives or resets completed work. A byte-for-byte record backup is kept outside
the public index before changes, and validation failure rolls back the move.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from business_portfolio.tools import build_browser
from portfolio_manager.project_lifecycle import _atomic_text, _single_writer
from portfolio_manager.project_management import _local_folder


OLD_PHASES = {"working_phase_2": "working_phase_4",
              "working_phase_3": "working_phase_2",
              "working_phase_4": "working_phase_5", "complete": "complete"}


def _plan_text(metadata: dict, previous_phase: str) -> str:
    name = metadata["title"]
    return f"""

## Current six-phase delivery plan

This project now uses the six-phase workflow. Its prior `{previous_phase}` was
mapped to `{metadata['project_phase']}` to preserve its actual stage of work.
Earlier phase numbers in the dated record above describe the former workflow;
they are history, not instructions to skip current research or repeat completed work.
The project remains **{name}** with the same ID, artifacts, evidence and permissions.
Migration is not approval of any unverified research, publication or marketing. Historical paths inside preserved work evidence may still name the old `projects/` container; resolve artifacts from the current project folder and repair only active path references when resuming, without changing historical evidence.

Target the whole product/release/marketing cycle to **2 days–3 weeks**. Reuse the
existing work. Before expanding scope, estimate the remaining time across all
phases; prioritize compatible ports and channels that fit this total window.
Record researched exclusions, blockers and any necessary owner scope decision.
Do not invent progress, drop a viable selected platform silently, or leave an
unbounded maintenance/marketing task as a completion requirement.

### Phase 1 — Product research and specification

- [ ] Reconcile the existing buyer, problem, differentiation, price, costs, rights,
  detailed product specification and acceptance tests with current evidence.
- [ ] Recheck material risks. If the idea is sound and only cosmetic changes remain,
  record “Good to go”; no forced rewrite or new idea is required.

### Phase 2 — Release platform and compatibility research

- [ ] Research all appropriate direct and adjacent release platforms; document
  eligibility, policies, costs, required formats, submission steps and sources.
- [ ] Update the Phase 1 specification with a compatible version and acceptance
  tests for every selected feasible platform; keep excluded/deferred options with
  reasons and respect the total 2–21 day delivery window.
- [ ] Independently recheck the release plan before relying on it for execution.

### Phase 3 — Marketing research

- [ ] Research suitable advertising/discovery platforms and non-platform tactics,
  audiences, positioning, search, demos, content, communities, timing and measurement.
- [ ] Save the concrete bounded marketing plan, dependencies, rules, sources and
  an independent recheck; update earlier requirements only where necessary.

### Phase 4 — Build and test

- [ ] Continue from the completed work and actual remaining checklist above;
  reconcile missing research first, then build, port, test and package every
  selected compatible version. Assign an appropriate product title without
  changing the stable ID or discarding the existing work directory.
- [ ] Record acceptance evidence and advance to Phase 5 with the lifecycle CLI
  using `--actor codex --evidence`, then stop at that handoff for the next prompt.

### Phase 5 — Release

- [ ] Execute the researched release plan on each selected feasible platform
  within the current permissions; record actual live/submission/download URLs,
  access, versions and verification. Keep outstanding approvals explicitly blocked.
- [ ] When release work is verified, advance to Phase 6 using
  `--actor codex --evidence`; wait for the Phase 6 prompt before marketing execution.

### Phase 6 — Marketing and completion

- [ ] Execute the bounded researched marketing plan and verify the actual
  placements and relevant links. Preserve costs, results and evidence limits.
- [ ] Mark Complete only after verified release and marketing evidence, with a
  factual description and live release/access and marketing URLs in the receipt.
  Completion does not establish sales or profit.

### Checkpoints and important data

At every execution checkpoint write and report `Phase N completion estimate: X% (best guess)`
for N=4, 5 or 6, explaining completed work, remaining work, blockers,
tests and the next action. Preserve all important non-secret facts, decisions,
identifiers, artifact locations and URLs in this project file as work happens.
Maintain an **Important URLs** ledger for source/edit/admin/build/upload/live/
purchase/download/demo/marketing/analytics/support locations, with purpose,
version, access/status and verification date. Keep replaced links as history.
Never put passwords, access tokens or private customer/payment information here.
"""


def migrate(repo: Path, *, rebuild: bool = True) -> list[dict]:
    repo = Path(repo).resolve(strict=True)
    portfolio = repo / "business_portfolio"
    with _single_writer(portfolio):
        data = build_browser.load_portfolio(portfolio)
        plans = []
        for row in data["records"]:
            old = portfolio / row["path"]
            niche = build_browser.project_niche_folder(old)
            if old.name == "project.md":
                new = niche / old.parent.name / "project.md"
            else:
                new = niche / old.stem / "project.md"
            if row.get("workflow_version") in (2, 3) and old == new:
                continue
            if old != new and new.parent.exists():
                raise ValueError(f"Migration destination already exists: {new.parent}")
            original = old.read_bytes()
            meta, _ = build_browser.parse_project(original.decode("utf-8"), str(old))
            old_phase = meta.get("project_phase", "working_phase_2")
            if meta.get("workflow_version") not in (2, 3) and old_phase not in OLD_PHASES:
                raise ValueError(f"Unknown previous workflow phase: {old_phase}")
            body = original.decode("utf-8").replace("\r\n", "\n").split("\n---\n", 1)[1]
            if meta.get("workflow_version") not in (2, 3):
                meta["project_phase"] = OLD_PHASES[old_phase]
                meta["workflow_version"] = 2
                meta["workflow_migration"] = {
                    "previous_project_phase": old_phase,
                    "previous_record_path": old.relative_to(repo).as_posix(),
                    "migrated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "research_approval_inferred": False,
                }
                meta.setdefault("research_verification", {
                    "phase_1": "unreviewed", "phase_2": "unreviewed", "phase_3": "unreviewed"})
                meta.setdefault("delivery_window_days", {"minimum": 2, "maximum": 21})
                body = body.rstrip() + _plan_text(meta, old_phase)
            plans.append({"id": meta["id"], "old": old, "new": new, "original": original,
                          "meta": meta, "body": body, "moved": False, "touched": False})
        # Correct references to actual moved paths, preserving dated text and IDs.
        replacements = [(p["old"].parent.relative_to(repo).as_posix(),
                         p["new"].parent.relative_to(repo).as_posix())
                        for p in plans if p["old"].name == "project.md" and p["old"] != p["new"]]
        def replace_refs(value):
            if isinstance(value, str):
                for source, target in replacements:
                    value = value.replace(source + "/", target + "/")
                return value
            if isinstance(value, list):
                return [replace_refs(item) for item in value]
            if isinstance(value, dict):
                return {key: item if key == "workflow_migration" else replace_refs(item)
                        for key, item in value.items()}
            return value
        receipts = []
        generated = {portfolio / name: (portfolio / name).read_bytes()
                     if (portfolio / name).is_file() else None
                     for name in ("PROJECT_INDEX.json", "PROJECT_BROWSER.html")} if rebuild else {}
        try:
            for plan in plans:
                old, new = plan["old"], plan["new"]
                original = plan["original"]
                if old.read_bytes() != original:
                    raise ValueError("Project changed while migration was being planned.")
                digest = hashlib.sha256(original).hexdigest()
                backup = _local_folder(portfolio, "workflow_migration", plan["id"]) / (digest + ".md")
                if backup.exists() or backup.is_symlink():
                    if (not backup.is_file() or build_browser.linked_input(backup) or
                            backup.read_bytes() != original):
                        raise ValueError("Migration backup is unsafe or differs from the original record.")
                else:
                    with backup.open("xb") as out:
                        out.write(original)
                plan["touched"] = True
                if old != new:
                    if old.name == "project.md":
                        os.replace(old.parent, new.parent)
                    else:
                        new.parent.mkdir()
                        (new.parent / "work").mkdir()
                        (new.parent / "work" / ".gitkeep").touch()
                        os.replace(old, new)
                    plan["moved"] = True
                contents = "---\n" + json.dumps(replace_refs(plan["meta"]), ensure_ascii=False, indent=2) + "\n---\n" + replace_refs(plan["body"])
                _atomic_text(new, contents)
                receipt = portfolio / "completed_projects" / (plan["id"] + ".json")
                if receipt.exists() and old != new:
                    raw = receipt.read_bytes()
                    entry = json.loads(raw)
                    if entry.get("source_project") == old.relative_to(repo).as_posix():
                        receipts.append((receipt, raw))
                        entry["source_project"] = new.relative_to(repo).as_posix()
                        _atomic_text(receipt, json.dumps(entry, ensure_ascii=False, indent=2) + "\n")
            build_browser.load_portfolio(portfolio)
            if rebuild:
                build_browser.build(portfolio)
        except BaseException:
            for receipt, raw in reversed(receipts):
                receipt.write_bytes(raw)
            for plan in reversed(plans):
                if not plan["touched"]:
                    continue
                old, new = plan["old"], plan["new"]
                if plan["moved"]:
                    if old.name == "project.md":
                        os.replace(new.parent, old.parent)
                    else:
                        os.replace(new, old)
                        (new.parent / "work" / ".gitkeep").unlink()
                        (new.parent / "work").rmdir()
                        new.parent.rmdir()
                if old.exists():
                    old.write_bytes(plan["original"])
            for path, content in generated.items():
                if content is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_bytes(content)
            raise
        for plan in plans:
            container = plan["old"].parent.parent if plan["old"].name == "project.md" else plan["old"].parent
            if container.name == "projects" and container.is_dir() and not any(container.iterdir()):
                container.rmdir()
        for container in (portfolio / "niches").rglob("projects"):
            if container.is_dir() and (container.parent / "NICHE.json").is_file():
                children = list(container.iterdir())
                if all(child.name == ".gitkeep" and child.is_file() and not child.is_symlink()
                       for child in children):
                    for child in children:
                        child.unlink()
                    container.rmdir()
        return [{"id": p["id"], "from": p["old"].relative_to(repo).as_posix(),
                 "to": p["new"].relative_to(repo).as_posix(),
                 "project_phase": p["meta"]["project_phase"]} for p in plans]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--no-rebuild", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(migrate(args.repo, rebuild=not args.no_rebuild), indent=2))


if __name__ == "__main__":
    main()
