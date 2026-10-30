"""Real Qt layout/lifecycle tests with a dummy controller, no model or account."""
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock,patch
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[3])]
from PySide6.QtWidgets import QApplication,QPushButton,QComboBox,QPlainTextEdit,QSystemTrayIcon
from assistant.permissions import Permissions
from assistant.storage import Store
from bridge.dashboard import Dashboard


class BridgeDashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=Store(Path(self.tmp.name));self.runtime=Mock();self.runtime.store=self.store;self.runtime.permissions=Permissions();self.runtime.requests=[]
        self.state={'mcp_clients_connected':0,'chrome_connected':False,'full_browser_access':False,'desktop_authorized':False,'stopped':False,'active_tool':None,'latest_action':'Ready','reasoning_state':'Waiting for Codex','pending_requests':0}
        self.runtime.status.side_effect=lambda:dict(self.state)
        with patch('bridge.dashboard.Runtime',return_value=self.runtime):self.window=Dashboard(Path(self.tmp.name))
        self.window.show();self.app.processEvents()
    def tearDown(self):
        self.window.explicit_quit=True;self.window.close();self.app.processEvents();self.store.close();self.tmp.cleanup()

    def test_no_duplicate_chat_model_or_reasoning_controls(self):
        labels={button.text() for button in self.window.findChildren(QPushButton)}
        self.assertTrue({'View Projects','Show Browser','Stop','Settings','Emergency Stop','Quit Bridge'}<=labels)
        self.assertFalse({'Send','+ New Chat','Attach'}&labels)
        self.assertFalse(self.window.findChildren(QComboBox));self.assertFalse(self.window.findChildren(QPlainTextEdit))
        self.assertIn('Waiting for Codex',self.window.work.text());self.assertIn('Disconnected',self.window.connection.text())

    def test_request_explains_why_and_preserves_maximized_geometry(self):
        self.window.showMaximized();self.app.processEvents();geometry=self.window.geometry();state=self.window.windowState()
        request={'id':'test','label':'Upload exact test file','args':{'approval_reason':'This transfers a private test file to the specified website.'},'event':threading.Event(),'generation':self.runtime.permissions.generation,'deadline':time.monotonic()+60,'allowed':False}
        self.runtime.requests.append(request);self.state['pending_requests']=1;self.window.refresh();self.app.processEvents()
        self.assertEqual(self.window.geometry(),geometry);self.assertEqual(self.window.windowState(),state);self.assertEqual(len(self.window.cards),1)
        card=self.window.cards['test'];next(b for b in card.findChildren(QPushButton) if b.text()=='Allow Once').click()
        self.assertTrue(request['event'].is_set());self.assertTrue(request['allowed']);self.assertEqual(len(self.window.cards),0)

    def test_close_to_tray_does_not_stop_controller_but_quit_does(self):
        with patch.object(QSystemTrayIcon,'isSystemTrayAvailable',return_value=True):self.window.close()
        self.assertFalse(self.window.isVisible());self.runtime.close.assert_not_called()
        self.window.explicit_quit=True;self.window.close();self.runtime.close.assert_called_once()


if __name__=='__main__':unittest.main()
