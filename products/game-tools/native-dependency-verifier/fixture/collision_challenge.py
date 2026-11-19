"""DIY comparison for the owned collision fixture, not a Godot parser."""
import hashlib
import json
from pathlib import Path
import re
import sys


def main(project):
    groups = {}

    def register(relative, destination):
        if not isinstance(relative, str) or not relative.startswith('res://') or not isinstance(destination, str):
            raise ValueError('unsupported fixture staging declaration')
        path = (project / relative[6:]).resolve()
        if not path.is_relative_to(project) or not path.is_file():
            raise ValueError('invalid or missing fixture library')
        key = (destination.casefold(), path.name.casefold())
        groups.setdefault(key, []).append((path.relative_to(project).as_posix(),
                                          hashlib.sha256(path.read_bytes()).hexdigest()))

    for descriptor in sorted((project / 'addons').rglob('*.gdextension')):
        text = descriptor.read_text(encoding='utf-8-sig')
        match = re.search(r'^windows\.release\.x86_64\s*=\s*"res://([^"\n]+)"\s*$', text, re.MULTILINE)
        if not match:
            raise ValueError('exact fixture release entry not found: ' + str(descriptor))
        register('res://' + match.group(1), '')
        dependency_section = text.split('[dependencies]', 1)
        if len(dependency_section) == 2:
            body = dependency_section[1].split('\n[', 1)[0]
            dependency = re.search(r'^(windows(?:\.x86_64)?)\s*=\s*(\{[^\n]*\})', body, re.MULTILINE)
            if not dependency:
                raise ValueError('unsupported fixture dependency map')
            mapping = json.loads(dependency.group(2))
            for relative, destination in mapping.items():
                register(relative, destination)
    conflicts = 0
    for (destination, name), candidates in sorted(groups.items()):
        if len({digest for _, digest in candidates}) > 1:
            conflicts += 1
            print('destination', repr(destination), 'name', name, candidates)
    return 1 if conflicts else 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: collision_challenge.py <owned-fixture-project>')
    try:
        raise SystemExit(main(Path(sys.argv[1]).resolve()))
    except (OSError, ValueError) as error:
        print('incomplete:', error, file=sys.stderr)
        raise SystemExit(2)
