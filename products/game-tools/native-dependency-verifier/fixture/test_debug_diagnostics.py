"""Run with: python test_debug_diagnostics.py <generated-experiment-root>."""
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(sys.argv.pop(1)).resolve()


def run(package, extra_path=None):
    env = os.environ.copy()
    env['APPDATA'] = str(ROOT / 'appdata')
    env['LOCALAPPDATA'] = str(ROOT / 'localappdata')
    env['PATH'] = str(Path(os.environ['SystemRoot']) / 'System32')
    if extra_path:
        env['PATH'] = str(extra_path) + os.pathsep + env['PATH']
    return subprocess.run([str(package / 'fixture.exe'), '--headless'], cwd=package, env=env,
                          capture_output=True, text=True, errors='replace', timeout=30)


@unittest.skipUnless(os.name == 'nt', 'Windows debug fixture')
class DebugDiagnosticsTests(unittest.TestCase):
    def test_clean_debug_export_loads(self):
        result = run(ROOT / 'debug-export')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('GDM-003 loaded: true', result.stdout)

    def test_missing_leaf_is_named_without_external_path(self):
        result = run(ROOT / 'debug-missing-leaf')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('GDM-003 loaded: false', result.stdout)
        self.assertIn('Missing dependencies: leaf.dll', result.stderr)

    def test_external_path_changes_debug_diagnostic_not_loader_outcome(self):
        result = run(ROOT / 'debug-missing-leaf', ROOT / 'debug-export')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('GDM-003 loaded: false', result.stdout)
        self.assertIn('Error 126', result.stderr)
        self.assertNotIn('Missing dependencies: leaf.dll', result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
