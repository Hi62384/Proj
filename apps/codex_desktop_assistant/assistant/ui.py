"""Everyday assistant interface; local controls are the sole authority writer.

The stable history/attachment/engine lifecycle is inherited from ui_base.
"""
import html
import json
import threading
import time
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap,QTextDocument
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QSplitter,QLabel,
    QPushButton,QListWidget,QLineEdit,QPlainTextEdit,QCheckBox,QFileDialog,QMessageBox,
    QDialog,QDialogButtonBox,QFormLayout,QComboBox,QSpinBox,QStyle,QScrollArea)
from .ui_base import ChatWindowBase as BaseWindow,ChatView,Composer,button as base_button
from .attention import Attention,InputGuard
from .file_policy import FilePolicy,ACTIONS,DECISIONS
from PySide6.QtWidgets import QGroupBox,QTableWidget,QHeaderView


def button(text,slot):
    widget=base_button(text,slot)
    icon={'Pause':QStyle.SP_MediaPause,'Resume':QStyle.SP_MediaPlay,'Stop':QStyle.SP_MediaStop,
          'Refresh':QStyle.SP_BrowserReload,'Settings':QStyle.SP_FileDialogDetailedView,
          'Permissions':QStyle.SP_DialogApplyButton,'Attach':QStyle.SP_FileIcon,
          'Send':QStyle.SP_ArrowForward,'Requests':QStyle.SP_MessageBoxInformation}.get(text)
    if icon is not None:widget.setIcon(widget.style().standardIcon(icon))
    return widget


class MainWindow(BaseWindow):
    def __init__(self,directory=None):
        self.models_catalog=[];self.pause_reason='';self.request_cards=[]
        super().__init__(directory)
        self.permissions.file_policy=FilePolicy(self.store.settings().get('file_rules',[]))
        self.attention=Attention(self)
        self.input_guard=InputGuard(self.permissions,lambda:bool(self.engine.active and self.engine.turn),self.focus_pause)
        self.permissions.input_check=self.input_guard.check;self.broker.input_guard=self.input_guard
        self.permissions.input_coordinator=self.input_guard
        self.input_guard.waiting=lambda message:self.emit('input_access',getattr(self.permissions.execution_context,'conversation',self.engine.active),message)
        from .storage import private_directory
        if self.store.directory.resolve()==private_directory().resolve() and (private_directory()/'chrome-host/settings.json').is_file():
            try:self.broker.chrome.bridge.start()
            except Exception as error:self.notice.setText('Chrome bridge needs attention: '+str(error))

    def build(self):
        root=QWidget();self.setCentralWidget(root);layout=QVBoxLayout(root);layout.setContentsMargins(14,12,14,12);layout.setSpacing(10)
        top=QHBoxLayout();top.addWidget(QLabel('Model'))
        self.connection=QLabel('Connecting…');self.connection.setToolTip('Uses your existing ChatGPT account')
        self.model=QComboBox();self.model.setMinimumWidth(150);self.model.currentIndexChanged.connect(self.model_changed);top.addWidget(self.model)
        top.addWidget(QLabel('Reasoning'));self.effort=QComboBox();self.effort.setMinimumWidth(105);self.effort.currentIndexChanged.connect(self.effort_changed);top.addWidget(self.effort)
        top.addStretch();self.status=QLabel('Ready');self.status.setMinimumWidth(140);top.addWidget(self.status)
        self.task_controls=QWidget();task_row=QHBoxLayout(self.task_controls);task_row.setContentsMargins(0,0,0,0)
        for label,slot in [('Continue',self.resume),('Stop',self.stop)]:task_row.addWidget(button(label,slot))
        self.attention_button=button('Requests',lambda:self.attention.open());self.attention_button.setMinimumWidth(125);top.addWidget(self.attention_button)
        top.addWidget(button('Permissions',self.file_permissions));top.addWidget(button('Settings',self.settings));layout.addLayout(top)
        controls=QHBoxLayout();controls.addWidget(QLabel('Desktop Access'))
        self.access_mode=QComboBox();self.access_mode.addItems(['Selected Window','Entire Monitor']);self.access_mode.currentIndexChanged.connect(self.refresh_targets);controls.addWidget(self.access_mode)
        self.access_target=QComboBox();self.access_target.setMinimumWidth(180);self.access_target.setMaximumWidth(330);controls.addWidget(self.access_target,1)
        controls.addWidget(button('Refresh',self.refresh_targets));controls.addWidget(button('Enable Access',self.enable_access));controls.addWidget(button('Revoke',self.revoke_desktop))
        self.launch_toggle=QCheckBox('Allow Program Launches');self.launch_toggle.toggled.connect(self.toggle_launches);controls.addWidget(self.launch_toggle)
        self.observation_indicator=QLabel('Observation OFF');controls.addWidget(self.observation_indicator);layout.addLayout(controls)
        split=QSplitter(Qt.Horizontal);layout.addWidget(split,1)
        self.sidebar=QWidget();side=QVBoxLayout(self.sidebar);side.setContentsMargins(0,0,8,0)
        side.addWidget(button('+ New Chat',self.new_chat));self.search=QLineEdit();self.search.setPlaceholderText('Search chats');self.search.textChanged.connect(self.load_list);side.addWidget(self.search)
        self.archived=QCheckBox('Archived chats');self.archived.toggled.connect(self.load_list);side.addWidget(self.archived)
        self.list=QListWidget();self.list.currentItemChanged.connect(self.select);side.addWidget(self.list,1)
        for label,slot in [('Rename',self.rename),('Pin / unpin',self.pin),('Archive / restore',self.archive),('Delete history',self.delete_history)]:side.addWidget(button(label,slot))
        split.addWidget(self.sidebar)
        center=QWidget();chat=QVBoxLayout(center);chat.setContentsMargins(12,0,12,0)
        self.title=QLabel('New conversation');self.title.setObjectName('conversationTitle');chat.addWidget(self.title)
        self.chat=ChatView();self.chat.setOpenLinks(False);self.chat.anchorClicked.connect(self.open_link);chat.addWidget(self.chat,1)
        self.approvals_widget=QWidget();self.approvals_layout=QVBoxLayout(self.approvals_widget);self.approvals_layout.setContentsMargins(0,0,0,0);chat.addWidget(self.approvals_widget);self.approvals_widget.hide()
        self.notice=QLabel('Choose a window or monitor above when your task needs computer access.');self.notice.setWordWrap(True);chat.addWidget(self.notice)
        self.attachment_list=QListWidget();self.attachment_list.setMaximumHeight(65);self.attachment_list.itemDoubleClicked.connect(self.preview_attachment);chat.addWidget(self.attachment_list)
        self.input=Composer();self.input.setMaximumHeight(125);self.input.setPlaceholderText('Message Codex…  Ctrl+Enter to send');self.input.send.connect(self.send);chat.addWidget(self.input)
        row=QHBoxLayout();row.addWidget(button('Attach',self.pick_files));row.addWidget(button('Remove attachment',self.remove_attachment));row.addStretch();send=button('Send',self.send);send.setObjectName('send');row.addWidget(send);chat.addLayout(row);split.addWidget(center)
        self.activity=QWidget();right=QVBoxLayout(self.activity);right.setContentsMargins(8,0,0,0);right.addWidget(QLabel('COMPUTER ACTIVITY'))
        self.activity_summary=QLabel('No computer task running');self.activity_summary.setWordWrap(True);right.addWidget(self.activity_summary)
        self.active_application=QLabel('Application: —');self.active_application.setWordWrap(True);right.addWidget(self.active_application)
        self.browser_toggle=QCheckBox('Dedicated browser');self.browser_toggle.toggled.connect(self.toggle_browser);right.addWidget(self.browser_toggle)
        self.dedicated_widgets=[self.browser_toggle]
        self.browser_mode=QComboBox();self.browser_mode.addItems(['Dedicated Browser','Existing Chrome']);self.browser_mode.currentIndexChanged.connect(self.select_browser_mode);right.addWidget(self.browser_mode)
        self.chrome_panel=QGroupBox('Chrome Connection');chrome_layout=QVBoxLayout(self.chrome_panel)
        self.chrome_connection=QLabel('Extension disconnected');self.chrome_connection.setWordWrap(True);chrome_layout.addWidget(self.chrome_connection)
        for label,slot in [('Connect Chrome',self.connect_chrome),('Chrome Tabs / Select Window',self.chrome_tabs),('Attach Tab',self.chrome_attach),('Release Tab',self.chrome_release),('Show Tab',self.chrome_show),('Check Connection',self.chrome_health)]:chrome_layout.addWidget(button(label,slot))
        self.chrome_manual=QCheckBox('Manual Control for Chrome Tab');self.chrome_manual.toggled.connect(self.chrome_manual_control);chrome_layout.addWidget(self.chrome_manual)
        self.chrome_panel.hide();right.addWidget(self.chrome_panel)
        self.chrome_dialog=None;self.chrome_selected_tab=None
        for label,operation in [('Open Browser','open'),('Show Browser','show'),('Browser Tabs','tabs')]:
            control=button(label,lambda checked=False,op=operation:self.browser_control(op));right.addWidget(control);self.dedicated_widgets.append(control)
        self.background_browser=QCheckBox('Work in Background');self.background_browser.setChecked(True)
        self.background_browser.toggled.connect(lambda on:self.browser_control('background',enabled=on));right.addWidget(self.background_browser)
        self.manual_browser=QCheckBox('Manual Control');self.manual_browser.toggled.connect(self.browser_manual);right.addWidget(self.manual_browser)
        self.public_browser=QCheckBox('Public browsing for this session')
        self.public_browser.setToolTip('Public websites may load without a separate site request. Account pages and consequential changes still require authorization.')
        self.public_browser.toggled.connect(lambda on:self.browser_control('public',enabled=on));right.addWidget(self.public_browser)
        self.browser_tabs_state=[];self.browser_tabs_dialog=None
        self.dedicated_widgets.extend([self.manual_browser,self.public_browser])
        self.preview=QLabel('Screen preview');self.preview.setMinimumSize(200,160);self.preview.setAlignment(Qt.AlignCenter);right.addWidget(self.preview)
        right.addWidget(button('Preview approved screen',self.capture_preview))
        self.grants=QLabel();self.grants.setWordWrap(True);right.addWidget(self.grants)
        history=QGroupBox('Activity History');history.setCheckable(True);history.setChecked(False);history_layout=QVBoxLayout(history)
        self.activity_text=QPlainTextEdit();self.activity_text.setReadOnly(True);self.activity_text.hide();history_layout.addWidget(self.activity_text);history.toggled.connect(self.activity_text.setVisible);right.addWidget(history);right.addStretch()
        right.addWidget(QLabel('Emergency stop · Ctrl+Alt+F12'))
        activity_content=self.activity;self.activity=QScrollArea();self.activity.setWidgetResizable(True);self.activity.setWidget(activity_content);split.addWidget(self.activity);split.setSizes([210,850,290])
        footer=QHBoxLayout();footer.addWidget(button('Chats',lambda:self.sidebar.setVisible(not self.sidebar.isVisible())));footer.addWidget(self.connection);footer.addStretch();footer.addWidget(self.task_controls);footer.addWidget(button('Activity',lambda:self.activity.setVisible(not self.activity.isVisible())));layout.addLayout(footer)
        # Retain internal compatibility while removing redundant visible toggles.
        for name in ('observation','desktop_toggle','top_desktop','top_browser'):
            widget=QCheckBox(self);widget.hide();setattr(self,name,widget)
        workflow=self.menuBar().addMenu('Workflows');workflow.addAction('Prepare Cedargrid draft',self.cedargrid_workflow)
        self.refresh_targets()

    def refresh_targets(self):
        self.access_target.clear()
        try:
            if self.access_mode.currentText()=='Selected Window':
                for window in self.desktop.windows():self.access_target.addItem(window['title'],window)
            else:
                monitors=self.desktop.monitors()
                for i,bounds in enumerate(monitors[:-1]):self.access_target.addItem(f'Monitor {i+1} · {bounds[2]-bounds[0]} × {bounds[3]-bounds[1]}',bounds)
                if len(monitors)>2:self.access_target.addItem('All monitors',monitors[-1])
        except Exception as error:self.access_target.addItem('Unable to list targets');self.access_target.setToolTip(str(error))

    def enable_access(self):
        try:
            if not self.hotkey.registered:raise ValueError('Emergency stop is unavailable; resolve the Ctrl+Alt+F12 conflict first')
            target=self.access_target.currentData()
            if target is None:raise ValueError('Choose an available target')
            if not self.store.settings().get('screenshot_consent',False):
                if QMessageBox.question(self,'Screen observation','Authorized screenshots may be sent to your Codex account as needed. Provider and runtime retention apply. Allow this?',QMessageBox.Yes|QMessageBox.No,QMessageBox.No)!=QMessageBox.Yes:return
                self.store.setting('screenshot_consent',True)
            self.permissions.halt()
            with self.permissions.lock:
                self.permissions.windows.clear();self.permissions.capture_bounds=None
                self.permissions.desktop_mode=self.access_mode.currentText()
                self.permissions.desktop_target_name=self.access_target.currentText()
                if self.permissions.desktop_mode=='Selected Window':self.permissions.windows[target['hwnd']]=self.desktop.identity(target['hwnd'])
                else:
                    self.permissions.capture_bounds=tuple(target);self.permissions.monitor_layout=tuple(self.desktop.monitors())
                self.permissions.observe=self.permissions.desktop=True;self.permissions.desktop_suspended=False
                self.permissions.allow_launches=self.launch_toggle.isChecked()
            if self.engine.active and self.engine.active!=self.selected:self.engine.pause()
            self.permissions.resume(self.selected);self.pause_reason=''
            self.notice.setText('Access enabled for '+self.access_target.currentText()+'. Opening chat during a computer task pauses input.');self.refresh_status()
        except Exception as error:self.notice.setText(str(error))

    def revoke_desktop(self):
        self.permissions.generation+=1
        with self.permissions.lock:
            self.permissions.windows.clear();self.permissions.capture_bounds=None;self.permissions.desktop=self.permissions.observe=False;self.permissions.allow_launches=False
        self.launch_toggle.setChecked(False);self.notice.setText('Desktop access revoked.');self.refresh_status()

    def toggle_browser(self,on):
        self.permissions.generation+=1;self.permissions.browser=bool(on)

    def browser_manual(self,on):
        # Immediate hold: queued model calls cannot race the owner taking over.
        self.permissions.browser_manual=bool(on)
        self.broker.browser.observation=None
        if not on:self.broker.browser.edit_until=time.monotonic()+30
        self.browser_control('manual',enabled=on)
        self.notice.setText('Manual Control: use the browser yourself. Turn this off when finished; Codex must inspect again.' if on else 'Browser control returned. Codex will inspect before continuing.')

    def browser_control(self,operation,**args):
        if self.broker.chrome.mode:
            if operation in ('open','show'):self.chrome_show()
            elif operation=='tabs':self.chrome_tabs()
            elif operation=='background' and not args.get('enabled'):self.chrome_show()
            return
        if self.engine.active and self.engine.active!=self.selected:
            self.notice.setText('Open the active chat before changing its browser controls.');return
        if operation in ('open','show','new_tab'):
            if self.permissions.halted.is_set() or self.permissions.owner!=self.selected:self.permissions.resume(self.selected)
            self.permissions.browser=True
            self.browser_toggle.blockSignals(True);self.browser_toggle.setChecked(True);self.browser_toggle.blockSignals(False)
        if operation=='public':self.permissions.public_browsing=bool(args['enabled'])
        self.engine.queue.put(('browser_ui',self.selected,{'operation':operation,**args}))

    def show_browser_tabs(self):
        dialog=QDialog(self);dialog.setWindowTitle('Browser Tabs');dialog.resize(650,380);layout=QVBoxLayout(dialog)
        listing=QListWidget();layout.addWidget(listing);self.browser_tabs_dialog=(dialog,listing)
        url=QLineEdit();url.setPlaceholderText('https://website.example — opens with your authorization');layout.addWidget(url)
        row=QHBoxLayout()
        def chosen(op):
            item=listing.currentItem()
            if item:self.browser_control(op,tab=item.data(Qt.UserRole))
        row.addWidget(button('Switch',lambda:chosen('tab')));row.addWidget(button('Close tab',lambda:chosen('close_tab')))
        row.addWidget(button('New tab',lambda:self.browser_control('new_tab',url=url.text().strip())))
        row.addWidget(button('Refresh',lambda:self.browser_control('tabs')));layout.addLayout(row)
        self.update_browser_tabs();dialog.finished.connect(lambda _:setattr(self,'browser_tabs_dialog',None));dialog.show()

    def update_browser_tabs(self):
        if not self.browser_tabs_dialog:return
        listing=self.browser_tabs_dialog[1];listing.clear()
        from PySide6.QtWidgets import QListWidgetItem
        for tab in self.browser_tabs_state:
            item=QListWidgetItem(('● ' if tab['active'] else '')+tab['title']+'\n'+tab['url']);item.setData(Qt.UserRole,tab['tab']);listing.addItem(item)

    def toggle_launches(self,on):
        self.permissions.generation+=1;self.permissions.allow_launches=bool(on)
        self.notice.setText('Ordinary installed programs may be launched within this session.' if on else 'Program launching disabled.')

    def select_browser_mode(self):
        existing=self.browser_mode.currentText()=='Existing Chrome';self.broker.chrome.mode=existing;self.permissions.chrome_mode=existing;self.chrome_panel.setVisible(existing)
        for widget in self.dedicated_widgets:widget.setVisible(not existing)
        self.notice.setText('Existing Chrome uses only extension-authorized tabs attached to this chat. DOM operations leave your active tab and physical input alone.' if existing else 'Dedicated Browser selected.')

    def connect_chrome(self):
        try:
            import subprocess,sys
            from PySide6.QtCore import QUrl
            from PySide6.QtGui import QDesktopServices
            setup=Path(__file__).resolve().parents[1]/'tools/setup_chrome.py'
            result=subprocess.run([sys.executable,str(setup),'install'],capture_output=True,text=True,timeout=20,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            if result.returncode:raise ValueError('Chrome setup failed. Run Setup_Chrome.cmd for diagnostics.')
            self.broker.chrome.bridge.start()
            self.notice.setText('Native host is registered for this Windows user. In Chrome, open chrome://extensions, enable Developer mode, choose Load unpacked, and select '+str(setup.parent.parent/'chrome_extension')+'. Then open the extension popup and Connect. Installation is verified only after a real connection.')
            QDesktopServices.openUrl(QUrl('chrome://extensions/'))
        except Exception as error:self.notice.setText(str(error))

    def chrome_tabs(self):
        if self.chrome_dialog:self.chrome_dialog.close()
        state=self.broker.chrome.status()
        dialog=QDialog(self);dialog.setWindowTitle('Chrome Tabs');dialog.resize(660,440);layout=QVBoxLayout(dialog)
        note=QLabel('Only extension-authorized tabs show a site. Use the extension popup on each website to authorize it. Attach binds a tab to this chat; a window selection does not grant unrelated tabs.');note.setWordWrap(True);layout.addWidget(note)
        listing=QListWidget();layout.addWidget(listing)
        from PySide6.QtWidgets import QListWidgetItem
        for tab in state['tabs']:
            item=QListWidgetItem('Window '+str(tab.get('window','?'))+' · Tab '+str(tab['tab'])+' · '+tab['origin']+(' · Manual' if tab.get('manual') else ''));item.setData(Qt.UserRole,tab['tab']);listing.addItem(item)
        def selected():
            items=listing.selectedItems()
            if items:self.chrome_selected_tab=items[0].data(Qt.UserRole)
            elif listing.currentItem():self.chrome_selected_tab=listing.currentItem().data(Qt.UserRole)
        listing.currentItemChanged.connect(lambda *_:selected())
        listing.itemSelectionChanged.connect(selected)
        row=QHBoxLayout()
        for label,slot in [('Attach Tab',self.chrome_attach),('Release Tab',self.chrome_release),('Show Tab',self.chrome_show)]:row.addWidget(button(label,slot))
        layout.addLayout(row);self.chrome_dialog=dialog;dialog.show()

    def chrome_attach(self):
        try:
            tab=self.chrome_selected_tab
            if tab is None:raise ValueError('Choose an authorized tab in Chrome Tabs first.')
            if self.engine.active and self.engine.active!=self.selected:raise ValueError('Select the active chat before attaching its Chrome tab.')
            if self.permissions.halted.is_set() or self.permissions.owner!=self.selected:self.permissions.resume(self.selected)
            self.broker.chrome.attach(self.selected,tab,ask=False);self.chrome_connection.setText('Attached Chrome tab '+str(tab)+' to this chat.');self.notice.setText('Authorized page content may be sent to your Codex account. Purchases, publication, sensitive actions and file transfers remain separately reviewed.')
        except Exception as error:self.notice.setText(str(error))

    def chrome_release(self):
        tab=self.chrome_selected_tab or self.broker.chrome.selected
        if tab is None:return
        self.broker.chrome.grants.pop(tab,None)
        self.chrome_job('release',{'tab':tab})

    def chrome_job(self,operation,args):
        # Transport work stays off Qt and off the Playwright owning thread.
        def work():
            try:
                result=self.broker.chrome.bridge.request(operation,args);self.emit('chrome_status',None,self.broker.chrome.status())
                if operation=='list_windows':self.emit('chrome_health',None,'Chrome connection verified by a real round trip · '+str(len(result.get('windows',[])))+' window(s).')
            except Exception as error:self.emit('chrome_error',None,str(error))
        self.engine.host_pool.submit(work)

    def chrome_show(self):
        tab=self.chrome_selected_tab or self.broker.chrome.selected
        if tab is not None:self.chrome_job('show',{'tab':tab})

    def chrome_manual_control(self,on):
        tab=self.chrome_selected_tab or self.broker.chrome.selected
        if tab is None:return
        with self.broker.chrome.bridge.lock:
            if tab in self.broker.chrome.bridge.offers:self.broker.chrome.bridge.offers[tab]['manual']=bool(on)
        self.broker.chrome.observations.clear();self.chrome_job('manual',{'tab':tab,'enabled':bool(on)})
        self.notice.setText('Chrome tab is yours. Return control when finished; Codex must inspect again.' if on else 'Chrome control returned. Inspect the current page before continuing.')

    def chrome_health(self):self.chrome_job('list_windows',{})

    def model_changed(self):
        model=self.model.currentData()
        if model is None:return
        previous=self.store.settings().get('effort','');entry=next((x for x in self.models_catalog if x.get('model',x['id'])==model),{})
        efforts=[x['reasoningEffort'] for x in entry.get('supportedReasoningEfforts',[])]
        chosen=previous if previous in efforts else entry.get('defaultReasoningEffort','')
        if chosen not in efforts:chosen=efforts[0] if efforts else ''
        self.effort.blockSignals(True);self.effort.clear()
        for value in efforts:self.effort.addItem({'xhigh':'Extra High'}.get(value,value.replace('_',' ').title()),value)
        self.effort.setCurrentIndex(self.effort.findData(chosen));self.effort.blockSignals(False)
        self.store.selection(model,chosen)
        if previous and chosen!=previous:self.notice.setText('Reasoning changed to '+(chosen or 'default')+' for this model. Applies next turn.')

    def effort_changed(self):
        if self.effort.currentData() is not None:self.store.setting('effort',self.effort.currentData());self.notice.setText('Reasoning saved for the next turn.')

    def focus_pause(self,reason):
        # Compatibility callback only. Ordinary focus/input never changes authority
        # or interrupts a model turn; InputGuard coordinates individual actions.
        return

    def stop(self):
        self.permissions.halt()
        self.broker.chrome.stop()
        super().stop();self.pause_reason='';self.engine.state(self.selected,'Stopped');self.status.setText('Stopped')

    def emergency(self,reason='Emergency stop. New input is disabled; review before continuing.'):
        self.permissions.halt()
        self.broker.chrome.stop()
        self.permissions.halt();self.engine.interrupt.set()
        if self.engine.turn_cancel:self.engine.turn_cancel.set()
        for request in self.requests:request['event'].set()
        self.engine.state(self.engine.active or self.selected,'Stopped')
        self.emit('paused',self.engine.active,reason)

    def resume(self):
        self.pause_reason=''
        if self.engine.active:
            self.notice.setText('Complete the requested step and choose Done — Continue above.' if any(r['args'].get('manual_step') and not r['event'].is_set() and r['conversation']==self.selected for r in self.requests) else 'The current task is still running.');return
        super().resume()

    def send(self):
        text=self.input.toPlainText().strip().lower().rstrip('.!')
        manual=next((r for r in self.requests if r['conversation']==self.selected and r['args'].get('manual_step') and not r['event'].is_set()),None)
        if manual and text in ('done','continue','resume'):
            valid=manual['generation']==self.permissions.generation and not self.permissions.halted.is_set() and time.monotonic()<=manual['deadline']
            if not valid:self.notice.setText('That request expired or was stopped. Review the task before continuing.');return
            self.store.add(self.selected,'user',self.input.toPlainText(),'sent')
            manual['allowed']=True;manual['event'].set();self.input.clear();self.refresh_requests();self.render();return
        super().send()

    def approve(self,conversation,label,args):
        generation=getattr(self.permissions.execution_context,'generation',self.permissions.generation)
        if generation!=self.permissions.generation or self.permissions.cancelled():return False
        request={'conversation':conversation,'label':label,'args':dict(args),'event':threading.Event(),
                 'allowed':False,'generation':generation,'deadline':time.monotonic()+300}
        self.requests.append(request);self.engine.waiting(conversation,1);self.emit('request_approval',conversation,request)
        try:
            while not request['event'].wait(.1):
                self.engine.pump_steering(conversation)
                if request['generation']!=self.permissions.generation or self.permissions.halted.is_set() or self.permissions.cancelled() or self.engine.stop_event.is_set() or time.monotonic()>request['deadline']:
                    request['event'].set();self.emit('request_expired',conversation,None);return False
            return request['allowed'] and not self.permissions.cancelled() and request['generation']==self.permissions.generation and time.monotonic()<=request['deadline']
        finally:self.engine.waiting(conversation,-1)

    def on_event(self,kind,conversation,data):
        if self.closing:return
        if kind=='chrome_status':
            self.chrome_connection.setText(('Extension connected · '+str(len(data.get('tabs',[])))+' authorized tab(s)') if data.get('connected') else 'Extension disconnected. Reconnect and reauthorize tabs. '+data.get('error',''))
            return
        if kind=='chrome_error':self.notice.setText('Chrome: '+str(data));return
        if kind=='chrome_health':self.notice.setText(str(data));return
        if kind=='browser_state':
            self.browser_tabs_state=data['tabs'];self.update_browser_tabs()
            if data.get('show_tabs') and not self.browser_tabs_dialog:self.show_browser_tabs()
            self.refresh_status();return
        if kind=='browser_error':self.notice.setText('Browser: '+str(data));return
        if kind=='connection':
            self.connection.setToolTip(str(data));self.connection.setText('Connected · ChatGPT' if str(data).startswith('Connected') else 'Connecting…' if str(data).startswith(('Connecting','Windows Linux startup retry')) else 'Connection needs attention');return
        if kind=='models':
            self.models_catalog=list(data);self.model.blockSignals(True);self.model.clear()
            for entry in data:self.model.addItem(entry.get('displayName',entry['id']),entry.get('model',entry['id']))
            index=self.model.findData(self.store.settings().get('model',''))
            if index<0:index=next((i for i,x in enumerate(data) if x.get('isDefault')),0)
            self.model.setCurrentIndex(index);self.model.blockSignals(False);self.model_changed();return
        if kind=='request_approval':
            if not data['event'].is_set() and data['generation']==self.permissions.generation and not self.permissions.halted.is_set():
                self.show_request(data);self.attention.notify('input',id(data),data['args'].get('notification_kind',data['args'].get('operation')))
            return
        if kind=='request_expired':self.refresh_requests();return
        if kind=='started' and not self.permissions.halted.is_set() and not self.permissions.desktop_suspended:self.pause_reason=''
        if kind=='computer_target':self.active_application.setText('Application: '+str(data));return
        if kind=='focus_paused':return
        if kind=='task_state' and conversation==self.selected:self.status.setText(str(data));return
        if kind=='input_access':
            if conversation==self.selected:self.activity_summary.setText(str(data) or 'Working on your task')
            return
        if hasattr(self,'attention'):
            if kind in ('handoff','error'):self.attention.notify('input' if kind=='handoff' else 'error',(kind,conversation,str(data)))
            elif kind=='idle' and conversation and self.store.conversation(conversation)['status']=='Completed':self.attention.notify('info',('idle',conversation,len(self.store.messages(conversation))))
        if kind=='action':
            summaries={'desktop.inspect':'Inspecting application controls','desktop.observe':'Viewing the approved screen','desktop.action':'Working in the approved application','desktop.open_app':'Opening an approved program','desktop.list_windows':'Finding authorized windows','browser.inspect':'Inspecting the page','browser.action':'Working on the page','browser.navigate':'Opening an approved website','files.read':'Reading a file','files.write':'Updating a file','files.create':'Creating a file','files.delete':'Deleting an approved file','files.list':'Inspecting a folder','attachments.read':'Reading an attachment'}
            self.activity_summary.setText(summaries.get(str(data),'Working on your task'))
        super().on_event(kind,conversation,data)
        if kind in ('paused','idle'):self.refresh_requests()

    def show_request(self,request):
        args=request['args'];card=QGroupBox('Waiting for User — Complete this step' if args.get('manual_step') else 'Waiting for User — Your permission is needed');card.setProperty('conversation',request['conversation']);form=QVBoxLayout(card)
        title=QLabel(request['label']);title.setTextFormat(Qt.PlainText);title.setWordWrap(True);form.addWidget(title)
        if args.get('manual_step'):
            details=QLabel(args['reason']);details.setTextFormat(Qt.PlainText);details.setWordWrap(True);form.addWidget(details)
        elif args.get('website_access'):
            description=('Website: '+args['origin']+'\n'+('From: '+args['source_origin']+'\n' if args.get('source_origin') else '')+'\n'+args.get('reason','')+'\n\n'+args.get('approval_reason',args.get('note',''))+'\n\nPage content and authorized screenshots may be sent to your Codex account. Allow Once lasts for this visit. Session expires on Stop or app close.')
            details=QLabel(description);details.setTextFormat(Qt.PlainText);details.setWordWrap(True);form.addWidget(details)
        elif args.get('file_permission'):
            details=QLabel('File: '+args['path']+'\n\nReason: '+args['reason']+'\n\n'+('A private recovery copy will be kept.' if args['reversible'] else 'No existing content will be changed.')+'\nAllow Once expires with this exact operation. Session applies only to this action and target.')
            details.setTextFormat(Qt.PlainText);details.setWordWrap(True);details.setTextInteractionFlags(Qt.TextSelectableByMouse);form.addWidget(details)
            if args.get('preview'):
                diff=QPlainTextEdit(args['preview']);diff.setReadOnly(True);diff.setMaximumHeight(120);form.addWidget(diff)
        else:
            if args.get('approval_reason'):
                reason=QLabel('Why approval is needed: '+args['approval_reason']);reason.setTextFormat(Qt.PlainText);reason.setWordWrap(True);form.addWidget(reason)
                context=args.get('target_context',{})
                destination=context.get('form_action') or context.get('page_url') or context.get('application')
                if destination:
                    target=QLabel('Target: '+destination);target.setTextFormat(Qt.PlainText);target.setWordWrap(True);form.addWidget(target)
            if args.get('file'):
                transfer=args['file'];file_label=QLabel('File: '+transfer['name']+' · '+str(transfer['bytes'])+' bytes\nSHA-256: '+transfer['sha256']);file_label.setTextFormat(Qt.PlainText);file_label.setWordWrap(True);form.addWidget(file_label)
            group=QGroupBox('Action details');group.setCheckable(True);group.setChecked(False);group_layout=QVBoxLayout(group)
            details=QPlainTextEdit(json.dumps(args,ensure_ascii=False,indent=2));details.setReadOnly(True);details.setMaximumHeight(140);details.hide();group_layout.addWidget(details);group.toggled.connect(details.setVisible);form.addWidget(group)
        row=QHBoxLayout()
        def decide(allowed,session=False):
            if request['event'].is_set():return
            valid=not self.permissions.halted.is_set() and request['generation']==self.permissions.generation and time.monotonic()<=request['deadline'] and request['conversation']==self.permissions.owner
            if allowed and valid and args.get('operation')=='delete':
                if QMessageBox.warning(self,'Confirm recoverable deletion','Delete the exact target shown above? A private recovery copy will be kept; recovery cannot be guaranteed.',QMessageBox.Yes|QMessageBox.No,QMessageBox.No)!=QMessageBox.Yes:return
            if allowed and valid and args.get('website_access'):
                if not args.get('chrome_tab'):self.permissions.browser=True;self.permissions.observe=True
                if session and not args.get('chrome_tab'):
                    if args.get('permission_kind')=='data_connection':self.permissions.browser_data_pairs.add((args['source_origin'],args['origin']))
                    else:self.permissions.origins.add(args['origin'])
            elif session and allowed and valid:
                with self.permissions.lock:self.permissions.file_policy.session.append(FilePolicy.rule(args['path'],'file',{args['operation']:'allow'}))
            request['allowed']=allowed and valid;request['event'].set();card.hide();self.refresh_requests()
            self.notice.setText('Decision received. Codex will verify the current state and continue.' if request['allowed'] else 'Denied. Codex will receive your decision.')
            self.render()
        row.addWidget(button('Done — Continue' if args.get('manual_step') else 'Allow Once',lambda:decide(True)))
        if args.get('file_permission') or args.get('website_access'):row.addWidget(button('Allow for This Session',lambda:decide(True,True)))
        row.addWidget(button('Cannot complete' if args.get('manual_step') else 'Deny',lambda:decide(False)));form.addLayout(row)
        self.approvals_layout.addWidget(card);self.request_cards.append((request,card));self.refresh_requests()
        request['message_id']=self.store.add(request['conversation'],'system',request['label']+'\n'+str(args.get('path',''))+'\n'+str(args.get('reason',args.get('approval_reason',''))),'Waiting for local approval');self.render()

    def refresh_requests(self):
        visible=False
        for request,card in self.request_cards:
            if request['event'].is_set() and request.get('message_id') and not request.get('resolved_recorded'):
                state='Approved for this exact request' if request['allowed'] else 'Denied, expired or revoked'
                self.store.message(request['message_id'],state=state);request['resolved_recorded']=True
            show=not request['event'].is_set() and request['conversation']==self.selected
            card.setVisible(show);visible|=show
        self.approvals_widget.setVisible(visible)

    def select(self,item,previous):
        super().select(item,previous);self.refresh_requests()

    def refresh_status(self):
        super().refresh_status()
        task=self.store.conversation(self.selected) if self.selected else None
        if task:
            state=task['status'];legacy={'Thinking':'Working','Acting':'Working','Waiting for approval':'Waiting for User','Review after interruption':'Error'}
            self.status.setText(legacy.get(state,'Stopped' if state.startswith('Paused') else 'Error' if state.startswith('Review') else state))
        p=self.permissions
        for widget,value in ((self.public_browser,p.public_browsing),(self.manual_browser,p.browser_manual)):
            widget.blockSignals(True);widget.setChecked(bool(value));widget.blockSignals(False)
        self.grants.setText(('Access off' if not p.desktop and not p.browser else 'Stopped' if p.halted.is_set() else 'Access enabled')+'\n'+p.desktop_mode+'\n'+p.desktop_target_name+'\n'+('Program launches allowed' if p.allow_launches else 'Program launches off')+f'\nWebsites: {len(p.origins)}')

    def file_permissions(self):
        dialog=QDialog(self);dialog.setWindowTitle('File permissions');dialog.resize(1000,520);layout=QVBoxLayout(dialog)
        explanation=QLabel('Unlisted ordinary files: Ask. Protected system and credential files: Deny. Explicit Deny always wins. Preferred rules persist; session approvals expire on close or Stop.');explanation.setWordWrap(True);layout.addWidget(explanation)
        table=QTableWidget(0,6);table.setHorizontalHeaderLabels(['Location','Scope','Read','Write','Create','Delete']);table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch);layout.addWidget(table)
        rows=[]
        def add_rule(rule):
            index=table.rowCount();table.insertRow(index);path=QLineEdit(rule['path']);table.setCellWidget(index,0,path)
            scope=QComboBox();scope.addItems(['file','folder','recursive']);scope.setCurrentText(rule['scope']);table.setCellWidget(index,1,scope)
            choices=[]
            for i,action in enumerate(ACTIONS):
                choice=QComboBox();choice.addItems(DECISIONS);choice.setCurrentText(rule['decisions'].get(action,'ask'));table.setCellWidget(index,i+2,choice);choices.append(choice)
            rows.append((path,scope,choices))
        for rule in self.permissions.file_policy.rules:add_rule(rule)
        def pick(folder=False,recursive=False):
            path=QFileDialog.getExistingDirectory(self,'Choose permission folder') if folder else QFileDialog.getOpenFileName(self,'Choose permission file')[0]
            if path:add_rule(FilePolicy.rule(path,'recursive' if recursive else 'folder' if folder else 'file',{}))
        row=QHBoxLayout();row.addWidget(button('Add file',lambda:pick()));row.addWidget(button('Add folder',lambda:pick(True)));row.addWidget(button('Add project / subfolders',lambda:pick(True,True)))
        def remove():
            index=table.currentRow()
            if index>=0:table.removeRow(index);rows.pop(index)
        row.addWidget(button('Remove selected rule',remove))
        def clear_session():
            self.permissions.generation+=1;self.permissions.file_policy.session=[];self.notice.setText('Session file permissions revoked. Other authorized work can continue.')
        row.addWidget(button('Revoke session grants',clear_session));layout.addLayout(row)
        session=QPlainTextEdit(json.dumps(self.permissions.file_policy.session,indent=2));session.setReadOnly(True);session.setMaximumHeight(90);layout.addWidget(session)
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel);buttons.accepted.connect(dialog.accept);buttons.rejected.connect(dialog.reject);layout.addWidget(buttons)
        if dialog.exec()!=QDialog.Accepted:return
        try:
            rules=[]
            for path,scope,choices in rows:
                root=Path(path.text()).resolve()
                if scope.currentText()!='file' and (root==root.parent or root==Path.home() or len(root.parts)<=2):
                    if QMessageBox.warning(self,'Broad file permission','This rule covers a broad location. It may expose personal files. Protected locations remain denied. Authorize this scope?',QMessageBox.Yes|QMessageBox.No,QMessageBox.No)!=QMessageBox.Yes:return
                rules.append(FilePolicy.rule(root,scope.currentText(),dict(zip(ACTIONS,[c.currentText() for c in choices]))))
            self.permissions.generation+=1
            with self.permissions.lock:self.permissions.file_policy.rules=rules;self.permissions.file_policy.session.clear()
            self.store.setting('file_rules',rules);self.notice.setText('File rules saved. The task can continue within the current policy.')
        except Exception as error:self.notice.setText(str(error))

    def settings(self):
        dialog=QDialog(self);dialog.setWindowTitle('Preferences');dialog.resize(620,570);form=QFormLayout(dialog);saved=self.store.settings()
        theme=QComboBox();theme.addItems(['Dark','Light']);theme.setCurrentText(saved.get('theme','Dark'));form.addRow('Appearance',theme)
        font=QSpinBox();font.setRange(10,24);font.setValue(saved.get('font_size',11));form.addRow('Text size',font)
        origins=QPlainTextEdit('\n'.join(sorted(self.permissions.origins)));origins.setMaximumHeight(90);form.addRow('Browser website origins',origins)
        exclusions=QLineEdit(', '.join(self.desktop.exclusions));form.addRow('Excluded window title words',exclusions)
        routine_note=QLabel('Routine controls are allowed within your current desktop/browser scopes. Only consequential or unverified activations need review.');routine_note.setWordWrap(True);form.addRow(routine_note)
        notifications={}
        for key,label in [('input','Requests needing you'),('error','Errors'),('info','Task completed')]:
            check=QCheckBox();check.setChecked(saved.get('notify_'+key,key!='info'));form.addRow('Notify: '+label,check);notifications[key]=check
        retention=QComboBox()
        for label,days in [('Until deleted',0),('7 days',7),('30 days',30),('90 days',90),('365 days',365)]:retention.addItem(label,days)
        retention.setCurrentIndex(max(0,retention.findData(saved.get('history_days',0))));form.addRow('Local history retention',retention)
        privacy=QLabel('Screenshots are sent only as needed within authorized scopes. Ordinary captures stay in memory. Provider and Codex runtime retention are separate. Desktop authority expires when the app closes.');privacy.setWordWrap(True);form.addRow(privacy)
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel);buttons.accepted.connect(dialog.accept);buttons.rejected.connect(dialog.reject);form.addRow(buttons)
        if dialog.exec()!=QDialog.Accepted:return
        try:
            approved={origin(x.strip()) for x in origins.toPlainText().splitlines() if x.strip()}
            excluded=[x.strip() for x in exclusions.text().split(',') if x.strip()]
            if approved!=self.permissions.origins or excluded!=self.desktop.exclusions:
                self.permissions.generation+=1
                with self.permissions.lock:
                    self.permissions.origins=approved;self.desktop.exclusions=excluded
            for key,value in [('theme',theme.currentText()),('font_size',font.value()),('exclusions',self.desktop.exclusions),('history_days',retention.currentData())]+[('notify_'+key,c.isChecked()) for key,c in notifications.items()]:self.store.setting(key,value)
            self.apply_settings();self.notice.setText('Preferences saved. Your current task continues.')
        except Exception as error:self.notice.setText(str(error))

    def apply_settings(self):
        super().apply_settings();settings=self.store.settings();dark=settings.get('theme','Dark')=='Dark'
        bg='#191b1f' if dark else '#f7f7f8';surface='#23262b' if dark else '#ffffff';text='#e8e9eb' if dark else '#23262b';border='#34373d' if dark else '#dfe1e5'
        self.setStyleSheet(f'''QWidget{{background:{bg};color:{text};font-family:Segoe UI;font-size:{settings.get('font_size',11)}pt;}}
            QTextBrowser,QPlainTextEdit,QListWidget,QLineEdit,QComboBox{{background:{surface};border:1px solid {border};border-radius:9px;padding:8px;selection-background-color:#4a5362;}}
            QTextBrowser{{border:0;padding:16px;}} QPushButton{{background:{surface};border:1px solid {border};border-radius:7px;padding:7px 10px;}}
            QPushButton:hover{{background:{border};}} QPushButton#send{{background:#dde5ee;color:#18212b;font-weight:600;}}
            QListWidget::item{{padding:8px;}} QListWidget::item:selected{{background:#414954;color:white;border-radius:6px;}}
            QLabel#conversationTitle{{font-size:18pt;font-weight:600;padding:8px;}} QGroupBox{{border:1px solid {border};border-radius:9px;margin-top:14px;padding:10px;}}
            QSplitter::handle{{background:{border};width:1px;}}''')
        self.chat.document().setDefaultStyleSheet('pre {background:#30343b;color:#eef0f4;padding:14px;} code {font-family:Consolas;} h3 {font-size:13pt;} table {border-collapse:collapse;} td,th {padding:6px;border:1px solid #777;}')

    def render(self):
        if self.closing or not self.selected:return
        import re
        parts=[];dark=self.store.settings().get('theme','Dark')=='Dark'
        class SafeDocument(QTextDocument):
            def loadResource(self,kind,url):return None
        for message in self.store.messages(self.selected):
            role=message['role'];name={'user':'You','assistant':'Codex','system':'Status'}.get(role,role)
            document=SafeDocument();document.setMarkdown(message['text'])
            body=re.search(r'<body[^>]*>(.*)</body>',document.toHtml(),re.S).group(1)
            attachments=[]
            for record in json.loads(message['attachments']):
                attachments.append('<p><a href="attachment:'+html.escape(record['id'],quote=True)+'">'+html.escape(record['name'])+'</a></p>')
                path=self.attachments.path(record)
                if path.suffix.lower() in ('.png','.jpg','.jpeg','.webp','.bmp','.gif') and path.exists():
                    url='attachment-image:'+record['id']
                    if url not in self.chat.images:self.chat.images[url]=QPixmap(str(path)).scaled(620,360,Qt.KeepAspectRatio,Qt.SmoothTransformation)
                    attachments.append('<p><img src="'+url+'"></p>')
            color=('#30363e' if dark else '#e9eef4') if role=='user' else ('#23262b' if dark else '#ffffff')
            state='' if message['state'] in ('saved','sent') else '<p><small>'+html.escape(message['state'])+'</small></p>'
            parts.append(f'<table width="100%" cellspacing="0" cellpadding="12" bgcolor="{color}" style="border:0;"><tr><td style="border:0;background-color:{color};"><b>{name}</b><br>{body}{"".join(attachments)}{state}</td></tr></table><br>')
        bar=self.chat.verticalScrollBar();bottom=bar.value()>=bar.maximum()-40;position=bar.value()
        self.chat.setHtml(''.join(parts))
        bar.setValue(bar.maximum() if bottom else position)
        self.attachment_list.setVisible(bool(self.pending))

    def closeEvent(self,event):
        self.permissions.halt()
        if hasattr(self,'input_guard'):self.input_guard.close()
        if hasattr(self,'attention'):self.attention.tray.hide()
        super().closeEvent(event)
