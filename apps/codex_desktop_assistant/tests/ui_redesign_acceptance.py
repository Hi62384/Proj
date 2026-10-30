"""Real Qt render/geometry acceptance using clearly labelled representative data.

Inference connection alone is stubbed to avoid a second account/runtime instance.
The deployed main application is checked separately through its real chat tests.
"""
import argparse
import json
import sys
from pathlib import Path
from unittest.mock import patch
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[3])]
from PySide6.QtWidgets import QApplication
from assistant.ui import MainWindow
from assistant.engine import Engine
from assistant.storage import private_directory


def main():
    if '--approve-ui-tests' not in sys.argv:raise SystemExit('UI test opt-in required')
    out=private_directory()/'verification/ui-overhaul-20261029';out.mkdir(parents=True,exist_ok=True)
    app=QApplication.instance() or QApplication([]);results={}
    def record(key,value=True):results[key]=value;(out/'results.json').write_text(json.dumps(results,indent=2));print(key+': '+str(value),flush=True)
    with patch.object(Engine,'connect',lambda self:None):
        window=MainWindow(out/'sample-state');window.show();app.processEvents()
        try:
            window.store.update(window.selected,title='Product launch · sample workspace');window.title.setText('Product launch · sample workspace')
            window.store.add(window.selected,'user','Create useful spreadsheet products, validate the files and prepare the listings.')
            window.store.add(window.selected,'assistant','I’ll organize the work into a persistent project, validate each product, and prepare the approved listings.\n\n| Stage | Next step |\n|---|---|\n| Research | Compare customer needs |\n| Create | Build working files |\n| Verify | Check calculations and previews |\n\nYou can keep working while the authorized tasks run.')
            window.model.addItem('Account model','sample');window.effort.addItem('Standard','sample');window.notice.setText('Representative UI sample — no real account operation.');window.render()
            queue=window.broker.projects.queue;project=queue.create(window.selected,'Small Business Toolkit — product launch')['project'];queue.products(project,window.selected,[{'id':'cashflow','recipe':'cashflow','title':'Cash Flow Planner'},{'id':'inventory','recipe':'inventory','title':'Inventory Reorder Planner'}])
            window.resize(1360,900);app.processEvents();assert window.chat.width()>600;assert not window.control_center.isVisible();assert not window.activity_text.isVisible();window.grab().save(str(out/'main-chat.png'));record('clean_chat_layout_and_hidden_technical_controls')
            window.resize(1024,720);app.processEvents();assert window.chat.width()>350 and window.input.width()>350;record('compact_layout_remains_usable')
            window.showMaximized();app.processEvents();geometry=window.geometry();state=window.windowState();window.show_requests();app.processEvents();assert window.geometry()==geometry and window.windowState()==state;window.requests_panel.grab().save(str(out/'requests.png'));window.requests_panel.close();record('requests_preserves_maximized_geometry')
            window.show_projects();app.processEvents();assert window.project_dashboard.cards.count()>=1;assert window.project_dashboard.products.topLevelItemCount()==2;window.project_dashboard.grab().save(str(out/'projects.png'));window.project_dashboard.close();record('project_cards_and_product_stage_overview')
            window.store.setting('theme','Light');window.apply_settings();app.processEvents();window.grab().save(str(out/'light-theme.png'));record('light_theme_renders');record('complete');record('screenshots',str(out))
        finally:window.explicit_quit=True;window.close();app.processEvents()


if __name__=='__main__':main()
