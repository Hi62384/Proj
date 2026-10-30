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
        from .ui_layout import build
        build(self)

    def show_control_center(self):
        self.control_center.show();self.control_center.raise_()

    def add_files(self,files):
        super().add_files(files);self.attachment_list.setVisible(bool(self.pending));self.remove_attachment_button.setVisible(bool(self.pending))

    def remove_attachment(self):
        super().remove_attachment();self.attachment_list.setVisible(bool(self.pending));self.remove_attachment_button.setVisible(bool(self.pending))

    def open_browser_access(self):
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices
        settings=self.store.directory/'chrome-host/settings.json'
        if not settings.is_file():self.connect_chrome();return
        extension=json.loads(settings.read_text())['extension_id']
        QDesktopServices.openUrl(QUrl('chrome-extension://'+extension+'/popup.html'))

    def show_requests(self):
        from .requests_ui import RequestsPanel
        self.refresh_requests()
        if getattr(self,'requests_panel',None):self.requests_panel.close()
        self.requests_panel=RequestsPanel(self);self.requests_panel.show()

    def show_projects(self):
        from .project_ui import ProjectDashboard
        if getattr(self,'project_dashboard',None):self.project_dashboard.close()
        self.project_dashboard=ProjectDashboard(self);self.project_dashboard.show()

    def synthetic_workflow(self):
        if self.engine.active:self.notice.setText('Finish or Stop the active chat turn before starting the local test.');return
        self.new_chat();scope=self.broker.projects.prepare_synthetic(self.selected)
        prompt='''Create five distinct spreadsheet products for small businesses, generate all required files and preview images, build a test store, create the listings, and publish them to the explicitly authorized local test storefront. This is the owner-invoked synthetic acceptance workflow, not real business publication. Use projects.* to plan and run the complete durable workflow. The host has created a real disposable authenticated local adapter with store ID '''+scope['store']+''' and preauthorized ONLY these five generated products at the following exact synthetic prices (zero spending). Product specifications: '''+json.dumps(scope['products'])+'''. Create the project and full product pipeline using projects.products with store set to the configured synthetic store ID, so publication and verification tasks are included from the start. Start local generation/QA/packaging first, and use projects.wait {project,seconds:20} between status checks while independent work runs. Inspect rendered previews. After all five packages pass QA, call projects.authorize_launch once for these exact products/store; the local host recognizes the explicit synthetic workflow authorization without interrupting the owner. Then add publish and verify tasks with dependencies on the existing package tasks, and continue until every listing and delivered file is verified. Do not repeat completed work. Retrieve final results and deliver each generated package into this chat using projects.deliver. Do not access any real account, payment, other browser tab, desktop, shell or unrelated files. If a built-in tool enum lacks projects.*, use its files.read_approved projects.* compatibility alias. A plan is not completion; report actual milestones and blockers.'''
        self.engine.submit(self.selected,prompt);self.notice.setText('Authorized local test started. Five synthetic products only; no real store or spending.');self.render()

    def synthetic_builder_workflow(self):
        if self.engine.active:self.notice.setText('Finish or Stop the active turn before the local builder test.');return
        if not self.broker.chrome.bridge.status().get('full_browser'):self.notice.setText('Enable Full Browser Access in the extension for the cross-site synthetic browser test.');self.open_browser_access();return
        from .builder_fixture import BuilderFixture
        self.new_chat();fixture=BuilderFixture()
        if not hasattr(self,'builder_fixtures'):self.builder_fixtures=[]
        self.builder_fixtures.append(fixture);self.broker.chrome.register_draft_fixture(self.selected,fixture.url)
        from .chrome_bridge import private_json
        path=self.store.directory/'verification/current-builder-fixture.json';path.parent.mkdir(parents=True,exist_ok=True);private_json(path,{'conversation':self.selected,'url':fixture.url})
        self.engine.submit(self.selected,'Run the fully authorized disposable browser-design test at '+fixture.url+'. Use only chrome.* and no desktop, shell, files, screenshots or other accounts. Start with no attached tab: create your own background tab, inspect it, open About Me, fill About text with exactly Practical business tools\nCreated for small teams (a real newline), open Colors, click Violet swatch, then fill Brand color with #125e77. Open Layout controls, Choose layout, select Editorial layout. Hover Show spacing menu and click Comfortable spacing. Inspect after each action and verify the result. Save draft once; the host already authorized this exact local unpublished-draft endpoint. Verify Unpublished draft saved in the page, and final color/layout/about values. Do not click Publish or Pay now. No manual clicks or approvals should be requested for these already authorized routine controls. Do not Show Tab or change the physical active tab. Keep the new tab for independent verification and report its ID only in technical details.')
        self.notice.setText('Local browser-design test started. No real account or public publication.')

    def quit_application(self):
        self.explicit_quit=True;self.broker.projects.stop();self.close()

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
        self.store.setting('browser_mode',self.browser_mode.currentText());existing=self.browser_mode.currentText()=='Existing Chrome';self.broker.chrome.mode=existing;self.permissions.chrome_mode=existing;self.chrome_panel.setVisible(existing)
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
        self.broker.projects.stop()
        self.permissions.halt()
        self.broker.chrome.stop()
        super().stop();self.pause_reason='';self.engine.state(self.selected,'Stopped');self.status.setText('Stopped')

    def emergency(self,reason='Emergency stop. New input is disabled; review before continuing.'):
        self.broker.projects.stop()
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
        self.requests.append(request);self.engine.waiting(conversation,1,'manual' if args.get('manual_step') else 'approval');self.emit('request_approval',conversation,request)
        try:
            while not request['event'].wait(.1):
                self.engine.pump_steering(conversation)
                if request['generation']!=self.permissions.generation or self.permissions.halted.is_set() or self.permissions.cancelled() or self.engine.stop_event.is_set() or time.monotonic()>request['deadline']:
                    request['event'].set();self.emit('request_expired',conversation,None);return False
            return request['allowed'] and not self.permissions.cancelled() and request['generation']==self.permissions.generation and time.monotonic()<=request['deadline']
        finally:self.engine.waiting(conversation,-1,'manual' if args.get('manual_step') else 'approval')

    def on_event(self,kind,conversation,data):
        if kind=='project_completed' and hasattr(self,'attention'):self.attention.notify('info','project-'+data['project'])
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
        if kind=='task_state':self.refresh_status();return
        if kind=='input_access':
            if conversation==self.selected:self.activity_summary.setText(str(data) or 'Working on your task')
            return
        if hasattr(self,'attention'):
            if kind in ('handoff','error'):self.attention.notify('input' if kind=='handoff' else 'error',(kind,conversation,str(data)))
            elif kind=='idle' and conversation and self.effective_status(conversation)=='Completed':self.attention.notify('info',('idle',conversation,len(self.store.messages(conversation))))
        if kind=='action':
            summaries={'desktop.inspect':'Inspecting application controls','desktop.observe':'Viewing the approved screen','desktop.action':'Working in the approved application','desktop.open_app':'Opening an approved program','desktop.list_windows':'Finding authorized windows','browser.inspect':'Inspecting the page','browser.action':'Working on the page','browser.navigate':'Opening an approved website','files.read':'Reading a file','files.write':'Updating a file','files.create':'Creating a file','files.delete':'Deleting an approved file','files.list':'Inspecting a folder','attachments.read':'Reading an attachment'}
            self.activity_summary.setText(summaries.get(str(data),'Working on your task'))
        if kind=='action':
            self.activity_text.appendPlainText(str(data));self.refresh_status();return
        super().on_event(kind,conversation,data)
        if kind in ('paused','idle'):self.refresh_requests()

    def show_request(self,request):
        args=request['args'];card=QGroupBox('Waiting for User — Complete this step' if args.get('manual_step') else 'Waiting for Approval — Your permission is needed');card.setProperty('conversation',request['conversation']);form=QVBoxLayout(card)
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
        from .status import pending
        live=pending(self.requests,self.permissions)
        for request in self.requests:
            if request not in live and not request['event'].is_set():request['allowed']=False;request['event'].set()
        count=len(live);self.attention_button.setText('Requests'+(' · '+str(count) if count else ''))
        if hasattr(self,'attention'):self.attention.unread=count
        visible=False
        for request,card in self.request_cards:
            if request['event'].is_set() and request.get('message_id') and not request.get('resolved_recorded'):
                state='Approved for this exact request' if request['allowed'] else 'Denied, expired or revoked'
                self.store.message(request['message_id'],state=state);request['resolved_recorded']=True
            show=request in live and request['conversation']==self.selected
            card.setVisible(show);visible|=show
        self.approvals_widget.setVisible(visible)

    def select(self,item,previous):
        super().select(item,previous);self.refresh_requests()

    def effective_status(self,conversation):
        from .status import resolve,pending
        projects=self.broker.projects.queue.rows('SELECT id FROM projects WHERE conversation=? ORDER BY updated DESC LIMIT 1',(conversation,))
        project=self.broker.projects.queue.summary(projects[0]['id'],conversation,limit=1) if projects else None
        requests=[r for r in pending(self.requests,self.permissions) if r['conversation']==conversation]
        return resolve(self.store.conversation(conversation),project,requests,self.engine.active==conversation)

    def refresh_status(self):
        if self.closing:return
        BaseWindow.refresh_status(self)
        self.refresh_requests()
        conversation=self.selected
        if conversation:self.status.setText(self.effective_status(conversation))
        projects=self.broker.projects.queue.rows('SELECT id FROM projects WHERE conversation=? ORDER BY updated DESC LIMIT 1',(conversation,))
        if projects:
            progress=self.broker.projects.queue.summary(projects[0]['id'],conversation,limit=1);counts=progress['counts']
            self.activity_summary.setText(f"{counts.get('completed',0)} of {progress['total']} tasks complete · {counts.get('blocked',0)+counts.get('review',0)} blocked")
            self.project_progress.setValue(round(100*counts.get('completed',0)/max(1,progress['total'])))
        p=self.permissions
        for widget,value in ((self.public_browser,p.public_browsing),(self.manual_browser,p.browser_manual)):
            widget.blockSignals(True);widget.setChecked(bool(value));widget.blockSignals(False)
        self.grants.setText(('Stopped' if p.halted.is_set() else 'Session enabled')+'\n'+p.desktop_mode+'\n'+p.desktop_target_name)
        chrome=self.broker.chrome.status()
        self.browser_activity.setText(('Chrome · '+str(len(chrome.get('tabs',[])))+' authorized pages · '+('Full access' if chrome.get('full_browser') else 'Restricted')) if chrome.get('connected') else 'Browser not connected')

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
        self.activity.setVisible(settings.get('show_activity',False));bg='#191b1f' if dark else '#f7f7f8';surface='#23262b' if dark else '#ffffff';text='#e8e9eb' if dark else '#23262b';border='#34373d' if dark else '#dfe1e5'
        self.setStyleSheet(f'''QWidget{{background:{bg};color:{text};font-family:Segoe UI;font-size:{settings.get('font_size',11)}pt;}}
            QTextBrowser,QPlainTextEdit,QListWidget,QLineEdit,QComboBox{{background:{surface};border:1px solid {border};border-radius:9px;padding:8px;selection-background-color:#4a5362;}}
            QTextBrowser{{border:0;padding:16px;}} QPushButton{{background:{surface};border:1px solid {border};border-radius:7px;padding:7px 10px;}}
            QPushButton:hover{{background:{border};}} QPushButton#send{{background:#dde5ee;color:#18212b;font-weight:600;}}
            QTreeWidget,QTableWidget{{background:{bg};border:1px solid {border};border-radius:8px;}} QHeaderView::section{{background:{surface};color:{text};border:0;border-bottom:1px solid {border};padding:8px;text-align:left;}} QListWidget::item{{padding:8px;}} QListWidget::item:selected{{background:#414954;color:white;border-radius:6px;}}
            QLabel#conversationTitle{{font-size:18pt;font-weight:600;padding:8px;}} QGroupBox{{border:1px solid {border};border-radius:9px;margin-top:14px;padding:10px;}}
            QSplitter::handle{{background:{border};width:1px;}}''')
        self.setStyleSheet(self.styleSheet()+f'''
            QWidget#sidebar{{background:{'#121820' if dark else '#eef1f5'};border-right:1px solid {border};}}
            QWidget#toolbar{{background:{bg};border-bottom:1px solid {border};}}
            QWidget#chatCenter,QTextBrowser{{background:{bg};}}
            QFrame#composerFrame{{background:{surface};border:1px solid {border};border-radius:16px;}}
            QPlainTextEdit#Composer{{background:transparent;border:0;padding:4px;}}
            QListWidget#conversationList{{background:transparent;border:0;padding:0;}}
            QLabel#sectionLabel,QLabel#muted,QLabel#notice{{color:{'#99a5b5' if dark else '#596678'};font-size:10pt;}}
            QLabel#conversationTitle{{font-size:17pt;padding:0;}} QLabel#panelTitle{{font-size:19pt;font-weight:600;}}
            QLabel#statusPill{{background:{surface};border-radius:12px;padding:5px 10px;font-size:10pt;}}
            QLabel#connectionIndicator{{color:{'#a9b5c4' if dark else '#576577'};font-size:10pt;}}
            QComboBox{{padding:5px 8px;min-height:22px;}} QPushButton{{padding:7px 10px;min-height:19px;}}
            QProgressBar{{border:0;border-radius:5px;background:{surface};height:9px;text-align:center;}}
            QProgressBar::chunk{{background:#32b8a0;border-radius:5px;}}
            QScrollBar:vertical{{background:transparent;width:9px;margin:0;}} QScrollBar::handle:vertical{{background:{border};border-radius:4px;min-height:28px;}}
            QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}
        ''')
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
            body=re.search(r'<body[^>]*>(.*)</body>',document.toHtml(),re.S).group(1);body=body.replace('margin-top:12px;','margin-top:4px;')
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
            parts.append(f'<table width="100%" cellspacing="0" cellpadding="12" bgcolor="{color}" style="border:0;"><tr><td style="border:0;background-color:{color};"><b>{name}</b>{body}{"".join(attachments)}{state}</td></tr></table><br>')
        bar=self.chat.verticalScrollBar();bottom=bar.value()>=bar.maximum()-40;position=bar.value()
        self.chat.setHtml(''.join(parts))
        bar.setValue(bar.maximum() if bottom else position)
        self.attachment_list.setVisible(bool(self.pending))

    def closeEvent(self,event):
        if not getattr(self,'explicit_quit',False) and self.broker.projects.queue.active() and hasattr(self,'attention') and self.attention.tray.isVisible():
            self.hide();self.attention.tray.setToolTip('Codex Desktop Assistant — project work continues; open to Stop or Quit');event.ignore();return
        self.permissions.halt();self.engine.interrupt.set()
        if self.engine.turn_cancel:self.engine.turn_cancel.set()
        for request in self.requests:request['event'].set()
        for dialog in self.findChildren(QDialog):dialog.close()
        self.broker.projects.stop()
        self.broker.projects.close()
        for fixture in getattr(self,'builder_fixtures',[]):fixture.close()
        if getattr(self,'project_dashboard',None):self.project_dashboard.timer.stop();self.project_dashboard.close()
        if hasattr(self,'input_guard'):self.input_guard.close()
        if hasattr(self,'attention'):self.attention.tray.hide()
        super().closeEvent(event)
