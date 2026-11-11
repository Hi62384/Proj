"""AWA-005 fictional field-map proof. Pure transformation; no CRM/network adapter.

Run from the repository: python business_portfolio/tools/awa005_mapping_demo.py
The report is printed only. Redirect it explicitly to keep observed evidence.
"""
from __future__ import annotations
import copy
from datetime import date
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def valid_value(value, rule):
    kind = rule['type']
    if kind == 'text':
        return type(value) is str
    if kind == 'integer':
        return type(value) is int and value >= 0
    if kind == 'boolean':
        return type(value) is bool
    if kind == 'picklist':
        return type(value) is str and value in rule['options']
    if kind == 'multi_picklist':
        return (type(value) is list and all(type(v) is str and v in rule['options'] for v in value)
                and len(value) == len(set(value)))
    if kind == 'date':
        if type(value) is not str:
            return False
        try:
            return date.fromisoformat(value).isoformat() == value
        except ValueError:
            return False
    return False


def map_fields(payload, mapping):
    """Return proposed patch/parity, or hold the whole event for review.

    Missing/null optional fields omit a write. Blank strings are held, never
    silently cleared. No truthiness fallback, coercion, alias inference or I/O.
    A label change is harmless when its stable ID is unchanged. IDs must match.
    """
    rules = mapping['fields']
    if not 1 <= len(rules) <= 15:
        raise ValueError('One pair, at most 15 fields')
    sources = [r['source_id'] for r in rules]
    targets = [r['target'] for r in rules]
    if len(set(sources)) != len(sources) or len(set(targets)) != len(targets):
        raise ValueError('Ambiguous map')
    if mapping.get('pair') != 'fictional-form-to-fictional-contact':
        raise ValueError('Unexpected source/destination pair')
    errors, by_id, rows, patch = [], {}, [], {}
    questions = payload.get('questions') if isinstance(payload, dict) else None
    if not isinstance(questions, list):
        questions = []
        errors.append('questions_not_array')
    for q in questions:
        if not isinstance(q, dict) or type(q.get('id')) is not str or 'value' not in q:
            errors.append('malformed_question')
            continue
        if q['id'] in by_id:
            errors.append('duplicate_source_id:' + q['id'])
        by_id[q['id']] = q['value']
    for key in sorted(set(by_id) - set(sources)):
        errors.append('unmapped_source_id:' + key)
    for rule in rules:
        key, target = rule['source_id'], rule['target']
        row = {'source_id': key, 'target': target}
        if key not in by_id:
            state = 'missing_required' if rule['required'] else 'missing_optional_omitted'
        else:
            value = by_id[key]
            row['value'] = copy.deepcopy(value)
            if value is None:
                state = 'null_required' if rule['required'] else 'null_optional_omitted'
            elif type(value) is str and not value.strip():
                state = 'blank_requires_review'
            elif type(value) is list and not value:
                state = 'empty_collection_requires_review'
            elif not valid_value(value, rule):
                state = 'invalid_type_or_option'
            else:
                state = 'mapped'
                patch[target] = copy.deepcopy(value)
        row['state'] = state
        rows.append(row)
        if state not in {'mapped', 'missing_optional_omitted', 'null_optional_omitted'}:
            errors.append(key + ':' + state)
    return {'mapping_version': mapping['version'], 'status': 'review' if errors else 'ready_local_only',
            'proposed_patch': {} if errors else patch, 'parity': rows, 'drift_alerts': errors,
            'external_writes': 0}


def run_cases(fixture):
    """Compare independently specified expected outputs, including exact JSON types."""
    reports = []
    for case in fixture['cases']:
        mapping = copy.deepcopy(fixture['mapping'])
        if case.get('rename_rule'):
            mapping['version'] = '1.1-fictional'
            mapping['fields'][1]['source_id'] = 'full_name_v2'
        payload = copy.deepcopy(fixture['sample'])
        for key in case.get('remove', []):
            payload['questions'] = [q for q in payload['questions'] if q['id'] != key]
        for key, value in case.get('set', {}).items():
            next(q for q in payload['questions'] if q['id'] == key)['value'] = value
        for old, new in case.get('rename_id', {}).items():
            next(q for q in payload['questions'] if q['id'] == old)['id'] = new
        if case.get('rename_label'):
            payload['questions'][1]['label'] = 'Changed display name'
        if case.get('reverse'):
            payload['questions'].reverse()
        payload['questions'].extend(copy.deepcopy(case.get('append', [])))
        before = copy.deepcopy(payload)
        result = map_fields(payload, mapping)
        expected_patch = {} if case['expected_status'] == 'review' else copy.deepcopy(fixture['expected_patch'])
        for key in case.get('omit_targets', []):
            expected_patch.pop(key)
        checks = {
            'status': result['status'] == case['expected_status'],
            'exact_patch_and_types': json.dumps(result['proposed_patch'], sort_keys=True, ensure_ascii=False)
                == json.dumps(expected_patch, sort_keys=True, ensure_ascii=False),
            'input_unchanged': payload == before,
            'no_external_writes': result['external_writes'] == 0,
            'all_fields_reported': len(result['parity']) == 15,
        }
        for key, state in case.get('expected_states', {}).items():
            checks['state:' + key] = any(r['source_id'] == key and r['state'] == state for r in result['parity'])
        reports.append({'id': case['id'], 'passed': all(checks.values()), 'checks': checks, **result})
    return {'purpose': 'Fictional deterministic transformation only; no live connector or customer acceptance.',
            'fixture_version': fixture['version'], 'cases_run': len(reports),
            'passed': sum(r['passed'] for r in reports), 'cases': reports,
            'never_run': ['CRM API writes/read-back', 'native connector import', 'auth/revocation',
                          'rate limits/retries', 'network partial failure/uncertain remote success',
                          'concurrency/idempotency', 'production rollback', 'customer acceptance']}


def main():
    fixture = json.loads((ROOT/'fixtures/awa005-field-mapping.json').read_text(encoding='utf-8'))
    report = run_cases(fixture)
    # ASCII JSON escapes preserve Unicode values on Windows legacy consoles too.
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report['passed'] == report['cases_run'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
