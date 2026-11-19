import contextlib
import io
from pathlib import Path
import tempfile
import unittest

import collision_challenge


class CollisionChallengeTests(unittest.TestCase):
    def make_project(self, root, last_bytes, destination=''):
        for name, content in [('first', b'first'), ('second', b'second'), ('third', last_bytes)]:
            folder = root / 'addons' / name / 'bin'
            folder.mkdir(parents=True)
            (folder / (name + '.dll')).write_bytes(name.encode())
            (folder / 'shared.dll').write_bytes(content)
            dependency = 'other.dll' if name == 'first' else 'shared.dll'
            (folder / 'other.dll').write_bytes(b'other')
            dest = destination if name == 'third' else ''
            (folder.parent / (name + '.gdextension')).write_text(
                '[libraries]\nwindows.release.x86_64 = "res://addons/' + name + '/bin/' + name + '.dll"\n'
                '[dependencies]\nwindows.x86_64 = {"res://addons/' + name + '/bin/' + dependency + '": "' + dest + '"}\n',
                encoding='utf-8')

    def test_dependency_collision_between_other_extensions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.make_project(root, b'third')
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(collision_challenge.main(root), 1)

    def test_identical_content_or_different_destination(self):
        for content, destination in [(b'second', ''), (b'third', 'nested')]:
            with self.subTest(destination=destination), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                self.make_project(root, content, destination)
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(collision_challenge.main(root), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
