"""Native Qt chat UI. All model and automation work runs outside the UI thread."""
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


class MainWindow(QMainWindow):
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

    def build(self):
        root=QWidget();self.setCentralWidget(root);layout=QVBoxLayout(root)
        top=QHBoxLayout();self.connection=QLabel('Connecting…');top.addWidget(self.connection)
        self.model=QComboBox();self.model.setMinimumWidth(160);self.model.currentIndexChanged.connect(self.model_changed);top.addWidget(self.model)
        top.addStretch();self.status=QLabel('Ready');top.addWidget(self.status)
        top.addWidget(button('Start',self.send))
        top.addWidget(button('Pause',self.pause));top.addWidget(button('Resume',self.resume))
        top.addWidget(button('Take Over',self.takeover));top.addWidget(button('Stop',self.stop))
        top.addWidget(button('Settings',self.settings));layout.addLayout(top)
        control_row=QHBoxLayout();self.observation_indicator=QLabel('Observation OFF');control_row.addWidget(self.observation_indicator)
        self.top_desktop=QCheckBox('Windows control');self.top_desktop.toggled.connect(self.toggle_desktop);control_row.addWidget(self.top_desktop)
        self.top_browser=QCheckBox('Browser control');self.top_browser.toggled.connect(self.toggle_browser);control_row.addWidget(self.top_browser);control_row.addStretch();layout.addLayout(control_row)
        split=QSplitter(Qt.Horizontal);layout.addWidget(split,1)
        left=QWidget();side=QVBoxLayout(left);side.addWidget(QLabel('CONVERSATIONS'))
        side.addWidget(button('+ New Chat',self.new_chat))
        self.search=QLineEdit();self.search.setPlaceholderText('Search conversations');self.search.textChanged.connect(self.load_list);side.addWidget(self.search)
        self.archived=QCheckBox('Show archived');self.archived.toggled.connect(self.load_list);side.addWidget(self.archived)
        self.list=QListWidget();self.list.currentItemChanged.connect(self.select);side.addWidget(self.list,1)
        side.addWidget(button('Rename',self.rename));side.addWidget(button('Pin / unpin',self.pin));side.addWidget(button('Archive / restore',self.archive))
        side.addWidget(button('Delete selected history',self.delete_history));split.addWidget(left)
        center=QWidget();chat=QVBoxLayout(center)
        self.title=QLabel('New conversation');self.title.setObjectName('conversationTitle');chat.addWidget(self.title)
        self.chat=ChatView();self.chat.setOpenLinks(False);self.chat.anchorClicked.connect(self.open_link);chat.addWidget(self.chat,1)
        self.notice=QLabel('Computer access is off. Enable scoped access in Settings when needed.');self.notice.setWordWrap(True);chat.addWidget(self.notice)
        self.attachment_list=QListWidget();self.attachment_list.setMaximumHeight(85);self.attachment_list.itemDoubleClicked.connect(self.preview_attachment);chat.addWidget(self.attachment_list)
        self.input=Composer();self.input.setMaximumHeight(140);self.input.setPlaceholderText('Ask Codex to help…  Ctrl+Enter to send. Corrections during work are retained and steered.');self.input.send.connect(self.send);chat.addWidget(self.input)
        row=QHBoxLayout();row.addWidget(button('Attach files',self.pick_files));row.addWidget(button('Remove attachment',self.remove_attachment));row.addStretch();row.addWidget(button('Send',self.send));chat.addLayout(row);split.addWidget(center)
        self.activity=QWidget();right=QVBoxLayout(self.activity);right.addWidget(QLabel('COMPUTER ACTIVITY'))
        self.observation=QCheckBox('Screen observation');self.observation.toggled.connect(self.toggle_observe);right.addWidget(self.observation)
        self.desktop_toggle=QCheckBox('Windows input');self.desktop_toggle.toggled.connect(self.toggle_desktop);right.addWidget(self.desktop_toggle)
        self.browser_toggle=QCheckBox('Dedicated browser');self.browser_toggle.toggled.connect(self.toggle_browser);right.addWidget(self.browser_toggle)
        self.preview=QLabel('No screenshot sent');self.preview.setMinimumSize(220,180);self.preview.setAlignment(Qt.AlignCenter);self.preview.setScaledContents(False);right.addWidget(self.preview)
        right.addWidget(button('Preview approved screen',self.capture_preview))
        self.activity_text=QPlainTextEdit();self.activity_text.setReadOnly(True);right.addWidget(self.activity_text,1)
        self.grants=QLabel();self.grants.setWordWrap(True);right.addWidget(self.grants)
        right.addWidget(QLabel('Emergency stop: Ctrl+Alt+F12'))
        split.addWidget(self.activity);split.setSizes([240,850,290])
        view=self.menuBar().addMenu('View');action=view.addAction('Computer activity');action.setCheckable(True);action.setChecked(True);action.toggled.connect(self.activity.setVisible)
        workflow=self.menuBar().addMenu('Workflows');workflow.addAction('Prepare Cedargrid hidden-listing workflow',self.cedargrid_workflow)

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

    def settings(self):
        dialog=QDialog(self);dialog.setWindowTitle('Assistant settings and session permissions');dialog.resize(800,700);outer=QVBoxLayout(dialog);tabs=QTabWidget();outer.addWidget(tabs)
        codex=QWidget();form=QFormLayout(codex)
        form.addRow('Authentication',QLabel(self.connection.text()))
        effort=QComboBox();effort.addItem('Account default','')
        entry=next((x for x in self.engine.models if x.get('model',x['id'])==self.model.currentData()),{})
        for item in entry.get('supportedReasoningEfforts',[]):effort.addItem(item['reasoningEffort'],item['reasoningEffort'])
        effort.setCurrentIndex(max(0,effort.findData(self.store.settings().get('effort',''))));form.addRow('Reasoning effort',effort)
        form.addRow(QLabel('Each conversation has its own saved Codex thread. Active tasks are never automatically replayed after a crash.'))
        tabs.addTab(codex,'Codex')
        desktop=QWidget();d=QVBoxLayout(desktop);d.addWidget(QLabel('Select exact windows for this session. Access is revoked at restart.'))
        windows=QListWidget();d.addWidget(windows)
        try:
            for window in self.desktop.windows():
                item=QListWidgetItem(window['title']);item.setData(Qt.UserRole,window);item.setFlags(item.flags()|Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked if window['hwnd'] in self.permissions.windows else Qt.Unchecked);windows.addItem(item)
        except Exception as error:d.addWidget(QLabel(str(error)))
        observe=QCheckBox('Allow screenshot observation of selected windows (sent to your Codex account)');observe.setChecked(self.permissions.observe);d.addWidget(observe)
        capture=QComboBox();capture.addItem('Selected windows only',None)
        try:
            monitors=self.desktop.monitors()
            for index,bounds in enumerate(monitors):capture.addItem(('All monitors' if index==len(monitors)-1 else 'Monitor '+str(index+1))+' '+str(bounds),bounds)
            capture.setCurrentIndex(max(0,capture.findData(self.permissions.capture_bounds)))
        except Exception:pass
        d.addWidget(QLabel('Optional broader capture scope (input remains limited to selected windows)'));d.addWidget(capture)
        desktop_input=QCheckBox('Allow input in selected windows');desktop_input.setChecked(self.permissions.desktop);d.addWidget(desktop_input)
        applications=dict(self.permissions.applications)
        app_list=QListWidget();app_list.addItems(list(applications));d.addWidget(app_list)
        def approve_application():
            path,_=QFileDialog.getOpenFileName(self,'Approve an existing installed application executable',filter='Windows applications (*.exe)')
            if path:applications[Path(path).stem]=str(Path(path).resolve());app_list.clear();app_list.addItems(list(applications))
        d.addWidget(button('Approve application launch',approve_application))
        d.addWidget(QLabel('Ctrl+Alt+F12 stops new input globally. Coordinate actions require individual review.'))
        exclusions=QLineEdit(','.join(self.desktop.exclusions));d.addWidget(QLabel('Exclude titles containing (comma separated)'));d.addWidget(exclusions)
        tabs.addTab(desktop,'Desktop')
        browser=QWidget();b=QVBoxLayout(browser)
        b.addWidget(QLabel('Dedicated persistent Chromium profile. Sign in manually after Take Over. Ordinary browser cookies are never imported.'))
        origins=QPlainTextEdit('\n'.join(sorted(self.permissions.origins)));origins.setPlaceholderText('Approved origins, one per line. Example: https://payhip.com');b.addWidget(origins)
        browser_input=QCheckBox('Allow dedicated browser for these origins');browser_input.setChecked(self.permissions.browser);b.addWidget(browser_input)
        b.addWidget(QLabel('Unapproved origins, mutation requests and WebSockets are blocked. Approve necessary site origins explicitly.'))
        tabs.addTab(browser,'Browser')
        privacy=QWidget();p=QVBoxLayout(privacy)
        p.addWidget(QLabel('Chat and attachments stay in your private Windows profile. Screenshots are not written by this app. Codex may retain image inputs in its own conversation rollout; this app cannot promise zero provider/runtime retention.'))
        retention=QComboBox()
        for label,days in (('Until I delete them',0),('7 days',7),('30 days',30),('90 days',90),('365 days',365)):retention.addItem(label,days)
        retention.setCurrentIndex(max(0,retention.findData(self.store.settings().get('history_days',0))))
        p.addWidget(QLabel('Local history and attachment retention (cleanup at next startup)'));p.addWidget(retention)
        labels=QPlainTextEdit('\n'.join(sorted(self.permissions.routine_labels)));labels.setPlaceholderText('Exact harmless control labels allowed without repeated confirmation, one per line');p.addWidget(QLabel('Bounded routine actions (session only; consequential labels still require approval)'));p.addWidget(labels)
        file_list=QListWidget();p.addWidget(QLabel('Exact approved local files'));p.addWidget(file_list)
        file_grants=dict(self.permissions.files)
        def show_files():file_list.clear();file_list.addItems([mode+'  '+path for path,mode in file_grants.items()])
        def add_file(write=False):
            path,_=(QFileDialog.getSaveFileName(self,'Approve exact file for read/write') if write else QFileDialog.getOpenFileName(self,'Approve exact file for reading'))
            if path:file_grants[str(Path(path).resolve())]='write' if write else 'read';show_files()
        p.addWidget(button('Approve file read',lambda:add_file(False)));p.addWidget(button('Approve file read/write',lambda:add_file(True)))
        def revoke_dialog():
            self.stop();origins.clear();labels.clear();file_grants.clear();applications.clear();file_list.clear();app_list.clear()
            observe.setChecked(False);desktop_input.setChecked(False);browser_input.setChecked(False);capture.setCurrentIndex(0)
            for index in range(windows.count()):windows.item(index).setCheckState(Qt.Unchecked)
        p.addWidget(button('Revoke all session access',revoke_dialog));show_files();tabs.addTab(privacy,'Privacy and files')
        interface=QWidget();f=QFormLayout(interface);theme=QComboBox();theme.addItems(['Dark','Light']);theme.setCurrentText(self.store.settings().get('theme','Dark'));f.addRow('Theme',theme)
        font=QSpinBox();font.setRange(10,24);font.setValue(self.store.settings().get('font_size',12));f.addRow('Font size',font)
        preview=QCheckBox('Show activity panel');preview.setChecked(self.activity.isVisible());f.addRow(preview)
        tabs.addTab(interface,'Interface')
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel);buttons.accepted.connect(dialog.accept);buttons.rejected.connect(dialog.reject);outer.addWidget(buttons)
        if dialog.exec()!=QDialog.Accepted:return
        try:
            approved_origins={origin(x.strip()) for x in origins.toPlainText().splitlines() if x.strip()}
            approved_windows={}
            for index in range(windows.count()):
                item=windows.item(index)
                if item.checkState()==Qt.Checked:
                    window=item.data(Qt.UserRole);approved_windows[window['hwnd']]=self.desktop.identity(window['hwnd'])
            self.permissions.halt()
            with self.permissions.lock:
                self.permissions.windows=approved_windows;self.permissions.origins=approved_origins
                self.permissions.capture_bounds=capture.currentData();self.permissions.applications=applications
                self.permissions.files=file_grants;self.permissions.routine_labels={x.strip().lower() for x in labels.toPlainText().splitlines() if x.strip()}
                self.permissions.observe=observe.isChecked();self.permissions.desktop=desktop_input.isChecked() and self.hotkey.registered
                self.permissions.browser=browser_input.isChecked()
                self.desktop.exclusions=[x.strip() for x in exclusions.text().split(',') if x.strip()]
            if self.engine.active and self.engine.active!=self.selected:self.engine.pause()
            self.permissions.resume(self.selected)
            for key,value in (('theme',theme.currentText()),('font_size',font.value()),('effort',effort.currentData()),('exclusions',self.desktop.exclusions),('show_activity',preview.isChecked()),('history_days',retention.currentData())):self.store.setting(key,value)
            self.store.setting('last_reviewed_scopes',{'origins':sorted(approved_origins),'files':file_grants,'applications':applications,'capture_bounds':capture.currentData(),'enabled_after_restart':False})
            self.apply_settings();self.notice.setText('Session access enabled for the selected conversation and exact scopes. Pause or Take Over revokes active input immediately.')
        except Exception as error:self.notice.setText(str(error))

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
