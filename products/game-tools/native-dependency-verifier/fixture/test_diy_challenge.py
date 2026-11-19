"""Run with: python test_diy_challenge.py <experiment-root>."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(sys.argv.pop(1)).resolve()
HELPER = Path(__file__).resolve().parent / 'diy_challenge.py'


class DiyChallengeTests(unittest.TestCase):
    def test_multiline_dictionary_and_unterminated_control(self):
        original = ROOT / 'multiline-project/addons/fixture/fixture.gdextension'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            leaf = {'ModuleName': 'leaf.dll', 'Filepath': None, 'Dependencies': []}
            report = root / 'dependencies.json'
            report.write_text(json.dumps({'Root': leaf}), encoding='utf-8')
            good = subprocess.run([sys.executable, str(HELPER), str(original), str(report)], capture_output=True, text=True)
            self.assertEqual(good.returncode, 1, good.stderr)
            self.assertIn("destination: ''", good.stdout)
            descriptor = root / 'fixture.gdextension'
            descriptor.write_text(original.read_text(encoding='utf-8').replace('}', ''), encoding='utf-8')
            bad = subprocess.run([sys.executable, str(HELPER), str(descriptor), str(report)], capture_output=True, text=True)
            self.assertEqual(bad.returncode, 2, bad.stderr)

    def test_relative_declared_leaf_is_not_called_absent(self):
        descriptor = ROOT / 'relative-project/addons/fixture/fixture.gdextension'
        leaf = {'ModuleName': 'leaf.dll', 'Filepath': None, 'Dependencies': []}
        middle = {'ModuleName': 'middle.dll', 'Filepath': 'middle.dll', 'Dependencies': [leaf]}
        root = {'ModuleName': 'root.dll', 'Filepath': 'root.dll', 'Dependencies': [middle]}
        extension = {'ModuleName': 'extension.dll', 'Filepath': 'extension.dll', 'Dependencies': [root]}
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / 'dependencies.json'
            report.write_text(json.dumps({'Root': extension}), encoding='utf-8')
            result = subprocess.run([sys.executable, str(HELPER), str(descriptor), str(report)],
                                    capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("destination: ''", result.stdout)
            self.assertNotIn('absent from', result.stdout)

    def test_unrecognized_dependency_path_is_incomplete(self):
        original = ROOT / 'relative-project/addons/fixture/fixture.gdextension'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            desc = root / 'fixture.gdextension'
            desc.write_text(original.read_text(encoding='utf-8').replace('./bin/leaf.dll', '../outside.dll'),
                            encoding='utf-8')
            report = root / 'dependencies.json'
            report.write_text(json.dumps({'Root': {'ModuleName': 'extension.dll', 'Dependencies': []}}), encoding='utf-8')
            result = subprocess.run([sys.executable, str(HELPER), str(desc), str(report)],
                                    capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 2)
            self.assertIn('unsupported fixture dependency path', result.stderr)

    def test_repeated_resolved_fixture_path_is_unknown(self):
        descriptor = ROOT / 'clean-project/addons/fixture/fixture.gdextension'
        repeated = {'ModuleName': 'root.dll', 'Filepath': 'C:/fixture/root.dll', 'Dependencies': []}
        middle = {'ModuleName': 'middle.dll', 'Filepath': 'C:/fixture/middle.dll', 'Dependencies': [repeated]}
        root = {'ModuleName': 'root.dll', 'Filepath': 'C:/fixture/root.dll', 'Dependencies': [middle]}
        extension = {'ModuleName': 'extension.dll', 'Filepath': 'C:/fixture/extension.dll', 'Dependencies': [root]}
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / 'dependencies.json'
            report.write_text(json.dumps({'Root': extension}), encoding='utf-8')
            result = subprocess.run([sys.executable, str(HELPER), str(descriptor), str(report)],
                                    capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 3, result.stderr)
            self.assertIn('root.dll -> middle.dll -> root.dll', result.stdout)
            self.assertIn('runtime unknown', result.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
