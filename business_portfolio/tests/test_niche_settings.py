import json
from pathlib import Path
import tempfile
import threading
import unittest

from business_portfolio.tools.niche_settings import set_working


class NicheSettingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'business_portfolio'
        self.niches = self.root / 'niches'
        for path, ident, title, parent in (
            ('digital-products', 'N-cat', 'Digital Products', None),
            ('digital-products/example', 'N-niche', 'Example', 'N-cat'),
        ):
            folder = self.niches / path
            folder.mkdir(parents=True)
            (folder / 'NICHE.json').write_text(json.dumps({
                'id': ident, 'title': title, 'parent': parent, 'path': path,
                'priority': 1, 'working': False,
            }), encoding='utf-8')

    def test_independent_setting_persists_and_is_boolean(self):
        set_working(self.root, 'N-cat', True)
        set_working(self.root, 'N-niche', True)
        set_working(self.root, 'N-cat', False)
        category = json.loads((self.niches / 'digital-products/NICHE.json').read_text())
        niche = json.loads((self.niches / 'digital-products/example/NICHE.json').read_text())
        self.assertIs(category['working'], False)
        self.assertIs(niche['working'], True)
        with self.assertRaises(ValueError):
            set_working(self.root, 'N-niche', 'false')

    def test_concurrent_updates_leave_valid_json(self):
        errors = []
        def update(value):
            try:
                set_working(self.root, 'N-niche', value)
            except Exception as exc:
                errors.append(exc)
        threads = [threading.Thread(target=update, args=(bool(i % 2),)) for i in range(12)]
        for thread in threads: thread.start()
        for thread in threads: thread.join()
        self.assertEqual(errors, [])
        data = json.loads((self.niches / 'digital-products/example/NICHE.json').read_text())
        self.assertIsInstance(data['working'], bool)


if __name__ == '__main__':
    unittest.main()
