"""Authoritative project status and non-disruptive unresolved-request panel."""
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[3])]
from assistant.status import resolve,pending
from assistant.permissions import Permissions
from assistant.engine import Engine
from assistant.ui import MainWindow
from PySide6.QtWidgets import QApplication


class StatusTests(unittest.TestCase):
    def test_project_overrides_completed_chat_and_blocked_is_not_completed(self):
        task={'status':'Completed'}
        self.assertEqual(resolve(task,{'state':'running','counts':{'completed':3},'total':5}),'Working')
        self.assertEqual(resolve(task,{'state':'blocked','counts':{'blocked':1},'total':5}),'Error')
        self.assertEqual(resolve(task,{'state':'completed','counts':{'completed':3},'total':5}),'Error')
    def test_approval_and_manual_requests_have_distinct_states(self):
        self.assertEqual(resolve(requests=[{'args':{}}]),'Waiting for Approval')
        self.assertEqual(resolve(requests=[{'args':{'manual_step':True}}]),'Waiting for User')
    def test_expired_denied_and_stale_requests_are_not_counted(self):
        p=Permissions();p.resume('owner');now=time.monotonic()
        def request(deadline,generation=None):return {'event':threading.Event(),'generation':p.generation if generation is None else generation,'deadline':deadline}
        live=request(now+5);expired=request(now-1);stale=request(now+5,p.generation-1);denied=request(now+5);denied['event'].set()
        self.assertEqual(pending([live,expired,stale,denied],p,now),[live])


class RequestUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.connection=patch.object(Engine,'connect',lambda self:None);self.connection.start()
        self.w=MainWindow(Path(self.tmp.name)/'state');self.w.showMaximized();self.app.processEvents()
    def tearDown(self):self.w.explicit_quit=True;self.w.close();self.app.processEvents();self.connection.stop();self.tmp.cleanup()
    def test_requests_open_preserves_maximized_geometry_and_counts_only_unresolved(self):
        w=self.w;w.permissions.resume(w.selected)
        request={'event':threading.Event(),'generation':w.permissions.generation,'deadline':time.monotonic()+60,'conversation':w.selected,'label':'Synthetic authorization','args':{'approval_reason':'A consequential test operation requires an owner decision.'},'allowed':False}
        w.requests.append(request);w.show_request(request);self.app.processEvents();geometry=w.geometry();state=w.windowState()
        w.show_requests();self.app.processEvents();self.assertEqual(w.geometry(),geometry);self.assertEqual(w.windowState(),state);self.assertIn('1',w.attention_button.text())
        request['event'].set();w.refresh_requests();w.requests_panel.refresh();self.assertEqual(w.attention_button.text(),'Requests');self.assertEqual(w.attention.unread,0)
    def test_main_layout_hides_technical_and_computer_controls(self):
        self.assertFalse(self.w.control_center.isVisible());self.assertFalse(self.w.activity_text.isVisible());self.assertFalse(self.w.browser_mode.isVisible())
        names=[b.text() for b in self.w.sidebar.findChildren(__import__('PySide6.QtWidgets',fromlist=['QPushButton']).QPushButton)]
        self.assertNotIn('Delete history',names);self.assertIn('Control Center',names)


if __name__=='__main__':unittest.main()
