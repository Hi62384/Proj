"""Real Qt mode controls with a disposable store; no model/browser is simulated."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[3])]
from PySide6.QtWidgets import QApplication,QScrollArea
from assistant.ui import MainWindow
from assistant.engine import Engine


@unittest.skipUnless(os.name=='nt','Native Windows UI required')
class ChromeUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.patch=patch.object(Engine,'connect',lambda self:None);self.patch.start()
        self.window=MainWindow(Path(self.tmp.name)/'state');self.window.show();self.app.processEvents()
    def tearDown(self):
        self.window.close();self.app.processEvents();self.patch.stop();self.tmp.cleanup()
    def test_mode_switch_preserves_dedicated_browser_and_scopes(self):
        window=self.window;dedicated=window.broker.browser
        window.browser_mode.setCurrentText('Existing Chrome');self.app.processEvents()
        self.assertTrue(window.broker.chrome.mode);self.assertTrue(window.permissions.chrome_mode);self.assertTrue(window.chrome_panel.isVisible())
        self.assertTrue(all(not widget.isVisible() for widget in window.dedicated_widgets));self.assertIsInstance(window.activity,QScrollArea)
        window.browser_mode.setCurrentText('Dedicated Browser');self.app.processEvents()
        self.assertFalse(window.broker.chrome.mode);self.assertFalse(window.chrome_panel.isVisible());self.assertIs(window.broker.browser,dedicated)
        self.assertFalse(window.permissions.browser);self.assertFalse(window.permissions.desktop)
    def test_attach_needs_real_extension_offer_and_is_conversation_bound(self):
        window=self.window;window.chrome_selected_tab=42;window.chrome_attach()
        self.assertFalse(window.broker.chrome.grants)
        bridge=window.broker.chrome.bridge
        with bridge.lock:bridge.session='test-session';bridge.offers[42]={'tab':42,'window':1,'origin':'https://example.org:443','manual':False}
        window.chrome_attach();self.assertEqual(window.broker.chrome.grants[42]['conversation'],window.selected)
        self.assertFalse(window.permissions.origins);self.assertFalse(window.permissions.desktop)
        window.permissions.resume('previous-chat')
        window.chrome_attach()
        self.assertEqual(window.permissions.owner,window.selected)
        self.assertEqual(window.broker.chrome.grants[42]['conversation'],window.selected)
        window.stop();self.assertTrue(window.permissions.halted.is_set());self.assertFalse(window.broker.chrome.grants)


if __name__=='__main__':unittest.main()
