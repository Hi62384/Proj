"""Versioned phases; historic numeric identifiers keep their original meanings."""
from __future__ import annotations

import re

VERSION = 3
PHASE_1 = "working_phase_1"
PHASE_2 = "working_phase_2"
PHASE_3 = "working_phase_3"
PHASE_4 = "working_phase_4"
COMPLETE = "complete"
PHASES = (PHASE_1, PHASE_2, PHASE_3, PHASE_4, COMPLETE)
RESEARCH_KEYS = ("phase_1", "phase_2", "phase_3")  # product, release, marketing checks
LEGACY_V2 = {PHASE_1: PHASE_1, PHASE_2: PHASE_1, PHASE_3: PHASE_1,
             PHASE_4: PHASE_2, "working_phase_5": PHASE_3,
             "working_phase_6": PHASE_4, COMPLETE: COMPLETE}
LEGACY_V1 = {PHASE_1: PHASE_1, PHASE_2: PHASE_2, PHASE_3: PHASE_1,
             PHASE_4: PHASE_3, COMPLETE: COMPLETE}


def phase_of(meta: dict) -> str:
    version = meta.get("workflow_version", 1)
    raw = meta.get("project_phase", PHASE_1 if version in (2, VERSION) else PHASE_2)
    mapping = ({p: p for p in PHASES} if version == VERSION else
               LEGACY_V2 if version == 2 else LEGACY_V1 if version == 1 else {})
    if not isinstance(raw, str) or raw not in mapping:
        raise ValueError("Invalid project phase or workflow version.")
    return mapping[raw]


def upgrade_record(meta: dict, body: str) -> tuple[dict, str]:
    """Upgrade on save without inventing approval or overwriting old evidence."""
    phase = phase_of(meta)
    version = meta.get("workflow_version", 1)
    if version == VERSION:
        return meta, body
    old = meta.get("project_phase", PHASE_1 if version == 2 else PHASE_2)
    meta = dict(meta)
    meta.update(workflow_version=VERSION, project_phase=phase)
    meta["workflow_v3_migration"] = {
        "previous_workflow_version": version, "previous_project_phase": old,
        "research_approval_inferred": False,
    }
    meta.setdefault("research_verification", {key: "unreviewed" for key in RESEARCH_KEYS})
    body = body.rstrip() + (
        "\n\n## Four-phase workflow migration\n\n"
        f"Previous workflow v{version} phase {old} maps to {phase}. "
        "Historical phase references retain their original meanings. "
        "Current workflow: Phase 1 research (product, release, marketing); "
        "Phase 2 build; Phase 3 release; Phase 4 marketing. "
        "No research approval or execution progress is inferred. Preserve existing work; "
        "reconcile missing research and prerequisites before external actions.\n"
    )
    if phase in (PHASE_2, PHASE_3, PHASE_4):
        matches = re.findall(r"Phase\s*" + old[-1] +
                             r"\s*completion estimate:\s*(\d{1,3})\s*%", body, re.I)
        valid = [n for n in matches if int(n) <= 100]
        if valid:
            body += f"\nPhase {phase[-1]} completion estimate: {valid[-1]}% (best guess)\n"
    return meta, body
