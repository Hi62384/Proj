"""Replace selected Phase 1–3 research records from pasted text or a file.

Planning sections may be rewritten and reorganized. Stable identity, phase and
existing operational/permission metadata remain protected; prompts require body
facts and URLs to be retained and exact-byte backups support recovery. A paste
never advances a phase: the owner controls the research handoffs explicitly.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re

from business_portfolio.tools import build_browser
from .project_lifecycle import _single_writer, project_phase, record_path
from .project_management import (_atomic_bytes, _backup_record, _record_text,
                                 _restore_views, _title, _view_snapshot)


MAX_UPDATE_BYTES = 5_000_000
EDITABLE_FIELDS = {
    'title', 'draft', 'record_type', 'priority', 'next_action', 'last_reviewed',
    'evidence_basis', 'source_ids', 'research_verification', 'research_verdict',
    'delivery_window_days', 'platforms_proposed',
}
TRANSPORT_FIELD = 'project_update_base_sha256'


def snapshot_sha256(text: str) -> str:
    return hashlib.sha256(text.replace('\r\n', '\n').encode('utf-8')).hexdigest()


def clean_project_text(text: str) -> str:
    if not isinstance(text, str) or len(text.encode('utf-8')) > MAX_UPDATE_BYTES:
        raise ValueError('The project text exceeds the 5 MB limit.')
    text = text.lstrip('\ufeff').replace('\r\n', '\n').strip()
    first, separator, remainder = text.partition('\n')
    match = re.fullmatch(r'(`{3,}|~{3,})(?:markdown|md|text|plaintext)?\s*', first, flags=re.I)
    if match:
        if not separator or not remainder.rstrip().endswith('\n' + match.group(1)):
            raise ValueError('Copy the complete project code block, including its closing fence.')
        text = remainder.rstrip()[:-(len(match.group(1)) + 1)].strip()
    if not text:
        raise ValueError('Paste the complete project text, including its JSON metadata.')
    return text + '\n'


def replace_project_text(repo, selection, text: str, *, expected_sha256: str | None = None) -> dict:
    """Validate and back up a same-phase replacement, then rebuild atomically."""
    repo = Path(repo).resolve(strict=True)
    portfolio = repo / 'business_portfolio'
    incoming = clean_project_text(text)
    with _single_writer(portfolio):
        target = record_path(repo, selection)
        original_bytes = target.read_bytes()
        original = original_bytes.decode('utf-8-sig').replace('\r\n', '\n')
        old, _ = build_browser.parse_project(original, str(target))
        updated, body = build_browser.parse_project(incoming, 'Pasted project')
        phase = project_phase(old)
        if phase not in {f'working_phase_{i}' for i in range(1, 4)}:
            raise ValueError('Pasting research text is available only in Phases 1–3.')
        digest = snapshot_sha256(original)
        supplied_digest = updated.pop(TRANSPORT_FIELD, None)
        if ((expected_sha256 is not None and expected_sha256 != digest) or
                (supplied_digest is not None and supplied_digest != digest)):
            raise ValueError('This update is stale. Copy a fresh prompt or reopen Paste project text.')
        for key, value in old.items():
            if key not in updated:
                raise ValueError(f'The pasted record removed existing metadata: {key}.')
            if key not in EDITABLE_FIELDS and updated[key] != value:
                raise ValueError(f'The pasted record changed protected metadata: {key}.')
        for key in updated.keys() - old.keys():
            if key not in EDITABLE_FIELDS:
                raise ValueError(f'Keep new planning details in Markdown; unsupported metadata: {key}.')
        if updated.get('project_phase') != phase:
            raise ValueError('Keep the current project phase; advance it separately in Portfolio Manager.')
        if (not isinstance(updated.get('source_ids'), list) or
                any(not isinstance(source, str) for source in updated['source_ids']) or
                not set(old.get('source_ids', [])).issubset(updated['source_ids'])):
            raise ValueError('Keep the existing registered source IDs in the project.')
        if updated.get('delivery_window_days') not in (None, {'minimum': 2, 'maximum': 21}):
            raise ValueError('Keep the overall delivery window at 2 days to 3 weeks.')
        if 'platforms_proposed' in updated and (not isinstance(updated['platforms_proposed'], list) or
                any(not isinstance(value, str) or not value.strip() for value in updated['platforms_proposed'])):
            raise ValueError('Proposed platforms must be a list of platform names.')
        updated['title'] = _title(updated.get('title'))
        if 'draft' in updated and not isinstance(updated['draft'], bool):
            raise ValueError('draft must be true or false.')
        if not body.strip():
            raise ValueError('The project text must contain its research, plans and next action.')
        if (updated['title'].strip().casefold() != 'empty project' and
                updated.get('record_type') != 'empty_project' and len(body.strip()) >= 80):
            updated['draft'] = False
        updated['last_reviewed'] = datetime.now(timezone.utc).date().isoformat()
        contents = _record_text(updated, body).encode('utf-8')
        views = _view_snapshot(portfolio)
        backup = _backup_record(portfolio, old['id'], original_bytes)
        if target.read_bytes() != original_bytes:
            raise ValueError('The project changed while the update was being prepared. Reopen Paste project text.')
        _atomic_bytes(target, contents)
        try:
            build_browser.build(portfolio)
        except Exception:
            _atomic_bytes(target, original_bytes)
            _restore_views(views)
            raise
        return {'id': old['id'], 'path': target.relative_to(repo).as_posix(),
                'project_phase': phase, 'backup': str(backup)}


def replace_project_from_file(repo, selection, source, *, expected_sha256: str | None = None) -> dict:
    """Optional file-drop equivalent of Paste project text; preserve work/."""
    repo = Path(repo).resolve(strict=True)
    target = record_path(repo, selection)
    source = Path(source)
    if (source.suffix.lower() != '.md' or not source.is_file() or
            build_browser.linked_input(source)):
        raise ValueError('Drop one regular Markdown project file.')
    if source.stat().st_size > MAX_UPDATE_BYTES:
        raise ValueError('The project file exceeds the 5 MB limit.')
    if source.resolve() == target.resolve():
        raise ValueError('Drop an external updated file, not the selected project itself.')
    return replace_project_text(repo, selection, source.read_text(encoding='utf-8-sig'),
                                expected_sha256=expected_sha256)
