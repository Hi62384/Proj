"""Time two bounded workflows on the owned fixture matrix; not a benchmark."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

FIXTURE = Path(__file__).resolve().parent
SPIKE = FIXTURE.parent / 'spike/fixture_spike.py'
CASES = [('clean-project', 'export'), ('omitted-project', 'omitted-export'),
         ('nested-project', 'nested-export'), ('dependency-order-project', 'dependency-order-export-retry')]


def execute(command, timeout=180):
    return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures', required=True, type=Path)
    parser.add_argument('--dependencies', required=True, type=Path)
    parser.add_argument('--probe', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    root, dependencies, probe = (p.resolve(strict=True) for p in
                                 (args.fixtures, args.dependencies, args.probe))
    if not root.is_dir() or not dependencies.is_file() or not probe.is_file():
        raise ValueError('fixtures must be a directory and both tools must be files')
    output = args.output.absolute()
    output.mkdir(parents=True, exist_ok=False)
    observations = []
    for project, package in CASES:
        descriptor = root / project / 'addons/fixture/fixture.gdextension'
        package_dir = root / package
        json_path = output / (package + '.dependencies.json')
        start = time.perf_counter()
        dep = execute([str(dependencies), '-json', '-chain', '-depth', '4', str(package_dir / 'extension.dll')])
        if dep.returncode != 0:
            raise ValueError('Dependencies failed for ' + package)
        # The CLI sometimes emits non-JSON text with exit 0; reject it explicitly.
        raw = dep.stdout.decode('utf-8-sig')
        json.loads(raw)
        json_path.write_text(raw, encoding='utf-8')
        helper = execute([sys.executable, str(FIXTURE / 'diy_challenge.py'), str(descriptor),
                          str(json_path), str(package_dir)])
        free_ms = round((time.perf_counter() - start) * 1000)
        if helper.returncode not in (0, 1, 3):
            raise ValueError('fixture helper failed for ' + package)
        start = time.perf_counter()
        integrated = execute([sys.executable, str(SPIKE), str(probe), str(descriptor), str(package_dir)])
        spike_ms = round((time.perf_counter() - start) * 1000)
        if integrated.returncode not in (1, 3):
            raise ValueError('integrated spike failed for ' + package)
        report = json.loads(integrated.stdout.decode('utf-8-sig'))
        observations.append({'case': package, 'dependencies_exit': dep.returncode,
                             'helper_exit': helper.returncode, 'free_elapsed_ms': free_ms,
                             'helper_output': helper.stdout.decode('utf-8-sig').strip(),
                             'spike_exit': integrated.returncode, 'spike_elapsed_ms': spike_ms,
                             'spike_findings': report['findings'], 'spike_unknown_checks': report['unknown_checks']})
        print(package, 'free_ms', free_ms, 'spike_ms', spike_ms, flush=True)
    (output / 'summary.json').write_text(json.dumps({'observations': observations}, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, UnicodeError, subprocess.SubprocessError) as error:
        print('comparison incomplete:', error, file=sys.stderr)
        raise SystemExit(2)
