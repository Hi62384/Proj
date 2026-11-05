"""Real Qt layout/lifecycle tests with a dummy controller, no model or account."""
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock,patch
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[3])]
from PySide6.QtWidgets import QApplication,QPushButton,QComboBox,QPlainTextEdit,QSystemTrayIcon,QCheckBox
from PySide6.QtCore import QTimer
from assistant.permissions import Permissions
from assistant.storage import Store
from bridge.dashboard import Dashboard


class BridgeDashboardTests(unittest.TestCase):
    def wait_browser(self):
        deadline=time.monotonic()+3
        while self.window.browser_showing and time.monotonic()<deadline:
            self.app.processEvents();time.sleep(.01)
        self.app.processEvents();self.assertFalse(self.window.browser_showing)

    def test_show_browser_closed_tab_error_survives_refresh(self):
        self.runtime.broker.chrome.selected=42
        self.runtime.broker.chrome.opened_urls={}
        self.runtime.broker.chrome.call.return_value={'tabs':[{'tab':43}]}
        self.window.show_browser();self.wait_browser();self.window.refresh()
        self.assertIn('tab was closed',self.window.notice.text())
        self.assertEqual(self.runtime.broker.chrome.call.call_count,1)

    def test_show_browser_restores_only_previous_exact_url(self):
        self.runtime.broker.chrome.selected=42
        self.runtime.broker.chrome.opened_urls={42:'https://example.test/work'}
        self.runtime.broker.chrome.call.side_effect=[{'tabs':[{'tab':43}]},{'tab':43,'authorized':True,'reused':True},{'shown':True}]
        with patch('bridge.windows.allow_chrome_foreground'):
            self.window.show_browser();self.wait_browser()
        calls=self.runtime.broker.chrome.call.call_args_list
        self.assertEqual(calls[1].args,(self.runtime.owner,'open_tab',{'url':'https://example.test/work'}))
        self.assertEqual(calls[2].args,(self.runtime.owner,'show',{'tab':43}))

    def test_show_browser_does_not_bypass_restored_page_authorization(self):
        self.runtime.broker.chrome.selected=42
        self.runtime.broker.chrome.opened_urls={42:'https://example.test/work'}
        self.runtime.broker.chrome.call.side_effect=[{'tabs':[]},{'tab':43,'authorized':False}]
        self.window.show_browser();self.wait_browser()
        self.assertIn('needs authorization',self.window.notice.text())
        self.assertEqual(self.runtime.broker.chrome.call.call_count,2)

    def test_show_browser_failure_is_visible_and_not_replayed(self):
        self.runtime.broker.chrome.selected=42
        self.runtime.broker.chrome.call.side_effect=[{'tabs':[{'tab':42}]},RuntimeError('Chrome is disconnected')]
        with patch('bridge.windows.allow_chrome_foreground'):
            self.window.show_browser();self.wait_browser()
        self.window.refresh();self.assertIn('Chrome is disconnected',self.window.notice.text())
        self.assertEqual(self.runtime.broker.chrome.call.call_count,2)

    def test_show_browser_uses_exact_selected_tab(self):
        self.runtime.broker.chrome.selected=42
        self.runtime.broker.chrome.call.side_effect=[{'tabs':[{'tab':42}]},{'shown':True}]
        with patch('bridge.windows.allow_chrome_foreground') as handoff:
            self.window.show_browser();self.wait_browser();handoff.assert_called_once()
        self.runtime.broker.chrome.call.assert_called_with(self.runtime.owner,'show',{'tab':42})
        self.assertIn('Chrome was asked',self.window.notice.text())

    def test_owner_routine_toggle_persists_without_modifying_file_rules(self):
        rules=[{'path':str(Path(self.tmp.name)),'scope':'recursive','decisions':{'read':'deny'}}]
        self.store.setting('file_rules',rules);observed={}
        def enable():
            dialog=self.app.activeModalWidget();toggle=dialog.findChild(QCheckBox,'routine_approvals')
            observed['initial']=toggle.isChecked();toggle.setChecked(True);dialog.accept()
        QTimer.singleShot(0,enable);self.window.settings()
        self.assertFalse(observed['initial']);self.assertTrue(self.store.settings()['routine_approvals'])
        self.assertEqual(self.store.settings()['file_rules'],rules)
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
