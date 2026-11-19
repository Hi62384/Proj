"""Narrow experiment: relate Dependencies JSON to this fixture's source descriptor.

Not a general Godot descriptor parser, Windows loader model, or product scanner.
Run from outside the Godot project; see the fixture README for limitations.
"""
import json
from pathlib import Path
import re
import sys


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit("usage: python diy_challenge.py DESCRIPTOR DEPENDENCIES_JSON [PACKAGE_ROOT]")
    descriptor = Path(sys.argv[1])
    report = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8-sig"))
    text = descriptor.read_text(encoding="utf-8-sig")
    # Deliberately restricted to the controlled fixture's two tested tags and
    # simple JSON-style dictionaries. Godot uses the first matching dependency section.
    dependency_section = text.split('[dependencies]', 1)
    if len(dependency_section) != 2:
        raise ValueError('fixture dependency section not found')
    body = dependency_section[1].split('\n[', 1)[0]
    match = re.search(r'^(windows(?:\.x86_64)?)\s*=\s*', body, re.MULTILINE)
    if not match:
        raise ValueError("fixture dependency map not found")
    dictionary = re.match(r'\{[^{};]*\}', body[match.end():])
    if not dictionary:
        raise ValueError('unsupported or unterminated fixture dependency map')
    remainder = body[match.end() + dictionary.end():].split('\n', 1)[0]
    if remainder.strip():
        raise ValueError('unsupported trailing fixture dependency syntax')
    value = re.sub(r',\s*}$', '}', dictionary.group(0))
    def unique(pairs):
        result = {}
        for key, item in pairs:
            if key in result:
                raise ValueError('duplicate dependency path')
            result[key] = item
        return result
    mapping = json.loads(value, object_pairs_hook=unique)
    declared = {}
    for path, destination in mapping.items():
        if not isinstance(path, str) or not isinstance(destination, str):
            raise ValueError('unsupported fixture dependency entry')
        if path.startswith('res://addons/fixture/bin/'):
            name = path[len('res://addons/fixture/bin/'):]
        elif path.startswith('./bin/'):
            name = path[len('./bin/'):]
        else:
            raise ValueError('unsupported fixture dependency path')
        if name in ('', '.', '..') or '/' in name or '\\' in name or name.casefold() in declared:
            raise ValueError('invalid or duplicate fixture dependency name')
        declared[name.casefold()] = destination
    source_files = {p.name.casefold() for p in (descriptor.parent / 'bin').glob('*.dll')}
    found = []
    host_only = []
    cycles = []
    package = Path(sys.argv[3]).resolve() if len(sys.argv) == 4 else None

    def visit(node, chain, ancestors):
        name = node['ModuleName']
        chain = chain + [name]
        path = node.get('Filepath')
        key = path.casefold() if isinstance(path, str) else None
        if key is not None and key in ancestors and name.casefold() in source_files:
            cycles.append(chain)
            return
        if node.get('Filepath') is None and name.casefold() in source_files:
            found.append((chain, declared.get(name.casefold())))
        elif package and node.get('Filepath') and name.casefold() in source_files:
            if not Path(node['Filepath']).resolve().is_relative_to(package):
                host_only.append(chain)
        for child in node.get('Dependencies', []):
            visit(child, chain, ancestors | {key} if key is not None else ancestors)

    visit(report['Root'], [], set())
    for chain, destination in found:
        if destination is None:
            print(' -> '.join(chain), '| absent from fixture dependency map', match.group(1))
        else:
            print(' -> '.join(chain), '| fixture dependency map', match.group(1), 'destination:', repr(destination))
    if not found:
        print('No unresolved import matched a DLL in this fixture source bin.')
    for chain in host_only:
        print(' -> '.join(chain), '| resolved outside package; runtime availability unknown')
    for chain in cycles:
        print(' -> '.join(chain), '| repeated resolved path; runtime unknown')
    return 1 if found else 3 if host_only or cycles else 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('incomplete:', error, file=sys.stderr)
        raise SystemExit(2)
