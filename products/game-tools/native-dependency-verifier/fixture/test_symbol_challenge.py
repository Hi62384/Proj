import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import symbol_challenge


class SymbolChallengeTests(unittest.TestCase):
    def compare(self, imported, exported):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            imports = root / 'imports.json'
            exports = root / 'exports.json'
            imports.write_text(json.dumps({'Imports': [{'Name': 'root.dll', 'ImportList': imported}]}))
            exports.write_text(json.dumps({'Exports': exported}))
            with contextlib.redirect_stdout(io.StringIO()):
                return symbol_challenge.main(imports, exports, 'ROOT.DLL')

    def test_missing_and_present_named_symbol(self):
        imported = [{'Name': 'root_value', 'ImportByOrdinal': False, 'DelayImport': False}]
        self.assertEqual(self.compare(imported, [{'Name': 'fixture_value', 'ForwardedName': ''}]), 1)
        self.assertEqual(self.compare(imported, [{'Name': 'root_value', 'ForwardedName': ''}]), 0)
        self.assertEqual(self.compare(imported, [{'Name': 'ROOT_VALUE', 'ForwardedName': ''}]), 1)

    def test_unsupported_import_and_forwarder_are_incomplete(self):
        ordinal = [{'Name': '', 'ImportByOrdinal': True, 'DelayImport': False}]
        with self.assertRaises(ValueError):
            self.compare(ordinal, [])
        delayed = [{'Name': 'x', 'ImportByOrdinal': False, 'DelayImport': True}]
        with self.assertRaises(ValueError):
            self.compare(delayed, [])
        with self.assertRaises(ValueError):
            self.compare([], [{'Name': 'x', 'ForwardedName': 'other.x'}])


if __name__ == '__main__':
    unittest.main(verbosity=2)
