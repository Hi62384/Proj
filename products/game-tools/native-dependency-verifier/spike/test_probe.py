"""Run with: python test_probe.py <PeProbe.dll> <experiment directory>."""
import hashlib
import json
from pathlib import Path
import random
import struct
import subprocess
import sys
import tempfile
import unittest

PROBE = Path(sys.argv.pop(1)).resolve()
FIXTURES = Path(sys.argv.pop(1)).resolve()


def run(path):
    return subprocess.run(['dotnet', str(PROBE), str(path)], capture_output=True, text=True, timeout=15)


class PeProbeTests(unittest.TestCase):
    def test_owned_imports_architecture_and_no_mutation(self):
        fixtures = [
            ('export/extension.dll', '0x8664', 'root.dll'),
            ('export/root.dll', '0x8664', 'middle.dll'),
            ('export/middle.dll', '0x8664', 'leaf.dll'),
            ('build-x86/extension.dll', '0x014C', 'root.dll'),
        ]
        for relative, machine, dependency in fixtures:
            with self.subTest(relative=relative):
                file = FIXTURES / relative
                before = hashlib.sha256(file.read_bytes()).digest()
                result = run(file)
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report['machine'], machine)
                self.assertIn(dependency, report['imports'])
                self.assertIn('dynamic loads unknown', report['limitations'])
                self.assertEqual(before, hashlib.sha256(file.read_bytes()).digest())

    def test_dynamic_name_is_not_misrepresented_as_static_import(self):
        result = run(FIXTURES / 'build-x86/dynamic.dll')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('optional-runtime.dll', json.loads(result.stdout)['imports'])

    def test_delay_import_is_distinguished_from_ordinary_import(self):
        result = run(FIXTURES / 'delay-build/middle-delay.dll')
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertIn('leaf.dll', report['delay_imports'])
        self.assertNotIn('leaf.dll', report['imports'])

    def test_truncated_file_and_out_of_range_import_name_are_rejected(self):
        original = bytearray((FIXTURES / 'export/extension.dll').read_bytes())
        pe = struct.unpack_from('<I', original, 0x3c)[0]
        sections = struct.unpack_from('<H', original, pe + 6)[0]
        opt_size = struct.unpack_from('<H', original, pe + 20)[0]
        optional = pe + 24
        self.assertEqual(struct.unpack_from('<H', original, optional)[0], 0x20b)
        import_rva = struct.unpack_from('<I', original, optional + 112 + 8)[0]
        section_table = optional + opt_size
        for index in range(sections):
            section = section_table + 40 * index
            virtual_size, address, raw_size, raw_offset = struct.unpack_from('<IIII', original, section + 8)
            if address <= import_rva < address + min(virtual_size, raw_size):
                descriptor = raw_offset + import_rva - address
                break
        else:
            self.fail('test fixture import descriptor was not found')
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'bad.dll'
            file.write_bytes(original[:64])
            self.assertEqual(run(file).returncode, 2)
            struct.pack_into('<I', original, descriptor + 12, 0x7fffffff)
            file.write_bytes(original)
            self.assertEqual(run(file).returncode, 2)

    def test_oversized_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'large.dll'
            with file.open('wb') as stream:
                stream.truncate(64 * 1024 * 1024 + 1)
            self.assertEqual(run(file).returncode, 2)

    def test_delay_descriptor_invalid_address_form_and_rva_are_rejected(self):
        original = bytearray((FIXTURES / 'delay-build/middle-delay.dll').read_bytes())
        pe = struct.unpack_from('<I', original, 0x3c)[0]
        count = struct.unpack_from('<H', original, pe + 6)[0]
        opt_size = struct.unpack_from('<H', original, pe + 20)[0]
        optional = pe + 24
        self.assertEqual(struct.unpack_from('<H', original, optional)[0], 0x20b)
        delay_rva = struct.unpack_from('<I', original, optional + 112 + 13 * 8)[0]
        for index in range(count):
            section = optional + opt_size + 40 * index
            virtual_size, address, raw_size, raw_offset = struct.unpack_from('<IIII', original, section + 8)
            if address <= delay_rva < address + min(virtual_size, raw_size):
                descriptor = raw_offset + delay_rva - address
                break
        else:
            self.fail('delay descriptor not found in fixture')
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'bad-delay.dll'
            for field, invalid in ((0, 0), (4, 0x7fffffff)):
                content = bytearray(original)
                struct.pack_into('<I', content, descriptor + field, invalid)
                file.write_bytes(content)
                self.assertEqual(run(file).returncode, 2)

    def test_deterministic_malformed_header_mutations_do_not_crash(self):
        original = bytearray((FIXTURES / 'export/extension.dll').read_bytes())
        pe = struct.unpack_from('<I', original, 0x3c)[0]
        opt_size = struct.unpack_from('<H', original, pe + 20)[0]
        optional = pe + 24
        section = optional + opt_size
        offsets = [0x3c, pe, pe + 6, pe + 20, optional, optional + 56,
                   optional + 112 + 8, optional + 112 + 12,
                   optional + 112 + 13 * 8, optional + 112 + 13 * 8 + 4,
                   section + 8, section + 12, section + 16, section + 20]
        rng = random.Random(23003)
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'mutated.dll'
            for offset in offsets:
                with self.subTest(offset=offset):
                    content = bytearray(original)
                    struct.pack_into('<I', content, offset, rng.choice([0, 0x7fffffff, 0xffffffff]))
                    file.write_bytes(content)
                    result = run(file)
                    self.assertIn(result.returncode, (0, 2), result.stderr)
                    if result.returncode == 0:
                        self.assertIn('limitations', json.loads(result.stdout))

    def test_invalid_import_directory_sizes_are_incomplete(self):
        original = bytearray((FIXTURES / 'export/extension.dll').read_bytes())
        pe = struct.unpack_from('<I', original, 0x3c)[0]
        optional = pe + 24
        self.assertEqual(struct.unpack_from('<H', original, optional)[0], 0x20b)
        size_offset = optional + 112 + 8 + 4
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'bad-size.dll'
            for size in (0, 1, 19, 1024 * 1024 + 1, 0x7fffffff):
                with self.subTest(size=size):
                    content = bytearray(original)
                    struct.pack_into('<I', content, size_offset, size)
                    file.write_bytes(content)
                    result = run(file)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertFalse(result.stdout.strip())


if __name__ == '__main__':
    unittest.main(verbosity=2)
