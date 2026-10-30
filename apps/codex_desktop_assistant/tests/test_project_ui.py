"""Real Qt project dashboard and user-controlled background/shutdown behavior."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[3])]
from PySide6.QtWidgets import QApplication
from assistant.ui import MainWindow
from assistant.engine import Engine


@unittest.skipUnless(os.name=='nt','Native Windows UI required')
class ProjectUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.connection=patch.object(Engine,'connect',lambda self:None);self.connection.start()
        self.window=MainWindow(Path(self.tmp.name)/'state');self.window.show();self.app.processEvents()
    def tearDown(self):
        self.window.explicit_quit=True;self.window.close();self.app.processEvents();self.connection.stop();self.tmp.cleanup()
    def test_task_dashboard_reports_real_durable_counts(self):
        queue=self.window.broker.projects.queue;project=queue.create(self.window.selected,'Create a project')['project']
        queue.products(project,self.window.selected,[{'id':'cash','recipe':'cashflow'}]);self.window.show_projects();self.app.processEvents()
        self.assertIn('3 tasks',self.window.project_dashboard.summary.text());self.assertEqual(self.window.project_dashboard.products.topLevelItemCount(),1);self.assertEqual(self.window.project_dashboard.products.topLevelItem(0).childCount(),3)
        self.window.stop();self.assertTrue(self.window.permissions.halted.is_set())
    def test_close_keeps_active_work_visible_in_tray_but_explicit_quit_is_available(self):
        with patch.object(self.window.broker.projects.queue,'active',return_value=True),patch.object(self.window.attention.tray,'isVisible',return_value=True):
            self.window.close();self.app.processEvents();self.assertFalse(self.window.isVisible());self.assertFalse(self.window.closing)
        self.window.show();self.window.explicit_quit=True


if __name__=='__main__':unittest.main()
