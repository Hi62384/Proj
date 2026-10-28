"""Real native Qt launch/interactions/persistence; does not simulate Codex output."""
import json
import sys
import time
from pathlib import Path
APP=Path(__file__).resolve().parents[1];sys.path[:0]=[str(APP),str(APP.parents[1])]
from PySide6.QtWidgets import QApplication,QPushButton,QInputDialog,QLineEdit,QDialogButtonBox,QComboBox,QLabel
from PySide6.QtCore import Qt,QTimer
from PySide6.QtTest import QTest
from assistant.storage import private_directory
from assistant.ui import MainWindow


def main():
    app=QApplication([]);app.setStyle('Fusion')
    directory=private_directory()/'verification'/('ui-'+time.strftime('%Y%m%d-%H%M%S'));directory.mkdir(parents=True)
    results={};window=MainWindow(directory/'state');window.show()
    def record(key,value=True):results[key]=value;print(key+': '+str(value),flush=True)
    def click(label):
        widgets=[x for x in window.findChildren(QPushButton) if x.text()==label]
        assert len(widgets)==1,label
        QTest.mouseClick(widgets[0],Qt.LeftButton);app.processEvents()
    try:
        assert QTest.qWaitForWindowExposed(window,5000);record('native_window_exposed')
        first=window.selected;click('+ New Chat');second=window.selected;assert second!=first
        record('new_conversation_control')
        def rename():
            dialog=QApplication.activeModalWidget();assert isinstance(dialog,QInputDialog)
            dialog.setTextValue('Synthetic UI conversation');dialog.accept()
        QTimer.singleShot(100,rename);click('Rename');assert window.store.conversation(second)['title']=='Synthetic UI conversation'
        record('rename_control')
        click('Pin / unpin');assert window.store.conversation(second)['pinned'];record('pin_control')
        click('Archive / restore');assert window.store.conversation(second)['archived'];window.archived.setChecked(True);window.choose(second);click('Archive / restore')
        window.archived.setChecked(False);window.choose(second);record('archive_restore_controls')
        fixture=directory/'sample.txt';fixture.write_text('Only synthetic UI content')
        window.add_files([str(fixture)]);assert len(window.pending)==1
        window.attachment_list.setCurrentRow(0);click('Remove attachment');assert not window.pending;record('attachment_add_remove')
        # Stage a real owner message through the UI. If WSL cannot start it must
        # remain durably visible with a diagnostic, never a fabricated response.
        window.input.setPlainText('Reply exactly UI-CHECK-618.');click('Send')
        deadline=time.monotonic()+20
        while time.monotonic()<deadline:
            app.processEvents();time.sleep(.03)
            state=window.store.conversation(second)['status']
            if state=='Review after error' or any(x['role']=='assistant' for x in window.store.messages(second)):break
        assert any(x['role']=='user' and 'UI-CHECK-618' in x['text'] for x in window.store.messages(second))
        record('send_is_durable')
        if any(x['role']=='assistant' and 'UI-CHECK-618' in x['text'] for x in window.store.messages(second)):record('real_model_response',True)
        else:record('real_model_response','BLOCKED: '+window.notice.text())
        # Verify settings dialog really saves UI preferences, with no computer grants.
        def settings():
            dialog=QApplication.activeModalWidget();assert dialog is not None
            theme=next(x for x in dialog.findChildren(QComboBox) if x.findText('Light')>=0)
            theme.setCurrentText('Light')
            dialog.accept()
        QTimer.singleShot(100,settings);click('Settings');assert window.store.settings()['theme']=='Light';record('settings_save_and_light_theme')
        click('Stop');assert window.permissions.halted.is_set() and not window.permissions.windows;record('stop_revokes_grants')
        window.grab().save(str(directory/'synthetic-ui.png'))
        window.close();app.processEvents()
        window=MainWindow(directory/'state');window.show();app.processEvents()
        assert window.store.conversation(second)['title']=='Synthetic UI conversation'
        assert window.permissions.halted.is_set() and not window.permissions.windows
        record('native_restart_persists_history_without_control')
        record('complete')
    except Exception as error:record('complete',False);record('error',type(error).__name__+': '+str(error));raise
    finally:
        window.close();app.processEvents();(directory/'results.json').write_text(json.dumps(results,indent=2));print('Private evidence: '+str(directory/'results.json'),flush=True)


if __name__=='__main__':main()
