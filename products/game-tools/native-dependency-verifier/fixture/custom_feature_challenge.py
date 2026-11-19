"""Small owned-fixture feature-selection comparison; not a Godot parser."""
import json
from pathlib import Path
import re
import sys


def main(descriptor, package, custom):
    features = {'windows', 'release', 'x86_64'}
    inactive = {'debug', 'linux', 'macos', 'android', 'ios', 'web', 'x86_32', 'arm64', 'editor'}
    for tag in custom:
        if not re.fullmatch(r'[A-Za-z0-9_-]+', tag) or tag in features | inactive:
            raise ValueError('invalid or conflicting custom feature')
        features.add(tag)
    active = False
    candidates = []
    for line in descriptor.read_text(encoding='utf-8-sig').splitlines():
        line = line.strip()
        if line.startswith('[') and line.endswith(']'):
            active = line == '[libraries]'
        elif active and line and not line.startswith(';'):
            item = re.fullmatch(r'([A-Za-z0-9_.]+)\s*=\s*("[^"\n]+")', line)
            if not item:
                raise ValueError('unsupported fixture library entry')
            key, raw = item.groups()
            tags = key.split('.')
            if len(tags) != len(set(tags)) or any(tag not in features | inactive for tag in tags):
                raise ValueError('unsupported fixture feature tag: ' + key)
            if all(tag in features for tag in tags):
                candidates.append((key, json.loads(raw)))
    if not candidates:
        raise ValueError('no matching fixture library')
    key, path = max(candidates, key=lambda item: len(item[0].split('.')))
    if not (path.startswith('res://addons/fixture/bin/') or path.startswith('./bin/')):
        raise ValueError('unsupported fixture source path')
    name = path[len('res://addons/fixture/bin/'):] if path.startswith('res://') else path[len('./bin/'):]
    if name in ('', '.', '..') or '/' in name or '\\' in name:
        raise ValueError('unsupported fixture filename')
    present = (package / name).is_file()
    print('selected', key, path, '| root file present:', present, '| runtime unknown')
    return 0 if present else 1


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise SystemExit('usage: custom_feature_challenge.py <descriptor> <package> [active-custom-feature ...]')
    try:
        raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:]))
    except (OSError, ValueError) as error:
        print('incomplete:', error, file=sys.stderr)
        raise SystemExit(2)
