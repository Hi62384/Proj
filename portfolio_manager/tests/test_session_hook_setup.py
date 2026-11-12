"""Exercise owner-requested hook setup using disposable project folders."""
import json
import base64
from pathlib import Path
import tempfile
import unittest

from portfolio_manager.setup_session_hook import configuration, install


class SessionHookSetupTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='portfolio hook test ')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        python = self.root / 'apps/codex_desktop_assistant/.venv/Scripts/python.exe'
        python.parent.mkdir(parents=True)
        python.write_bytes(b'python')
        hook = self.root / 'portfolio_manager/codex_session_hook.py'
        hook.parent.mkdir()
        hook.write_text('# test', encoding='utf-8')

    def test_install_merges_preserves_and_is_idempotent(self):
        config = self.root / '.codex/hooks.json'
        config.parent.mkdir()
        original = b'{"description":"Existing", "hooks":{"Stop":[{"hooks":[]}]}}'
        config.write_bytes(original)
        self.assertTrue(install(self.root))
        result = json.loads(config.read_text(encoding='utf-8'))
        self.assertEqual(result['description'], 'Existing')
        self.assertIn('Stop', result['hooks'])
        handler = result['hooks']['SessionStart'][0]['hooks'][0]
        encoded = handler['command'].split()[-1]
        invocation = base64.b64decode(encoded).decode('utf-16le')
        self.assertIn('codex_session_hook.py', invocation)
        self.assertIn(str(self.root), invocation)
        self.assertEqual((config.parent / 'hooks.json.portfolio-backup').read_bytes(), original)
        self.assertFalse(install(self.root))

    def test_invalid_configuration_and_different_existing_hook_are_preserved(self):
        config = self.root / '.codex/hooks.json'
        config.parent.mkdir()
        for original in (b'{bad', json.dumps({'hooks': {'SessionStart': [{'hooks': [
                {'type': 'command', 'command': 'python codex_session_hook.py'}]}]}}).encode()):
            with self.subTest(original=original):
                config.write_bytes(original)
                with self.assertRaises(ValueError):
                    install(self.root)
                self.assertEqual(config.read_bytes(), original)

    def test_preview_does_not_write(self):
        result, changed = configuration(self.root, b'')
        self.assertTrue(changed)
        self.assertIn('SessionStart', json.loads(result)['hooks'])
        self.assertFalse((self.root / '.codex').exists())


if __name__ == '__main__':
    unittest.main()
