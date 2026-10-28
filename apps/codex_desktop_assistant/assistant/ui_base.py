"""Shared chat history, attachments, lifecycle and coordinator event handling."""
import json
import threading
import time
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QObject, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap, QTextDocument
from PySide6.QtWidgets import (QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QSplitter,QLabel,
    QPushButton,QListWidget,QListWidgetItem,QLineEdit,QPlainTextEdit,QTextBrowser,QCheckBox,
    QFileDialog,QMessageBox,QInputDialog,QDialog,QDialogButtonBox,QTabWidget,QFormLayout,
    QComboBox,QSpinBox,QApplication)

from .attachments import Attachments
from .browser import Browser
from .desktop import Desktop, EmergencyStop,SessionGuard
from .engine import Engine
from .permissions import Permissions, origin
from .storage import Store
from .tools import Broker


class Bridge(QObject):
    event=Signal(str,object,object)


class ChatView(QTextBrowser):
    def __init__(self):
        super().__init__();self.images={}
    def loadResource(self,kind,url):
        # Model Markdown cannot read local files or load remote tracking images.
        return self.images.get(url.toString())


class Composer(QPlainTextEdit):
    send=Signal()
    def keyPressEvent(self,event):
        if event.key() in (Qt.Key_Return,Qt.Key_Enter) and event.modifiers() & Qt.ControlModifier:
            self.send.emit();return
        super().keyPressEvent(event)


def button(text,slot):
    widget=QPushButton(text);widget.clicked.connect(slot);return widget


class ChatWindowBase(QMainWindow):
    def __init__(self,directory=None):
        super().__init__()
        self.setWindowTitle('Codex Desktop Assistant');self.resize(1380,900);self.setMinimumSize(980,640)
        self.store=Store(directory);self.attachments=Attachments(self.store.directory)
        for attachment in self.store.prune(self.store.settings().get('history_days',0)):
            self.attachments.remove(attachment)
        self.permissions=Permissions();self.desktop=Desktop(self.permissions)
        self.browser=Browser(self.store.directory,self.permissions)
        self.bridge=Bridge();self.bridge.event.connect(self.on_event)
        self.broker=Broker(self.permissions,self.desktop,self.browser,self.attachments,self.store,self.emit,self.approve)
        self.engine=Engine(self.store,self.permissions,self.broker,self.emit)
        self.selected=None;self.pending=[];self.requests=[];self.last_preview=None
        self.closing=False;self.approval_dialog=None
        self.setAcceptDrops(True)
        self.build();self.apply_settings();self.load_list()
        self.render_timer=QTimer(self);self.render_timer.setSingleShot(True);self.render_timer.setInterval(80);self.render_timer.timeout.connect(self.render)
        if self.list.count():self.list.setCurrentRow(0)
        else:self.new_chat()
        self.hotkey=EmergencyStop(self.emergency)
        self.session_guard=SessionGuard(lambda:self.emergency('Desktop locked or resumed from sleep. Review the current interface before Resume.'))
        self.permissions.safety_check=self.session_guard.check
        self.timer=QTimer(self);self.timer.timeout.connect(self.refresh_status);self.timer.start(500)
        if not self.hotkey.registered:self.notice.setText('Emergency shortcut unavailable. Check whether Ctrl+Alt+F12 is used by another app; desktop input remains disabled.')
        self.engine.connect()

    def emit(self,kind,conversation,data):self.bridge.event.emit(kind,conversation,data)

    def approve(self,conversation,label,args):
        request={'conversation':conversation,'label':label,'args':args,'event':threading.Event(),'allowed':False,'generation':self.permissions.generation}
        self.requests.append(request);self.emit('request_approval',conversation,request)
        deadline=time.monotonic()+300
        while not request['event'].wait(.1):
            if self.permissions.halted.is_set() or self.engine.stop_event.is_set() or time.monotonic()>deadline:return False
        return request['allowed'] and request['generation']==self.permissions.generation

    def on_event(self,kind,conversation,data):
        if self.closing:return
        if kind=='connection':self.connection.setText(str(data))
        elif kind=='models':
            self.model.blockSignals(True);self.model.clear();self.model.addItem('Account default','')
            for entry in data:self.model.addItem(entry.get('displayName',entry['id']),entry.get('model',entry['id']))
            index=self.model.findData(self.store.settings().get('model',''));self.model.setCurrentIndex(max(0,index));self.model.blockSignals(False)
        elif kind=='request_approval':
            if data['event'].is_set() or self.permissions.halted.is_set():return
            dialog=QMessageBox(self);dialog.setWindowTitle('Review this exact action');dialog.setIcon(QMessageBox.Question)
            self.approval_dialog=dialog
            dialog.setText(str(data['label']));dialog.setInformativeText('Allow this action once? Take Over or Ctrl+Alt+F12 cancels waiting actions.');dialog.setDetailedText(json.dumps(data['args'],ensure_ascii=False,indent=2))
            dialog.setStandardButtons(QMessageBox.Yes|QMessageBox.No);dialog.setDefaultButton(QMessageBox.No)
            data['allowed']=dialog.exec()==QMessageBox.Yes and not self.permissions.halted.is_set();data['event'].set()
            self.approval_dialog=None
        elif kind=='preview' and conversation==self.selected:
            self.last_preview=data;pixmap=QPixmap();pixmap.loadFromData(data)
            self.preview.setPixmap(pixmap.scaled(280,230,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        elif kind=='action':
            self.activity_text.appendPlainText(str(data));self.status.setText('Acting')
        elif kind in ('queued','steered'):
            self.notice.setText('Message saved; '+('accepted into the active turn.' if kind=='steered' else 'queued for Codex.'))
        elif kind=='handoff':self.notice.setText('Your turn: '+str(data))
        elif kind=='error':self.notice.setText(str(data))
        elif kind=='paused':
            self.notice.setText(str(data))
            if self.approval_dialog:self.approval_dialog.done(QMessageBox.No)
        if kind in ('delta','message','idle','queued','steered','handoff','error'):
            if conversation==self.selected:
                if kind=='delta':
                    if not self.render_timer.isActive():self.render_timer.start()
                else:self.render()
            if kind in ('idle','error'):self.load_list()

    def new_chat(self):
        ident=self.store.new();self.archived.setChecked(False);self.load_list();self.choose(ident)

    def load_list(self,*args):
        selected=self.selected;self.list.blockSignals(True);self.list.clear()
        for conversation in self.store.conversations(self.search.text(),self.archived.isChecked()):
            item=QListWidgetItem(('★ ' if conversation['pinned'] else '')+conversation['title']);item.setData(Qt.UserRole,conversation['id']);self.list.addItem(item)
            if conversation['id']==selected:self.list.setCurrentItem(item)
        self.list.blockSignals(False)

    def choose(self,ident):
        for index in range(self.list.count()):
            item=self.list.item(index)
            if item.data(Qt.UserRole)==ident:self.list.setCurrentItem(item);self.select(item,None);return

    def select(self,item,previous):
        if not item:return
        if self.selected!=item.data(Qt.UserRole):self.chat.images.clear()
        self.selected=item.data(Qt.UserRole);self.title.setText(self.store.conversation(self.selected)['title']);self.render()

    def render(self):
        if self.closing or not self.selected:return
        parts=[]
        for message in self.store.messages(self.selected):
            parts.append('### '+{'user':'You','assistant':'Codex','system':'Status'}.get(message['role'],message['role']))
            parts.append(message['text'])
            records=json.loads(message['attachments'])
            if records:
                for record in records:
                    name=record['name'].replace('[','\\[').replace(']','\\]')
                    parts.append(f"[{name}](attachment:{record['id']})")
                    path=self.attachments.path(record)
                    if path.suffix.lower() in ('.png','.jpg','.jpeg','.webp','.bmp','.gif') and path.exists():
                        url='attachment-image:'+record['id']
                        if url not in self.chat.images:self.chat.images[url]=QPixmap(str(path)).scaled(620,360,Qt.KeepAspectRatio,Qt.SmoothTransformation)
                        parts.append(f'![Attached image]({url})')
            if message['state'] not in ('saved','sent'):parts.append('\n*'+message['state']+'*')
        bar=self.chat.verticalScrollBar();bottom=bar.value()>=bar.maximum()-40
        self.chat.setMarkdown('\n\n'.join(parts))
        if bottom:bar.setValue(bar.maximum())

    def send(self):
        try:
            if self.store.conversation(self.selected)['archived']:raise ValueError('Restore this conversation before sending')
            text=self.input.toPlainText();records=list(self.pending)
            self.engine.submit(self.selected,text,records)
            if self.store.conversation(self.selected)['title']=='New conversation' and text.strip():self.store.update(self.selected,title=text.strip().splitlines()[0][:65])
            self.input.clear();self.pending.clear();self.attachment_list.clear();self.load_list();self.render()
        except Exception as error:self.notice.setText(str(error))

    def rename(self):
        if not self.selected:return
        text,ok=QInputDialog.getText(self,'Rename conversation','Name',text=self.store.conversation(self.selected)['title'])
        if ok and text.strip():self.store.update(self.selected,title=text.strip()[:120]);self.title.setText(text);self.load_list()

    def pin(self):
        if self.selected:self.store.update(self.selected,pinned=not self.store.conversation(self.selected)['pinned']);self.load_list()

    def archive(self):
        if self.selected==self.engine.active:self.pause()
        if self.selected:self.store.update(self.selected,archived=not self.store.conversation(self.selected)['archived']);self.load_list()

    def delete_history(self):
        if not self.selected:return
        if self.engine.active==self.selected:self.notice.setText('Stop this task before deleting its local history.');return
        if QMessageBox.question(self,'Delete local history','Delete this conversation and its private attachment copies? Codex-managed rollout retention is separate.',QMessageBox.Yes|QMessageBox.No,QMessageBox.No)!=QMessageBox.Yes:return
        for message in self.store.messages(self.selected):
            for record in json.loads(message['attachments']):self.attachments.remove(record)
        self.store.delete(self.selected);self.selected=None;self.load_list()
        if self.list.count():self.list.setCurrentRow(0)
        else:self.new_chat()

    def pick_files(self):
        files,_=QFileDialog.getOpenFileNames(self,'Attach files');self.add_files(files)

    def add_files(self,files):
        for path in files[:10]:
            try:
                if len(self.pending)>=10:raise ValueError('At most ten attachments per message')
                record=self.attachments.add(path);self.pending.append(record)
                item=QListWidgetItem(record['name']);item.setData(Qt.UserRole,record);self.attachment_list.addItem(item)
            except Exception as error:self.notice.setText(str(error))

    def remove_attachment(self):
        row=self.attachment_list.currentRow()
        if row>=0:self.attachments.remove(self.pending.pop(row));self.attachment_list.takeItem(row)

    def preview_attachment(self,item):
        record=item.data(Qt.UserRole)
        try:
            content=self.attachments.content(record)
            dialog=QDialog(self);dialog.setWindowTitle(record['name']);dialog.resize(700,550);layout=QVBoxLayout(dialog)
            if any(x['type']=='image' for x in content):
                label=QLabel();label.setPixmap(QPixmap(str(self.attachments.path(record))).scaled(650,470,Qt.KeepAspectRatio,Qt.SmoothTransformation));layout.addWidget(label)
            else:
                text=QPlainTextEdit();text.setReadOnly(True);text.setPlainText('\n'.join(x.get('text','') for x in content));layout.addWidget(text)
            layout.addWidget(button('Close',dialog.accept));dialog.exec()
        except Exception as error:self.notice.setText(str(error))

    def dragEnterEvent(self,event):
        if event.mimeData().hasUrls():event.acceptProposedAction()

    def dropEvent(self,event):self.add_files([url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()])

    def pause(self):self.engine.pause()
    def takeover(self):
        self.engine.pause(manual=True)
        if not self.engine.active:self.browser.manual_mode=True
        self.notice.setText('Control disabled. Finish your manual step, then Resume. No new input actions are permitted.')
    def stop(self):
        self.engine.pause();self.permissions.revoke();self.last_preview=None;self.preview.clear();self.preview.setText('Observation off');self.notice.setText('Stopped. All computer grants revoked; re-authorize before computer actions.')
    def emergency(self,reason='Emergency stop: new input disabled. Review before resuming.'):
        self.permissions.halt();self.engine.interrupt.set()
        for request in self.requests:request['event'].set()
        self.emit('paused',self.engine.active,reason)

    def resume(self):
        try:self.engine.resume(self.selected)
        except Exception as error:self.notice.setText(str(error))

    def toggle_observe(self,on):
        if on and not (self.permissions.windows or self.permissions.origins or self.permissions.capture_bounds):self.observation.setChecked(False);self.settings();return
        self.permissions.observe=on
        if not on:self.permissions.generation+=1;self.last_preview=None;self.preview.clear();self.preview.setText('Observation off')

    def capture_preview(self):
        try:
            if not self.permissions.observe:raise ValueError('Enable scoped observation in Settings first')
            if self.permissions.capture_bounds is not None:raw=self.desktop.capture()
            elif len(self.permissions.windows)==1:raw=self.desktop.capture(next(iter(self.permissions.windows)))
            else:
                choices=[x for x in self.desktop.windows() if x['hwnd'] in self.permissions.windows]
                title,ok=QInputDialog.getItem(self,'Preview selected window','Window',[x['title'] for x in choices],editable=False)
                if not ok:return
                raw=self.desktop.capture(next(x['hwnd'] for x in choices if x['title']==title))
            self.last_preview=raw;pixmap=QPixmap();pixmap.loadFromData(raw);self.preview.setPixmap(pixmap.scaled(280,230,Qt.KeepAspectRatio,Qt.SmoothTransformation))
            self.notice.setText('Local preview only. This preview was not sent to Codex.')
        except Exception as error:self.notice.setText(str(error))

    def toggle_desktop(self,on):
        if on and (not self.permissions.windows or not self.hotkey.registered):self.desktop_toggle.setChecked(False);self.settings();return
        self.permissions.desktop=on
        if not on:self.permissions.halt()

    def toggle_browser(self,on):
        if on and not self.permissions.origins:self.browser_toggle.setChecked(False);self.settings();return
        self.permissions.browser=on
        if not on:self.permissions.halt()

    def model_changed(self):
        if self.model.currentData() is not None:self.store.setting('model',self.model.currentData());self.store.setting('effort','')

    def open_link(self,url):
        if url.scheme() in ('http','https'):QDesktopServices.openUrl(url)
        elif url.scheme()=='attachment':
            record=next((a for message in self.store.messages(self.selected) for a in json.loads(message['attachments']) if a['id']==url.path()),None)
            if record:
                item=QListWidgetItem();item.setData(Qt.UserRole,record);self.preview_attachment(item)

    def cedargrid_workflow(self):
        from .workflows import cedargrid
        try:
            instructions,assets=cedargrid(Path(__file__).resolve().parents[3])
            dialog=QDialog(self);dialog.setWindowTitle('Cedargrid draft workflow · local preparation');dialog.resize(820,650);layout=QVBoxLayout(dialog)
            label=QLabel('Review the draft plan and select any assets to attach. Nothing opens Payhip or publishes a listing.');label.setWordWrap(True);layout.addWidget(label)
            preview=QPlainTextEdit(instructions);preview.setReadOnly(True);layout.addWidget(preview,1)
            files=QListWidget()
            for asset in assets:
                item=QListWidgetItem(asset['name']+f" ({asset['bytes']:,} bytes)");item.setData(Qt.UserRole,asset);item.setFlags(item.flags()|Qt.ItemIsUserCheckable);item.setCheckState(Qt.Unchecked);files.addItem(item)
            layout.addWidget(files)
            buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);buttons.button(QDialogButtonBox.Ok).setText('Add reviewed plan to composer');buttons.accepted.connect(dialog.accept);buttons.rejected.connect(dialog.reject);layout.addWidget(buttons)
            if dialog.exec()!=QDialog.Accepted:return
            self.input.setPlainText(instructions)
            self.add_files([files.item(i).data(Qt.UserRole)['path'] for i in range(files.count()) if files.item(i).checkState()==Qt.Checked])
            self.notice.setText('Local Cedargrid workflow prepared for review. No external account was accessed.')
        except Exception as error:self.notice.setText(str(error))

    def refresh_status(self):
        if self.selected:
            conversation=self.store.conversation(self.selected)
            if conversation:self.status.setText(conversation['status'])
        if self.engine.active and self.engine.active!=self.selected:
            active=self.store.conversation(self.engine.active)
            if active:self.status.setText('Working in: '+active['title'][:35])
        p=self.permissions.snapshot()
        self.grants.setText(('PAUSED' if p['paused'] else 'SESSION ENABLED')+f"\nWindows: {len(p['windows'])}\nWebsites: {len(p['origins'])}\nObservation: {'ON' if p['observation'] else 'OFF'}")
        self.observation_indicator.setText('SCREEN OBSERVATION ON' if p['observation'] else 'Observation OFF')
        self.observation_indicator.setStyleSheet('color:#f59e0b;font-weight:600' if p['observation'] else '')
        for widget,value in ((self.observation,p['observation']),(self.desktop_toggle,p['desktop']),(self.browser_toggle,p['browser']),(self.top_desktop,p['desktop']),(self.top_browser,p['browser'])):
            widget.blockSignals(True);widget.setChecked(value);widget.blockSignals(False)

    def apply_settings(self):
        settings=self.store.settings();dark=settings.get('theme','Dark')=='Dark'
        self.desktop.exclusions=settings.get('exclusions',self.desktop.exclusions)
        self.activity.setVisible(settings.get('show_activity',True))
        background='#111827' if dark else '#f1f5f9';surface='#1f2937' if dark else '#ffffff';text='#e5e7eb' if dark else '#172033';border='#374151' if dark else '#cbd5e1'
        self.setStyleSheet(f'''QWidget{{background:{background};color:{text};font-family:Segoe UI;font-size:{settings.get('font_size',12)}pt;}} QTextBrowser,QPlainTextEdit,QListWidget,QLineEdit,QComboBox{{background:{surface};border:1px solid {border};border-radius:7px;padding:8px;}} QPushButton{{background:{surface};border:1px solid {border};border-radius:6px;padding:7px 11px;}} QPushButton:hover{{border-color:#14b8a6;}} QListWidget::item:selected{{background:#115e59;}} QLabel#conversationTitle{{font-size:19pt;font-weight:600;}} QSplitter::handle{{background:{border};width:2px;}}''')

    def closeEvent(self,event):
        self.closing=True;self.timer.stop();self.render_timer.stop()
        self.permissions.revoke()
        for request in self.requests:request['event'].set()
        clean=self.engine.close();self.hotkey.close();self.session_guard.close()
        if clean:self.store.close()
        event.accept()
