"""Run with: python test_fixture_spike.py <PeProbe.dll> <experiment directory>."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import fixture_spike

PROBE = Path(sys.argv.pop(1)).resolve()
ROOT = Path(sys.argv.pop(1)).resolve()
SAFE_PROBE = Path(sys.argv.pop(1)).resolve() if len(sys.argv) > 1 else None


def digest_tree(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).digest()
            for p in root.rglob('*') if p.is_file()}


class FixtureSpikeTests(unittest.TestCase):
    def test_multiline_descriptor_and_missing_leaf(self):
        project = ROOT / 'multiline-project'
        desc = project / 'addons/fixture/fixture.gdextension'
        package = ROOT / 'multiline-export'
        before_source, before_package = digest_tree(project), digest_tree(package)
        result = fixture_spike.scan(PROBE, desc, package)
        self.assertEqual(result['selected_library']['source'], './bin/extension.dll')
        self.assertEqual(result['findings'], [])
        self.assertEqual(before_source, digest_tree(project))
        self.assertEqual(before_package, digest_tree(package))
        result = fixture_spike.scan(PROBE, desc, ROOT / 'multiline-missing-leaf')
        self.assertEqual(result['findings'][0]['code'], 'package_root_missing')
        self.assertEqual(result['findings'][0]['chain'], ['extension.dll', 'root.dll', 'middle.dll', 'leaf.dll'])
        self.assertEqual(result['findings'][0]['declared_source'], './bin/leaf.dll')

    def test_cases_and_input_immutability(self):
        cases = [
            ('clean-project', 'export', None, None),
            ('embedded-project', 'embedded-export', None, None),
            ('clean-project', 'missing-direct', 'package_root_missing', ''),
            ('omitted-project', 'omitted-export', 'package_root_missing', None),
            ('nested-project', 'nested-export', 'package_root_missing', 'nested'),
            ('clean-project', 'misplaced-leaf', 'package_root_missing', ''),
            ('clean-project', 'wrong-arch-valid-symbol', 'wrong_architecture', None),
            ('clean-project', 'missing-extension', 'package_root_missing', None),
        ]
        for project, package, code, destination in cases:
            with self.subTest(package=package):
                desc = ROOT / project / 'addons/fixture/fixture.gdextension'
                folder = ROOT / package
                before = digest_tree(folder)
                before_source = digest_tree(ROOT / project)
                report = fixture_spike.scan(PROBE, desc, folder)
                self.assertTrue(report['unknown_checks'])
                self.assertEqual(before, digest_tree(folder))
                self.assertEqual(before_source, digest_tree(ROOT / project))
                codes = [f['code'] for f in report['findings']]
                if package == 'wrong-arch-valid-symbol':
                    self.assertEqual(set(codes), {'wrong_architecture', 'staged_content_differs'})
                else:
                    self.assertEqual(codes, [code] if code else [])
                if code == 'package_root_missing':
                    self.assertEqual(report['findings'][0]['declared_destination'], destination)
                if package == 'omitted-export':
                    self.assertEqual(report['findings'][0]['chain'],
                                     ['extension.dll', 'root.dll', 'middle.dll', 'leaf.dll'])
                if code == 'wrong_architecture':
                    self.assertEqual(next(f for f in report['findings'] if f['code'] == code)['actual'], '0x014C')

    def test_host_path_does_not_change_package_observation(self):
        desc = ROOT / 'clean-project/addons/fixture/fixture.gdextension'
        report = fixture_spike.scan(PROBE, desc, ROOT / 'missing-transitive')
        self.assertEqual(report['findings'][0]['chain'][-1], 'leaf.dll')
        self.assertIn('host and system DLL resolution', report['unknown_checks'])

    def test_missing_delay_import_remains_unknown(self):
        desc = ROOT / 'clean-project/addons/fixture/fixture.gdextension'
        report = fixture_spike.scan(PROBE, desc, ROOT / 'delay-missing-export')
        self.assertEqual([f['code'] for f in report['findings']], ['staged_content_differs'])
        self.assertEqual(report['delay_imports'][0]['chain'],
                         ['extension.dll', 'root.dll', 'middle.dll', 'leaf.dll'])
        self.assertEqual(report['delay_imports'][0]['status'], 'runtime-dependent unknown')

    def test_import_cycle_terminates_and_remains_unknown(self):
        desc = ROOT / 'clean-project/addons/fixture/fixture.gdextension'
        package = ROOT / 'cycle-export'
        before = digest_tree(package)
        report = fixture_spike.scan(PROBE, desc, package)
        self.assertEqual(before, digest_tree(package))
        self.assertEqual(report['cycles'][0]['chain'],
                         ['extension.dll', 'root.dll', 'middle.dll', 'root.dll'])
        self.assertEqual(report['cycles'][0]['status'], 'static import cycle; runtime unknown')

    def test_replaced_dependency_reports_byte_difference_not_runtime_cause(self):
        desc = ROOT / 'clean-project/addons/fixture/fixture.gdextension'
        report = fixture_spike.scan(PROBE, desc, ROOT / 'replaced-dependency')
        finding = next(item for item in report['findings'] if item['code'] == 'staged_content_differs')
        self.assertEqual(finding['basename'], 'root.dll')
        self.assertNotEqual(finding['source_sha256'], finding['staged_sha256'])
        self.assertIn('may be legitimate', finding['confidence'])

    def test_benign_byte_difference_is_advisory_not_confirmed_failure(self):
        desc = ROOT / 'clean-project/addons/fixture/fixture.gdextension'
        report = fixture_spike.scan(PROBE, desc, ROOT / 'benign-transform')
        self.assertEqual([item['code'] for item in report['findings']], ['staged_content_differs'])
        self.assertEqual(report['findings'][0]['severity'], 'advisory')
        command = [sys.executable, str(Path(fixture_spike.__file__)), str(PROBE), str(desc),
                   str(ROOT / 'benign-transform')]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 3, result.stderr)

    def test_godot_library_specificity_and_dependency_order_cases(self):
        good_desc = ROOT / 'tag-fresh-project/addons/fixture/fixture.gdextension'
        good = fixture_spike.scan(PROBE, good_desc, ROOT / 'tag-fresh-export')
        self.assertEqual(good['findings'], [])
        bad_desc = ROOT / 'tag-specific-missing/addons/fixture/fixture.gdextension'
        bad = fixture_spike.scan(PROBE, bad_desc, ROOT / 'tag-specific-missing-export')
        self.assertEqual(bad['findings'][0]['code'], 'source_library_missing')
        self.assertTrue(bad['findings'][0]['checked_field'].endswith('libraries:windows.release.x86_64'))
        order_desc = ROOT / 'dependency-order-project/addons/fixture/fixture.gdextension'
        order = fixture_spike.scan(PROBE, order_desc, ROOT / 'dependency-order-export-retry')
        self.assertEqual(order['findings'][0]['chain'][-1], 'leaf.dll')
        self.assertIsNone(order['findings'][0]['declared_source'])
        self.assertTrue(order['findings'][0]['checked_field'].endswith('dependencies:windows'))

    def test_unknown_features_are_not_assumed_inactive(self):
        original = ROOT / 'clean-project/addons/fixture/fixture.gdextension'
        with tempfile.TemporaryDirectory() as directory:
            descriptor = Path(directory) / 'fixture.gdextension'
            descriptor.write_text(original.read_text(encoding='utf-8').replace(
                                  '[dependencies]', 'windows.release.custom = "res://addons/fixture/bin/custom.dll"\n\n[dependencies]'),
                                  encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'unsupported or duplicate fixture feature tag'):
                fixture_spike.scan(PROBE, descriptor, ROOT / 'export')

    def test_explicit_custom_feature_matches_owned_export(self):
        desc = ROOT / 'custom-feature-project/addons/fixture/fixture.gdextension'
        package = ROOT / 'custom-feature-export'
        with self.assertRaisesRegex(ValueError, 'unsupported or duplicate fixture feature tag'):
            fixture_spike.scan(PROBE, desc, package)
        before_source = digest_tree(ROOT / 'custom-feature-project')
        before_package = digest_tree(package)
        report = fixture_spike.scan(PROBE, desc, package, custom_features=['premium'])
        self.assertEqual(report['selected_library']['source'], 'res://addons/fixture/bin/premium.dll')
        self.assertTrue(report['selected_library']['field'].endswith('windows.release.x86_64.premium'))
        self.assertEqual(report['findings'], [])
        self.assertEqual(before_source, digest_tree(ROOT / 'custom-feature-project'))
        self.assertEqual(before_package, digest_tree(package))
        missing = fixture_spike.scan(PROBE, desc, ROOT / 'custom-feature-missing', custom_features=['premium'])
        self.assertEqual(missing['findings'][0]['code'], 'package_root_missing')
        self.assertEqual(missing['findings'][0]['chain'], ['premium.dll'])
        with self.assertRaisesRegex(ValueError, 'invalid or conflicting explicit custom feature'):
            fixture_spike.scan(PROBE, desc, package, custom_features=['debug'])

    def test_relative_fixture_paths_preserve_declaration_and_detect_missing(self):
        desc = ROOT / 'relative-project/addons/fixture/fixture.gdextension'
        report = fixture_spike.scan(PROBE, desc, ROOT / 'relative-export')
        self.assertEqual(report['selected_library']['source'], './bin/extension.dll')
        self.assertEqual(report['selected_library']['normalized_source'],
                         'res://addons/fixture/bin/extension.dll')
        self.assertEqual(report['findings'], [])
        missing = fixture_spike.scan(PROBE, desc, ROOT / 'relative-missing-leaf')
        finding = missing['findings'][0]
        self.assertEqual(finding['code'], 'package_root_missing')
        self.assertEqual(finding['declared_source'], './bin/leaf.dll')

    def test_different_extension_dlls_with_same_staged_name_are_reported(self):
        descriptor = ROOT / 'collision-project/addons/fixture/fixture.gdextension'
        package = ROOT / 'collision-export'
        before = digest_tree(package)
        report = fixture_spike.scan(PROBE, descriptor, package)
        self.assertEqual(before, digest_tree(package))
        finding = next(item for item in report['findings'] if item['code'] == 'conflicting_staged_basename')
        self.assertEqual(finding['basename'], 'extension.dll')
        self.assertNotEqual(*finding['sha256'])
        self.assertEqual(finding['declarations'], ['res://addons/fixture/bin/extension.dll',
                                                   'res://addons/other/bin/extension.dll'])

    def test_identical_extension_dlls_are_not_claimed_as_content_collision(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'project'
            shutil.copytree(ROOT / 'collision-project', project, ignore=shutil.ignore_patterns('.godot'))
            shutil.copyfile(project / 'addons/fixture/bin/extension.dll',
                            project / 'addons/other/bin/extension.dll')
            report = fixture_spike.scan(PROBE, project / 'addons/fixture/fixture.gdextension', ROOT / 'export')
            self.assertFalse(any(item['code'] == 'conflicting_staged_basename' for item in report['findings']))

    def test_distinct_dependency_sources_for_same_destination_are_reported(self):
        descriptor = ROOT / 'dependency-collision-project/addons/fixture/fixture.gdextension'
        package = ROOT / 'dependency-collision-export'
        before = digest_tree(package)
        report = fixture_spike.scan(PROBE, descriptor, package)
        self.assertEqual(before, digest_tree(package))
        finding = next(item for item in report['findings'] if item['code'] == 'conflicting_staged_dependency')
        self.assertEqual(finding['basename'], 'root.dll')
        self.assertEqual(finding['destination'], '')
        self.assertNotEqual(*finding['sha256'])
        self.assertEqual(finding['declarations'], ['res://addons/fixture/bin/root.dll',
                                                   'res://addons/other/bin/root.dll'])

    def test_identical_dependencies_do_not_claim_content_collision(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'project'
            shutil.copytree(ROOT / 'dependency-collision-project', project, ignore=shutil.ignore_patterns('.godot'))
            shutil.copyfile(project / 'addons/fixture/bin/root.dll', project / 'addons/other/bin/root.dll')
            report = fixture_spike.scan(PROBE, project / 'addons/fixture/fixture.gdextension', ROOT / 'export')
            self.assertFalse(any(item['code'] == 'conflicting_staged_dependency' for item in report['findings']))

    def test_different_dependency_destinations_do_not_claim_same_staged_path(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'project'
            shutil.copytree(ROOT / 'dependency-collision-project', project, ignore=shutil.ignore_patterns('.godot'))
            descriptor = project / 'addons/other/other.gdextension'
            text = descriptor.read_text(encoding='utf-8').replace(
                '"res://addons/other/bin/root.dll": ""', '"res://addons/other/bin/root.dll": "nested"')
            descriptor.write_text(text, encoding='utf-8')
            report = fixture_spike.scan(PROBE, project / 'addons/fixture/fixture.gdextension', ROOT / 'export')
            self.assertFalse(any(item['code'] == 'conflicting_staged_dependency' for item in report['findings']))

    def test_collision_between_other_extensions_is_not_missed(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'project'
            shutil.copytree(ROOT / 'clean-project', project, ignore=shutil.ignore_patterns('.godot'))
            for name, binary in [('second', ROOT / 'build-x64/root.dll'),
                                 ('third', ROOT / 'wrong-dependency-build/root.dll')]:
                folder = project / 'addons' / name / 'bin'
                folder.mkdir(parents=True)
                shutil.copyfile(ROOT / 'build-x64/extension.dll', folder / (name + '.dll'))
                shutil.copyfile(binary, folder / 'shared.dll')
                (folder.parent / (name + '.gdextension')).write_text(
                    '[libraries]\nwindows.release.x86_64 = "res://addons/' + name + '/bin/' + name + '.dll"\n'
                    '[dependencies]\nwindows.x86_64 = {"res://addons/' + name + '/bin/shared.dll": ""}\n',
                    encoding='utf-8')
            report = fixture_spike.scan(PROBE, project / 'addons/fixture/fixture.gdextension', ROOT / 'export')
            finding = next(item for item in report['findings'] if item['code'] == 'conflicting_staged_dependency')
            self.assertEqual(finding['basename'], 'shared.dll')
            self.assertEqual(finding['declarations'], ['res://addons/second/bin/shared.dll',
                                                       'res://addons/third/bin/shared.dll'])

    def test_extension_can_conflict_with_other_declared_dependency(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'project'
            shutil.copytree(ROOT / 'clean-project', project, ignore=shutil.ignore_patterns('.godot'))
            folder = project / 'addons/other/bin'
            folder.mkdir(parents=True)
            shutil.copyfile(ROOT / 'wrong-dependency-build/root.dll', folder / 'root.dll')
            (folder.parent / 'other.gdextension').write_text(
                '[libraries]\nwindows.release.x86_64 = "res://addons/other/bin/root.dll"\n', encoding='utf-8')
            report = fixture_spike.scan(PROBE, project / 'addons/fixture/fixture.gdextension', ROOT / 'export')
            finding = next(item for item in report['findings'] if item['code'] == 'conflicting_staged_binary')
            self.assertEqual(finding['basename'], 'root.dll')

    def test_hardlinked_package_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = root / 'original.dll'
            shutil.copyfile(ROOT / 'export/extension.dll', original)
            package = root / 'package'
            package.mkdir()
            try:
                os.link(original, package / 'extension.dll')
            except OSError as error:
                self.skipTest('hard links unavailable: ' + str(error))
            desc = ROOT / 'clean-project/addons/fixture/fixture.gdextension'
            with self.assertRaisesRegex(ValueError, 'single-link regular file'):
                fixture_spike.scan(PROBE, desc, package)

    @unittest.skipUnless(os.name == 'nt', 'Windows junction test')
    def test_package_directory_junction_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / 'target'
            target.mkdir()
            link = root / 'junction'
            created = subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(link), str(target)],
                                     capture_output=True, text=True)
            if created.returncode:
                self.skipTest('junction unavailable: ' + created.stderr)
            try:
                desc = ROOT / 'clean-project/addons/fixture/fixture.gdextension'
                with self.assertRaisesRegex(ValueError, 'reparse point'):
                    fixture_spike.scan(PROBE, desc, link)
                self.assertTrue(target.is_dir())
            finally:
                os.rmdir(link)

    def test_package_dll_limit_returns_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / 'package'
            package.mkdir()
            for index in range(257):
                (package / f'fixture-{index}.dll').touch()
            desc = ROOT / 'clean-project/addons/fixture/fixture.gdextension'
            with self.assertRaisesRegex(ValueError, 'DLL count limit'):
                fixture_spike.scan(PROBE, desc, package)

    def test_fixture_path_traversal_is_rejected(self):
        original = ROOT / 'clean-project/addons/fixture/fixture.gdextension'
        with tempfile.TemporaryDirectory() as directory:
            descriptor = Path(directory) / 'fixture.gdextension'
            descriptor.write_text(original.read_text(encoding='utf-8').replace(
                'res://addons/fixture/bin/extension.dll',
                'res://addons/fixture/bin/../outside.dll'), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'unsupported fixture library path'):
                fixture_spike.scan(PROBE, descriptor, ROOT / 'export')


    @unittest.skipUnless(SAFE_PROBE, 'optional handle probe not supplied')
    def test_optional_handle_mode_matches_fixture_findings(self):
        for project, package in [('clean-project', 'export'), ('omitted-project', 'omitted-export'),
                                 ('collision-project', 'collision-export'),
                                 ('clean-project', 'delay-missing-export')]:
            with self.subTest(package=package):
                desc = ROOT / project / 'addons/fixture/fixture.gdextension'
                standard = fixture_spike.scan(PROBE, desc, ROOT / package)
                via_handle = fixture_spike.scan(PROBE, desc, ROOT / package, SAFE_PROBE)
                self.assertEqual(via_handle, standard)


if __name__ == '__main__':
    unittest.main(verbosity=2)
