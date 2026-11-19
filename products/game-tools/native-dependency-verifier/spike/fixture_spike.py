"""Compare the owned Godot fixture; not a general package or loader verifier.

The descriptor must use the exact fixture's simple release library and one-line
Windows dependency map. PE parsing is delegated to the companion .NET probe.
Run only against owned, trusted experiment directories.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

import godot_subset


def checked_path(path, *, file=False):
    """Reject links/reparse points in every existing path component."""
    path = path.absolute()
    for item in (path, *path.parents):
        metadata = item.lstat()
        attributes = getattr(metadata, 'st_file_attributes', 0)
        if stat.S_ISLNK(metadata.st_mode) or attributes & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400):
            raise ValueError('symlink or reparse point in input path')
    metadata = path.lstat()
    if file and (not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1):
        raise ValueError('input is not a single-link regular file')
    return path


def scan(probe, descriptor, package, safe_probe=None, custom_features=()):
    descriptor = checked_path(descriptor, file=True)
    package = checked_path(package)
    if descriptor.stat().st_size > 1024 * 1024:
        raise ValueError('fixture descriptor size limit exceeded')
    text = descriptor.read_text(encoding='utf-8-sig')
    sections = godot_subset.parse_sections(text)

    features = {'windows', 'release', 'x86_64'}
    inactive = {'debug', 'linux', 'macos', 'android', 'ios', 'web', 'x86_32', 'arm64', 'editor'}
    for tag in custom_features:
        if not re.fullmatch(r'[A-Za-z0-9_-]+', tag) or tag in features | inactive:
            raise ValueError('invalid or conflicting explicit custom feature: ' + tag)
        features.add(tag)

    def matches(key):
        tags = key.split('.')
        if len(tags) != len(set(tags)) or any(tag not in features | inactive for tag in tags):
            raise ValueError('unsupported or duplicate fixture feature tag: ' + key)
        return all(tag in features for tag in tags)

    eligible = [(key, path) for key, path in sections['libraries'] if matches(key)]
    if not eligible:
        raise ValueError('no supported release library entry')
    # In Godot 4.7.2 the matching library with the most tags wins; ties retain
    # the first entry. Only the explicit fixed feature set above is modeled.
    library_key, original_library = max(eligible, key=lambda item: len(item[0].split('.')))
    fixture_prefix = 'res://addons/fixture/bin/'

    def canonical_fixture_path(value):
        if not isinstance(value, str):
            raise ValueError('unsupported fixture library path')
        if value.startswith(fixture_prefix):
            name = value[len(fixture_prefix):]
        elif value.startswith('./bin/'):
            name = value[len('./bin/'):]
        else:
            raise ValueError('unsupported fixture library path')
        if '/' in name or '\\' in name or name in ('', '.', '..'):
            raise ValueError('unsupported fixture library path')
        return fixture_prefix + name

    library = canonical_fixture_path(original_library)
    selected = next(((key, value) for key, value in sections['dependencies'] if matches(key)), None)
    if selected is None or not isinstance(selected[1], dict):
        raise ValueError('no supported fixture dependency map')
    dependency_key, mapping = selected
    if any(not isinstance(dest, str) for dest in mapping.values()):
        raise ValueError('unsupported fixture dependency destination')
    pairs = [(canonical_fixture_path(path), path, dest) for path, dest in mapping.items()]
    destinations = {Path(canonical[6:]).name.casefold(): (original, dest)
                    for canonical, original, dest in pairs}
    if len(destinations) != len(pairs):
        raise ValueError('duplicate fixture dependency basename')
    source = checked_path(descriptor.parent / 'bin')
    if not source.is_dir() or not package.is_dir():
        raise ValueError('fixture source bin and package directory must exist')
    known = set()
    for index, item in enumerate(source.iterdir(), 1):
        if index > 1024:
            raise ValueError('fixture source entry limit exceeded')
        if item.suffix.lower() == '.dll':
            checked_path(item, file=True)
            if item.name.casefold() in known:
                raise ValueError('ambiguous source DLL basename')
            known.add(item.name.casefold())
    entries = []
    for index, item in enumerate(package.iterdir(), 1):
        if index > 1024:
            raise ValueError('fixture package entry limit exceeded')
        if item.suffix.lower() == '.dll':
            checked_path(item, file=True)
            entries.append(item)
            if len(entries) > 256:
                raise ValueError('fixture DLL count limit exceeded')
    files = {}
    for item in entries:
        if item.is_symlink() or item.name.casefold() in files:
            raise ValueError('symlink or ambiguous DLL in fixture package')
        files[item.name.casefold()] = item
    findings = []
    delayed = []
    seen = set()
    active_chain = set()
    cycles = []
    unknown = {'runtime dynamic loads', 'host and system DLL resolution', 'delay imports',
               'non-root search locations', 'general Godot feature selection and PCK mapping'}

    # Compare selected extension basenames for the observed flat staging case.
    # This remains limited to trusted projects with simple one-line descriptors.
    project = checked_path(descriptor.parent.parent.parent)
    if descriptor.parent.parent.name != 'addons':
        raise ValueError('unsupported fixture project layout')
    checked_path(project / 'project.godot', file=True)
    staged = {}
    stage_count = 0

    def register_staged(declared, destination, field, kind, normalized=None):
        nonlocal stage_count
        effective = declared if normalized is None else normalized
        if (not isinstance(effective, str) or not effective.startswith('res://addons/') or '\\' in effective
                or not isinstance(destination, str)):
            raise ValueError('unsupported fixture staging declaration')
        parts = effective[6:].split('/')
        if any(part in ('', '.', '..') or ':' in part for part in parts):
            raise ValueError('unsafe fixture staging path')
        if destination and not re.fullmatch(r'[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*', destination):
            raise ValueError('unsupported fixture staging destination')
        stage_count += 1
        if stage_count > 1024:
            raise ValueError('fixture staging declaration limit exceeded')
        key = (destination.casefold(), parts[-1].casefold())
        staged.setdefault(key, []).append((declared, destination, field, kind, project.joinpath(*parts)))

    main_field = descriptor.relative_to(project).as_posix()
    register_staged(original_library, '', main_field + ':libraries:' + library_key, 'library', library)
    for canonical, declared, destination in pairs:
        register_staged(declared, destination, main_field + ':dependencies:' + dependency_key, 'dependency', canonical)
    others = []
    root = checked_path(project / 'addons')
    total_entries = 0

    def fail_walk(error):
        raise error

    for current, directories, filenames in os.walk(root, followlinks=False, onerror=fail_walk):
        current = Path(current)
        if len(current.relative_to(root).parts) > 32:
            raise ValueError('fixture directory depth limit exceeded')
        if len(directories) + len(filenames) > 1024:
            raise ValueError('fixture directory entry limit exceeded')
        total_entries += len(directories) + len(filenames)
        if total_entries > 4096:
            raise ValueError('fixture project entry limit exceeded')
        for name in directories:
            checked_path(current / name)
        for name in filenames:
            if name.lower().endswith('.gdextension'):
                others.append(checked_path(current / name, file=True))
                if len(others) > 64:
                    raise ValueError('fixture descriptor count limit exceeded')
    for other in sorted(others, key=lambda path: str(path).casefold()):
        if other.resolve() == descriptor.resolve():
            continue
        if other.stat().st_size > 1024 * 1024:
            raise ValueError('fixture descriptor size limit exceeded')
        other_sections = godot_subset.parse_sections(other.read_text(encoding='utf-8-sig'))
        candidates = [(key, value) for key, value in other_sections['libraries'] if matches(key)]
        dependency_candidates = [(key, value) for key, value in other_sections['dependencies'] if matches(key)]
        if not candidates:
            raise ValueError('other fixture has no supported release library entry')
        other_key, other_library = max(candidates, key=lambda item: len(item[0].split('.')))
        if not isinstance(other_library, str) or not other_library.startswith('res://addons/') or '\\' in other_library:
            raise ValueError('unsupported other fixture library path')
        parts = other_library[6:].split('/')
        if any(part in ('', '.', '..') or ':' in part for part in parts):
            raise ValueError('unsafe other fixture library path')
        other_path = checked_path(project.joinpath(*parts), file=True)
        if not other_path.is_relative_to(project) or not other_path.is_file():
            raise ValueError('other fixture library missing or outside project')
        other_field = other.relative_to(project).as_posix()
        register_staged(other_library, '', other_field + ':libraries:' + other_key, 'library')

        if dependency_candidates:
            other_dependency_key, other_mapping = dependency_candidates[0]
            if not isinstance(other_mapping, dict):
                raise ValueError('unsupported other fixture dependency map')
            for other_declared, other_destination in other_mapping.items():
                register_staged(other_declared, other_destination,
                                other_field + ':dependencies:' + other_dependency_key, 'dependency')

    hashes = {}
    for (destination, _), candidates in sorted(staged.items()):
        unique_sources = {entry[0].casefold() for entry in candidates}
        if len(unique_sources) == 1 and destination == '' and candidates[0][4].name.casefold() in files:
            entry = candidates[0]
            staged_path = files[entry[4].name.casefold()]
            try:
                source_path = checked_path(entry[4], file=True)
            except FileNotFoundError:
                continue  # The selected source-library rule reports its own absence.
            if not source_path.is_relative_to(project):
                raise ValueError('fixture staged source outside project')
            if max(source_path.stat().st_size, staged_path.stat().st_size) > 64 * 1024 * 1024:
                raise ValueError('fixture staged file too large')
            source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
            staged_hash = hashlib.sha256(staged_path.read_bytes()).hexdigest()
            if source_hash != staged_hash:
                findings.append({'code': 'staged_content_differs', 'basename': entry[4].name,
                                 'severity': 'advisory',
                                 'checked_field': entry[2], 'declared_source': entry[0],
                                 'source_sha256': source_hash, 'staged_sha256': staged_hash,
                                 'confidence': 'bytes differ; signing or other transformations may be legitimate'})
        if len(candidates) < 2:
            continue
        for index, left in enumerate(candidates):
            for right in candidates[index + 1:]:
                if left[0].casefold() == right[0].casefold():
                    continue
                for entry in (left, right):
                    path = checked_path(entry[4], file=True)
                    if not path.is_relative_to(project) or path.stat().st_size > 64 * 1024 * 1024:
                        raise ValueError('fixture staged file outside scope or too large')
                    if path not in hashes:
                        hashes[path] = hashlib.sha256(path.read_bytes()).hexdigest()
                if hashes[left[4]] == hashes[right[4]]:
                    continue
                if len(findings) >= 256:
                    raise ValueError('fixture staging conflict limit exceeded')
                code = ('conflicting_staged_basename' if left[3] == right[3] == 'library' else
                        'conflicting_staged_dependency' if left[3] == right[3] == 'dependency' else
                        'conflicting_staged_binary')
                finding = {'code': code, 'basename': left[4].name,
                           'declarations': [left[0], right[0]], 'sha256': [hashes[left[4]], hashes[right[4]]],
                           'checked_fields': [left[2], right[2]],
                           'confidence': 'observed fixture staging; other export layouts unknown'}
                if code != 'conflicting_staged_basename':
                    finding['destination'] = left[1]
                findings.append(finding)

    def visit(name, chain):
        folded = name.casefold()
        chain = chain + [name]
        if folded not in files:
            if folded in known:
                declaration = destinations.get(folded)
                findings.append({'code': 'package_root_missing', 'chain': chain,
                                 'checked_field': (descriptor.name + ':libraries:' + library_key
                                                   if len(chain) == 1 else
                                                   descriptor.name + ':dependencies:' + dependency_key),
                                 'declared_source': (declaration[0] if declaration else
                                                     original_library if len(chain) == 1 else None),
                                 'declared_destination': declaration[1] if declaration else None,
                                 'confidence': 'package root only; host resolution unknown'})
            return
        if folded in active_chain:
            cycles.append({'chain': chain, 'status': 'static import cycle; runtime unknown'})
            return
        if folded in seen:
            return
        seen.add(folded)
        active_chain.add(folded)
        if len(seen) > 64:
            raise ValueError('fixture import graph limit exceeded')
        command = (['dotnet', str(safe_probe), str(package), files[folded].name, '--pe'] if safe_probe else
                   ['dotnet', str(probe), str(files[folded])])
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        if result.returncode:
            raise ValueError('PE inspection incomplete for ' + name)
        info = json.loads(result.stdout)
        if safe_probe:
            info = info['pe']
        if info['machine'] != '0x8664':
            findings.append({'code': 'wrong_architecture', 'chain': chain,
                             'actual': info['machine'], 'expected': '0x8664'})
        for child in sorted(info['delay_imports'], key=str.casefold):
            delayed.append({'chain': chain + [child], 'status': 'runtime-dependent unknown'})
        for child in sorted(info['imports'], key=str.casefold):
            visit(child, chain)
        active_chain.remove(folded)

    # This is the observed flat export convention for this fixture, not a
    # claim that all Godot exports use the same path transformation.
    library_name = library[len(fixture_prefix):]
    if library_name.casefold() not in known:
        findings.append({'code': 'source_library_missing', 'checked_field': descriptor.name + ':libraries:' + library_key,
                         'declared_source': original_library})
    else:
        visit(library_name, [])
    return {'schema_version': 1, 'scope': 'owned fixture; Windows x64 release only',
            'selected_library': {'field': descriptor.name + ':libraries:' + library_key,
                                 'source': original_library, 'normalized_source': library,
                                 'active_features': sorted(features)},
            'findings': findings, 'delay_imports': delayed, 'cycles': cycles,
            'unknown_checks': sorted(unknown)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('probe', type=Path)
    parser.add_argument('descriptor', type=Path)
    parser.add_argument('package', type=Path)
    parser.add_argument('safe_probe', type=Path, nargs='?')
    parser.add_argument('--feature', action='append', default=[], help='explicit active custom feature; repeatable')
    args = parser.parse_args()
    try:
        report = scan(args.probe.absolute(), args.descriptor.absolute(), args.package.absolute(),
                      args.safe_probe.absolute() if args.safe_probe else None, args.feature)
    except (OSError, ValueError, KeyError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        print('incomplete:', exc, file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True))
    return 1 if any(item.get('severity') != 'advisory' for item in report['findings']) else 3


if __name__ == '__main__':
    raise SystemExit(main())
