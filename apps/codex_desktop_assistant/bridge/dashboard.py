"""Status, human requests and owner controls. No chat or inference engine."""
import json
import time
from PySide6.QtCore import QObject,Signal,QTimer,Qt
from PySide6.QtGui import QAction,QIcon
from PySide6.QtWidgets import (QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QDialog,QPlainTextEdit,QMenu,QSystemTrayIcon,QStyle,QComboBox,QCheckBox,QDialogButtonBox,QMessageBox,QScrollArea,QFileDialog,QTabWidget)
from .runtime import Runtime


class Events(QObject):event=Signal(str,object,object)


def button(text,slot):
    widget=QPushButton(text);widget.clicked.connect(slot);return widget


class Dashboard(QMainWindow):
    def __init__(self,directory,manager=None,*,restore_saved=True):
        super().__init__();self.setWindowTitle('Codex Computer Bridge');self.resize(860,650);self.explicit_quit=False;self.cards={}
        self.manager=manager;self.manager_panel=None;self.saved_workers_checked=False
        self.workspace_windows={}
        self.events=Events();self.events.event.connect(self.on_event);self.browser_message='';self.browser_showing=False
        self.runtime=Runtime(directory,self.events.event.emit,manager);self.store=self.runtime.store;self.permissions=self.runtime.permissions;self.desktop=self.runtime.desktop;self.broker=self.runtime.broker;self.attachments=self.runtime.attachments
        root=QWidget();self.setCentralWidget(root);layout=QVBoxLayout(root);layout.setContentsMargins(28,24,28,24);layout.setSpacing(16)
        title=QLabel('Codex Computer Bridge');title.setStyleSheet('font-size:25px;font-weight:600');layout.addWidget(title)
        caption=QLabel('Give instructions in official Codex. This window shows execution and requests.');caption.setWordWrap(True);layout.addWidget(caption)
        self.connection=QLabel();self.work=QLabel();self.work.setWordWrap(True);self.notice=QLabel('Ready');self.notice.setWordWrap(True)
        for widget in (self.connection,self.work,self.notice):layout.addWidget(widget)
        row=QHBoxLayout()
        for text,slot in (('View Projects',self.show_projects),('Show Browser',self.show_browser),('Stop',lambda:self.runtime.stop()),('Settings',self.settings)):row.addWidget(button(text,slot))
        layout.addLayout(row)
        scroll=QScrollArea();scroll.setWidgetResizable(True);requests=QWidget();self.request_layout=QVBoxLayout(requests);self.request_layout.addStretch();scroll.setWidget(requests);layout.addWidget(scroll,1)
        footer=QHBoxLayout();footer.addWidget(button('Emergency Stop',lambda:self.runtime.stop()));footer.addStretch();footer.addWidget(button('Quit Portfolio Manager' if manager else 'Quit Bridge',self.quit_bridge));layout.addLayout(footer)
        if manager:
            from portfolio_manager.ui import ManagerPanel
            self.setWindowTitle('Portfolio Manager');self.resize(1120,760)
            self.tabs=QTabWidget();bridge_view=self.takeCentralWidget()
            self.manager_panel=ManagerPanel(manager.coordinator,manager.supervisor,self.runtime.stop,
                                            parent=self.tabs,on_stop_all=self.cancel_bridge_work,candidate_host=manager)
            self.tabs.addTab(self.manager_panel,'Portfolio')
            self.tabs.addTab(bridge_view,'Computer Access')
            self.setCentralWidget(self.tabs)
        self.setStyleSheet('QWidget{background:#f7f8fa;color:#15202b;font-family:"Segoe UI";font-size:14px} QPushButton{background:white;border:1px solid #cbd2da;border-radius:7px;padding:10px 16px} QPushButton:hover{background:#e7eef4} QPlainTextEdit{background:white;border:1px solid #cbd2da} QScrollArea{border:0}')
        self.tray=QSystemTrayIcon(self.style().standardIcon(QStyle.SP_ComputerIcon),self);self.tray.setToolTip('Codex Computer Bridge')
        menu=QMenu();menu.addAction('Open dashboard',self.show_dashboard);menu.addAction('Emergency Stop',self.runtime.stop);menu.addAction('Quit Portfolio Manager' if manager else 'Quit Bridge',self.quit_bridge);self.tray.setContextMenu(menu);self.tray.activated.connect(lambda reason:self.show_dashboard() if reason==QSystemTrayIcon.Trigger else None);self.tray.messageClicked.connect(self.show_dashboard);self.tray.show()
        self.timer=QTimer(self);self.timer.timeout.connect(self.refresh);self.timer.start(1000);self.runtime.start_pipe();self.refresh()
        if manager and restore_saved:
            QTimer.singleShot(0,self.restore_workers)

    def restore_workers(self):
        if self.saved_workers_checked:return
        try:
            self.manager.restore()
            self.saved_workers_checked=True
        except (OSError,ValueError,RuntimeError) as error:
            from portfolio_autopilot.codex_relay.diagnostics import sanitize
            self.manager_panel.notice.setText('Could not restore workers. '+sanitize(error)[:400])

    def show_dashboard(self):
        if not self.isVisible():self.show()
        self.raise_();self.activateWindow()

    def cancel_bridge_work(self):
        for event in list(self.runtime.inflight.values()):event.set()
        for request in self.runtime.requests:request['event'].set()
        self.broker.projects.stop()
        self.refresh()

    def show_computer_access(self):
        self.tabs.setCurrentIndex(1)
        self.show_dashboard()

    def show_workspace(self, workspace):
        from portfolio_manager.workspace_window import WorkspaceWindow

        window = self.workspace_windows.get(workspace['id'])
        if window is None:
            window = WorkspaceWindow(self.manager, workspace, on_emergency=self.runtime.stop,
                                     on_stop_all=self.cancel_bridge_work,
                                     on_access=self.show_computer_access,
                                     on_close=self.workspace_windows.pop)
            window.setStyleSheet(self.styleSheet())
            self.workspace_windows[workspace['id']] = window
        else:
            window.apply_workspace(workspace)
        if window.isMinimized():
            window.showNormal()
        else:
            window.show()
        window.raise_()
        window.activateWindow()

    def on_event(self,kind,conversation,data):
        if kind=='show_dashboard':self.show_dashboard()
        if kind=='show_portfolio' and self.manager:
            self.restore_workers()
            if isinstance(data, dict) and 'id' in data:
                self.show_workspace(data)
            else:
                self.tabs.setCurrentWidget(self.manager_panel);self.show_dashboard()
        if kind=='browser_show_result':
            self.browser_showing=False;self.browser_message=str(data)
        if kind=='request':
            if not self.manager or self.manager.control()['mode']=='human':
                self.tray.showMessage('Codex needs your input','Open Computer Access to review the required action.',QSystemTrayIcon.Warning,10000)
        self.refresh()

    def refresh(self):
        state=self.runtime.status()
        self.connection.setText('Codex: '+('Connected' if state['mcp_clients_connected'] else 'Disconnected')+'    ·    Chrome: '+('Connected' if state['chrome_connected'] else 'Disconnected')+'    ·    Browser access: '+('Full' if state['full_browser_access'] else 'Restricted')+'    ·    Desktop: '+('Authorized' if state['desktop_authorized'] else 'Off'))
        lines=[]
        project=next(iter(state.get('projects',[])),None)
        if project:lines.extend(['Project: '+project['objective'],str(project.get('completed_tasks',0))+'/'+str(project.get('total_tasks',0))+' tasks complete'])
        lines.extend(['Stopped — resume in Settings.' if state['stopped'] else 'Current activity: '+(state['active_tool'] or state['latest_action']),state['reasoning_state']])
        if state.get('current_website'):lines.append('Website: '+state['current_website'])
        self.work.setTextFormat(Qt.PlainText);self.work.setText('\n'.join(lines))
        self.notice.setTextFormat(Qt.PlainText)
        parked=self.store.settings().get('portfolio_parked_bridge_requests',[]) if self.manager else []
        parked_note=('\nRecent actions held for human review: '+', '.join(row['action'] for row in parked[-3:])) if parked else ''
        self.notice.setText('Pending human requests: '+str(state['pending_requests'])+parked_note+ ('\n'+self.browser_message if self.browser_message else ''));self.tray.setToolTip(('Portfolio Manager' if self.manager else 'Codex Computer Bridge')+' — '+('Stopped' if state['stopped'] else state['active_tool'] or 'Ready'))
        control=self.manager.control() if self.manager else None
        show_requests=not control or (control['mode']=='human' and not control['stopped'] and not control['emergency'])
        pending={r['id']:r for r in self.runtime.requests if show_requests and not r['event'].is_set() and r['deadline']>time.monotonic() and r['generation']==self.permissions.generation}
        for key in set(self.cards)-set(pending):self.cards.pop(key).deleteLater()
        for key,request in pending.items():
            if key in self.cards:continue
            card=QWidget();box=QVBoxLayout(card);label=QLabel(request['label']);label.setTextFormat(Qt.PlainText);label.setWordWrap(True);box.addWidget(label)
            reason=request['args'].get('approval_reason') or request['args'].get('reason') or request['args'].get('question','Review the specific action before allowing it.');label=QLabel(reason);label.setTextFormat(Qt.PlainText);label.setWordWrap(True);box.addWidget(label)
            details=button('View exact scope',lambda checked=False,r=request:self.request_details(r));box.addWidget(details)
            row=QHBoxLayout()
            def decide(allowed,r=request):r['allowed']=allowed;r['event'].set();self.refresh()
            row.addWidget(button('Done — Continue' if request['args'].get('manual_step') else 'Allow Once',lambda checked=False,f=decide:f(True)));row.addWidget(button('Deny',lambda checked=False,f=decide:f(False)));box.addLayout(row)
            self.request_layout.insertWidget(self.request_layout.count()-1,card);self.cards[key]=card

    def request_details(self,request):
        dialog=QDialog(self);dialog.setWindowTitle('Exact requested authorization');dialog.resize(760,520);layout=QVBoxLayout(dialog);text=QPlainTextEdit(json.dumps(request['args'],indent=2,ensure_ascii=False));text.setReadOnly(True);layout.addWidget(text);layout.addWidget(button('Close',dialog.accept));dialog.exec()

    def show_projects(self):
        dialog=QDialog(self);dialog.setWindowTitle('Projects and deliverables');dialog.resize(880,650);layout=QVBoxLayout(dialog);text=QPlainTextEdit();text.setReadOnly(True);layout.addWidget(text)
        def refresh():
            queue=self.broker.projects.queue;lines=[]
            for project in queue.rows('SELECT * FROM projects ORDER BY updated DESC LIMIT 100'):
                summary=queue.summary(project['id'],project['conversation']);lines.extend([project['objective'],summary['state']+' — '+str(summary['counts'].get('completed',0))+'/'+str(summary['total'])+' tasks complete'])
                for job in summary['jobs']:
                    if job['state'] in ('blocked','failed','review'):lines.append('Needs attention: '+job['key']+' — '+job['error'])
                lines.append('')
            text.setPlainText('\n'.join(lines) or 'No projects yet. Ask official Codex to create one.')
        refresh();timer=QTimer(dialog);timer.timeout.connect(refresh);timer.start(2000)
        layout.addWidget(button('Open deliverables folder',lambda:self.open_folder(self.store.directory/'projects')));layout.addWidget(button('Close',dialog.accept));dialog.exec();timer.stop()

    def open_folder(self,path):
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def show_browser(self):
        if self.browser_showing:return
        selected=self.broker.chrome.selected
        if selected is None:
            self.browser_message='No task browser tab selected. Ask Codex to open or reuse the page you need.';self.refresh();return
        self.browser_showing=True;self.browser_message='Bringing the selected task tab forward…';self.refresh()
        def show():
            try:
                tabs=self.broker.chrome.call(self.runtime.owner,'list_tabs',{})['tabs']
                target=selected
                if not any(tab['tab']==target for tab in tabs):
                    url=self.broker.chrome.opened_urls.get(target)
                    if not url:raise RuntimeError('The selected task tab was closed. Ask Codex to restore that page; existing matching tabs will be reused.')
                    restored=self.broker.chrome.call(self.runtime.owner,'open_tab',{'url':url})
                    if not restored.get('authorized'):raise RuntimeError('The restored page needs authorization in the Chrome extension.')
                    target=restored['tab']
                from .windows import allow_chrome_foreground
                allow_chrome_foreground()  # explicit local owner action, limited to installed Chrome
                self.broker.chrome.call(self.runtime.owner,'show',{'tab':target})
                message='Chrome was asked to show the selected task tab. If it stays behind another window, select Chrome on the Windows taskbar.'
            except Exception as error:message='Could not show browser: '+str(error)
            self.events.event.emit('browser_show_result',None,message)
        import threading
        threading.Thread(target=show,daemon=True).start()

    def settings(self):
        dialog=QDialog(self);dialog.setWindowTitle('Computer Bridge Settings');layout=QVBoxLayout(dialog)
        layout.addWidget(QLabel('Desktop control stays off until enabled here. Chrome uses its existing permissions.'))
        routine=QCheckBox('Automatically allow routine work');routine.setObjectName('routine_approvals')
        routine.setChecked(self.store.settings().get('routine_approvals') is True)
        routine.toggled.connect(lambda enabled:self.store.setting('routine_approvals',bool(enabled)))
        layout.addWidget(routine)
        from .routine_policy import PROJECT_ROOT
        note=QLabel('Allows default Read requests inside '+str(PROJECT_ROOT)+', reuse/screenshots of already authorized Chrome sites, and saves to existing Invisible Payhip products. Explicit file Ask/Deny rules, Stop and access scopes stay in force. Uploads, publication, purchases, credentials, destructive actions and unknown requests still require review.');note.setWordWrap(True);layout.addWidget(note)
        layout.addWidget(button('Desktop access…',self.desktop_settings))
        def files():
            from assistant.ui import MainWindow
            MainWindow.file_permissions(self)  # shared local policy editor; no AI instance
        layout.addWidget(button('File Read / Write / Create / Delete…',files))
        def browser():
            import subprocess
            info=json.loads((self.store.directory/'chrome-host/settings.json').read_text());chrome='C:/Program Files/Google/Chrome/Application/chrome.exe'
            subprocess.Popen([chrome,'chrome-extension://'+info['extension_id']+'/popup.html'])
        layout.addWidget(button('Chrome authorization…',browser))
        def resume():self.store.setting('bridge_stopped',False);self.permissions.resume(self.runtime.owner);self.runtime.latest='Ready';self.refresh()
        layout.addWidget(button('Resume after Stop',resume));layout.addWidget(button('Preserved history and backups',lambda:self.open_folder(self.store.directory)))
        layout.addWidget(button('Read archived conversations',self.history))
        layout.addWidget(button('Close',dialog.accept));dialog.exec()

    def history(self):
        dialog=QDialog(self);dialog.setWindowTitle('Preserved conversation archive');dialog.resize(880,650);layout=QVBoxLayout(dialog);choices=QComboBox();text=QPlainTextEdit();text.setReadOnly(True)
        for record in self.store.execute('SELECT id,title FROM conversations ORDER BY updated DESC LIMIT 500'):choices.addItem(record['title'],record['id'])
        def read():text.setPlainText('\n\n'.join(message['role'].upper()+': '+message['text'] for message in self.store.messages(choices.currentData()))[:200000])
        choices.currentIndexChanged.connect(read);layout.addWidget(choices);layout.addWidget(text);read();layout.addWidget(button('Close',dialog.accept));dialog.exec()

    def desktop_settings(self):
        dialog=QDialog(self);dialog.setWindowTitle('Authorize desktop scope');layout=QVBoxLayout(dialog);mode=QComboBox();mode.addItems(['Selected Window','Entire Monitor']);target=QComboBox();launch=QCheckBox('Allow launching ordinary installed applications')
        def populate():
            target.clear()
            if mode.currentText()=='Selected Window':
                for window in self.desktop.windows():target.addItem(window['title'],window)
            else:
                for i,bounds in enumerate(self.desktop.monitors()[:-1]):target.addItem('Monitor '+str(i+1),bounds)
        mode.currentTextChanged.connect(populate);populate();layout.addWidget(mode);layout.addWidget(target);layout.addWidget(launch)
        text=QLabel('Authorized screen observations can be sent to official Codex. Passwords, MFA and CAPTCHA remain manual. Ctrl+Alt+F12 stops input.');text.setWordWrap(True);layout.addWidget(text)
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel);buttons.accepted.connect(dialog.accept);buttons.rejected.connect(dialog.reject);layout.addWidget(buttons)
        if dialog.exec()!=QDialog.Accepted:return
        if not self.runtime.hotkey.registered:QMessageBox.warning(self,'Emergency shortcut unavailable','Resolve the Ctrl+Alt+F12 conflict before enabling desktop input.');return
        choice=target.currentData()
        if choice is None:return
        self.permissions.halt();self.permissions.windows={};self.permissions.capture_bounds=None;self.permissions.desktop_mode=mode.currentText()
        if mode.currentText()=='Selected Window':self.permissions.windows[choice['hwnd']]=self.desktop.identity(choice['hwnd'])
        else:self.permissions.capture_bounds=tuple(choice);self.permissions.monitor_layout=tuple(self.desktop.monitors())
        self.permissions.desktop=self.permissions.observe=True;self.permissions.allow_launches=launch.isChecked();self.permissions.resume(self.runtime.owner);self.refresh()

    def quit_bridge(self):self.explicit_quit=True;self.close()

    def closeEvent(self,event):
        if not self.explicit_quit and QSystemTrayIcon.isSystemTrayAvailable():self.hide();event.ignore();return
        for window in list(self.workspace_windows.values()):
            window.close()
        self.timer.stop();self.runtime.close()
        if self.manager_panel:self.manager_panel.shutdown()
        if self.manager:self.manager.close()
        self.tray.hide();event.accept()
        from PySide6.QtWidgets import QApplication
        QApplication.instance().quit()
