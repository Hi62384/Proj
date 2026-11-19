"""Run with: python test_custom_feature_challenge.py <experiment-root>."""
import contextlib
import io
from pathlib import Path
import sys
import unittest

import custom_feature_challenge

ROOT = Path(sys.argv.pop(1)).resolve()


class CustomFeatureChallengeTests(unittest.TestCase):
    def test_owned_export_and_missing_variant(self):
        desc = ROOT / 'custom-feature-project/addons/fixture/fixture.gdextension'
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(custom_feature_challenge.main(desc, ROOT / 'custom-feature-export', ['premium']), 0)
        self.assertIn('windows.release.x86_64.premium', output.getvalue())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(custom_feature_challenge.main(desc, ROOT / 'custom-feature-missing', ['premium']), 1)

    def test_unknown_or_conflicting_feature_is_incomplete(self):
        desc = ROOT / 'custom-feature-project/addons/fixture/fixture.gdextension'
        with self.assertRaisesRegex(ValueError, 'unsupported fixture feature tag'):
            custom_feature_challenge.main(desc, ROOT / 'custom-feature-export', [])
        with self.assertRaisesRegex(ValueError, 'invalid or conflicting custom feature'):
            custom_feature_challenge.main(desc, ROOT / 'custom-feature-export', ['debug'])

    def test_relative_library_path(self):
        desc = ROOT / 'relative-project/addons/fixture/fixture.gdextension'
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(custom_feature_challenge.main(desc, ROOT / 'relative-export', []), 0)
        self.assertIn('./bin/extension.dll', output.getvalue())


if __name__ == '__main__':
    unittest.main(verbosity=2)
