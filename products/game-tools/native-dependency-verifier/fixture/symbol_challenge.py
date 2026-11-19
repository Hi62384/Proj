"""Fixture-only comparison of Dependencies JSON imports and exports."""
import json
from pathlib import Path
import sys


def main(imports_path, exports_path, module):
    imports = json.loads(imports_path.read_text(encoding='utf-8-sig'))['Imports']
    exports = json.loads(exports_path.read_text(encoding='utf-8-sig'))['Exports']
    groups = [entry for entry in imports if entry['Name'].casefold() == module.casefold()]
    if len(groups) != 1:
        raise ValueError('expected exactly one import module')
    imported = groups[0]['ImportList']
    if any(entry.get('ImportByOrdinal') or entry.get('DelayImport') for entry in imported):
        raise ValueError('ordinal and delay imports are outside this experiment')
    if any(entry.get('ForwardedName') for entry in exports):
        raise ValueError('forwarded exports are outside this experiment')
    names = {entry['Name'] for entry in exports if entry.get('Name')}
    missing = sorted(entry['Name'] for entry in imported if entry['Name'] not in names)
    for name in missing:
        print(module + ': missing named export ' + name)
    if not missing:
        print(module + ': no missing named exports in this fixture comparison')
    return 1 if missing else 0


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit('usage: symbol_challenge.py <imports.json> <exports.json> <module>')
    try:
        raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('incomplete:', error, file=sys.stderr)
        raise SystemExit(2)
