"""Everyday chat layout; existing controller settings live in one Control Center."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,
    QLineEdit,QListWidget,QCheckBox,QSplitter,QScrollArea,QGroupBox,QPlainTextEdit,
    QFrame,QDialog,QTabWidget,QProgressBar,QMenu)
from .ui_base import ChatView,Composer,button as base_button
from PySide6.QtWidgets import QStyle


def button(text,slot):
    item=base_button(text,slot)
    icon={'+ New Chat':QStyle.SP_FileIcon,'Projects':QStyle.SP_DirOpenIcon,'Settings':QStyle.SP_FileDialogDetailedView,'Control Center':QStyle.SP_ComputerIcon,'Stop':QStyle.SP_MediaStop,'Send':QStyle.SP_ArrowUp,'Attach':QStyle.SP_FileIcon,'Requests':QStyle.SP_MessageBoxInformation}.get(text)
    if icon is not None:item.setIcon(item.style().standardIcon(icon))
    return item


def build(window):
    w=window;root=QWidget();root.setObjectName('appRoot');w.setCentralWidget(root)
    outer=QVBoxLayout(root);outer.setContentsMargins(0,0,0,0);outer.setSpacing(0)
    toolbar=QWidget();toolbar.setObjectName('toolbar');top=QHBoxLayout(toolbar);top.setContentsMargins(18,10,18,10)
    top.addWidget(QLabel('CODEX'))
    w.model=QComboBox();w.model.setObjectName('modelSelector');w.model.setMinimumWidth(155);w.model.setMaximumWidth(270);w.model.currentIndexChanged.connect(w.model_changed);top.addWidget(w.model)
    w.effort=QComboBox();w.effort.setToolTip('Reasoning effort');w.effort.setMinimumWidth(100);w.effort.setMaximumWidth(150);w.effort.currentIndexChanged.connect(w.effort_changed);top.addWidget(w.effort)
    top.addStretch();w.connection=QLabel('Connecting…');w.connection.setObjectName('connectionIndicator');top.addWidget(w.connection)
    w.status=QLabel('Ready');w.status.setObjectName('statusPill');top.addWidget(w.status)
    w.attention_button=button('Requests',w.show_requests);top.addWidget(w.attention_button)
    top.addWidget(button('Stop',w.stop));outer.addWidget(toolbar)
    w.main_split=QSplitter(Qt.Horizontal);outer.addWidget(w.main_split,1)
    w.sidebar=QWidget();w.sidebar.setObjectName('sidebar');side=QVBoxLayout(w.sidebar);side.setContentsMargins(12,16,12,12);side.setSpacing(10)
    side.addWidget(button('+ New Chat',w.new_chat));w.search=QLineEdit();w.search.setPlaceholderText('Search conversations');w.search.textChanged.connect(w.load_list);side.addWidget(w.search)
    label=QLabel('PINNED & RECENT');label.setObjectName('sectionLabel');side.addWidget(label)
    w.list=QListWidget();w.list.setObjectName('conversationList');w.list.currentItemChanged.connect(w.select);side.addWidget(w.list,1)
    def selection_changed():
        items=w.list.selectedItems()
        if len(items)==1 and items[0].data(Qt.UserRole)!=w.selected:w.select(items[0],None)
    w.list.itemSelectionChanged.connect(selection_changed)
    w.list.setContextMenuPolicy(Qt.CustomContextMenu)
    def context(position):
        item=w.list.itemAt(position)
        if not item:return
        w.list.setCurrentItem(item);menu=QMenu(w)
        for title,slot in [('Rename',w.rename),('Pin / unpin',w.pin),('Archive / restore',w.archive),('Delete local history',w.delete_history)]:menu.addAction(title,slot)
        menu.exec(w.list.mapToGlobal(position))
    w.list.customContextMenuRequested.connect(context)
    w.archived=QCheckBox('Archived');w.archived.toggled.connect(w.load_list);side.addWidget(w.archived)
    side.addWidget(button('Projects',w.show_projects));side.addWidget(button('Control Center',w.show_control_center));side.addWidget(button('Settings',w.settings));w.main_split.addWidget(w.sidebar)
    center=QWidget();center.setObjectName('chatCenter');chat=QVBoxLayout(center);chat.setContentsMargins(24,18,24,12);chat.setSpacing(10)
    header=QHBoxLayout();w.title=QLabel('New conversation');w.title.setWordWrap(True);w.title.setObjectName('conversationTitle');header.addWidget(w.title);header.addStretch();header.addWidget(button('Activity',lambda:w.activity.setVisible(not w.activity.isVisible())));chat.addLayout(header)
    w.chat=ChatView();w.chat.setOpenLinks(False);w.chat.anchorClicked.connect(w.open_link);chat.addWidget(w.chat,1)
    w.approvals_widget=QWidget();w.approvals_layout=QVBoxLayout(w.approvals_widget);w.approvals_layout.setContentsMargins(0,0,0,0);chat.addWidget(w.approvals_widget);w.approvals_widget.hide()
    w.notice=QLabel('Describe a goal. Codex will plan the work and ask only when it needs you.');w.notice.setWordWrap(True);w.notice.setObjectName('notice');chat.addWidget(w.notice)
    w.attachment_list=QListWidget();w.attachment_list.setMaximumHeight(65);w.attachment_list.itemDoubleClicked.connect(w.preview_attachment);chat.addWidget(w.attachment_list);w.attachment_list.hide()
    composer=QFrame();composer.setObjectName('composerFrame');compose=QVBoxLayout(composer);compose.setContentsMargins(10,8,10,8);compose.setSpacing(4)
    w.input=Composer();w.input.setObjectName('Composer');w.input.setMinimumHeight(65);w.input.setMaximumHeight(150);w.input.setPlaceholderText('Describe a task, or ask anything…');w.input.send.connect(w.send);compose.addWidget(w.input)
    actions=QHBoxLayout();actions.addWidget(button('Attach',w.pick_files));w.remove_attachment_button=button('Remove attachment',w.remove_attachment);w.remove_attachment_button.hide();actions.addWidget(w.remove_attachment_button);actions.addStretch();hint=QLabel('Ctrl+Enter to send');hint.setObjectName('muted');actions.addWidget(hint);send=button('Send',w.send);send.setObjectName('send');actions.addWidget(send);compose.addLayout(actions);chat.addWidget(composer)
    bottom=QHBoxLayout();bottom.addWidget(button('Chats',lambda:w.sidebar.setVisible(not w.sidebar.isVisible())));bottom.addStretch();w.task_controls=QWidget();resume=QHBoxLayout(w.task_controls);resume.setContentsMargins(0,0,0,0);resume.addWidget(button('Continue',w.resume));bottom.addWidget(w.task_controls);chat.addLayout(bottom);w.main_split.addWidget(center)
    activity=QWidget();activity.setObjectName('activityPanel');right=QVBoxLayout(activity);right.setContentsMargins(16,18,16,12)
    heading=QLabel('Task activity');heading.setObjectName('panelTitle');right.addWidget(heading)
    w.activity_summary=QLabel('Ready for your next task');w.activity_summary.setWordWrap(True);right.addWidget(w.activity_summary)
    w.active_application=QLabel('No application in use');w.active_application.setWordWrap(True);right.addWidget(w.active_application)
    w.project_progress=QProgressBar();w.project_progress.setRange(0,100);w.project_progress.setValue(0);right.addWidget(w.project_progress)
    w.browser_activity=QLabel('Browser ready');w.browser_activity.setWordWrap(True);right.addWidget(w.browser_activity)
    w.preview=QLabel('Approved visual observations appear here when needed.');w.preview.setWordWrap(True);w.preview.setAlignment(Qt.AlignCenter);w.preview.setMinimumHeight(120);right.addWidget(w.preview)
    technical=QGroupBox('Technical Details');technical.setCheckable(True);technical.setChecked(False);details=QVBoxLayout(technical);w.activity_text=QPlainTextEdit();w.activity_text.setReadOnly(True);w.activity_text.hide();details.addWidget(w.activity_text);technical.toggled.connect(w.activity_text.setVisible);right.addWidget(technical);right.addStretch()
    w.activity=QScrollArea();w.activity.setWidgetResizable(True);w.activity.setWidget(activity);w.main_split.addWidget(w.activity);w.main_split.setSizes([235,900,285]);w.main_split.setStretchFactor(1,1)
    control_center(w)
    for name in ('observation','desktop_toggle','top_desktop','top_browser'):
        widget=QCheckBox(w);widget.hide();setattr(w,name,widget)
    workflow=w.menuBar().addMenu('Workflows');workflow.addAction('Prepare Cedargrid draft',w.cedargrid_workflow);workflow.addAction('Projects and completed work',w.show_projects);workflow.addAction('Run authorized local five-product test',w.synthetic_workflow);workflow.addAction('Run local builder test',w.synthetic_builder_workflow)
    w.menuBar().addAction('Quit application',w.quit_application);w.menuBar().hide()
    w.refresh_targets()


def control_center(w):
    dialog=QDialog(w);dialog.setWindowTitle('Control Center');dialog.resize(720,700);layout=QVBoxLayout(dialog)
    intro=QLabel('Choose how Codex can work. Browser scope and sensitive-action approvals remain separate.');intro.setWordWrap(True);layout.addWidget(intro)
    tabs=QTabWidget();layout.addWidget(tabs,1)
    browser=QWidget();page=QVBoxLayout(browser);tabs.addTab(browser,'Browser')
    w.browser_mode=QComboBox();w.browser_mode.addItems(['Dedicated Browser','Existing Chrome']);page.addWidget(w.browser_mode)
    w.chrome_panel=QGroupBox('Existing Chrome');chrome=QVBoxLayout(w.chrome_panel);w.chrome_connection=QLabel('Extension disconnected');w.chrome_connection.setWordWrap(True);chrome.addWidget(w.chrome_connection)
    chrome.addWidget(button('Browser access settings',w.open_browser_access));chrome.addWidget(button('Connect Chrome',w.connect_chrome))
    advanced=QGroupBox('Advanced tab controls');advanced.setCheckable(True);advanced.setChecked(False);advanced_layout=QVBoxLayout(advanced);tab_controls=QWidget();tab_rows=QVBoxLayout(tab_controls)
    for name,slot in [('Chrome Tabs / Select Window',w.chrome_tabs),('Attach Tab',w.chrome_attach),('Release Tab',w.chrome_release),('Show Tab',w.chrome_show),('Check Connection',w.chrome_health)]:tab_rows.addWidget(button(name,slot))
    advanced_layout.addWidget(tab_controls);tab_controls.hide();advanced.toggled.connect(tab_controls.setVisible);chrome.addWidget(advanced)
    w.chrome_manual=QCheckBox('Manual Control for Chrome Tab');w.chrome_manual.toggled.connect(w.chrome_manual_control);chrome.addWidget(w.chrome_manual);page.addWidget(w.chrome_panel)
    w.chrome_dialog=None;w.chrome_selected_tab=None
    w.dedicated_widgets=[];w.browser_toggle=QCheckBox('Enable dedicated browser');w.browser_toggle.toggled.connect(w.toggle_browser);page.addWidget(w.browser_toggle);w.dedicated_widgets.append(w.browser_toggle)
    for label,op in [('Open Browser','open'),('Show Browser','show'),('Browser Tabs','tabs')]:
        item=button(label,lambda checked=False,operation=op:w.browser_control(operation));page.addWidget(item);w.dedicated_widgets.append(item)
    w.background_browser=QCheckBox('Work in background');w.background_browser.setChecked(True);w.background_browser.toggled.connect(lambda on:w.browser_control('background',enabled=on));page.addWidget(w.background_browser)
    w.manual_browser=QCheckBox('Manual Control');w.manual_browser.toggled.connect(w.browser_manual);page.addWidget(w.manual_browser);w.dedicated_widgets.append(w.manual_browser)
    w.public_browser=QCheckBox('Public browsing for dedicated browser');w.public_browser.toggled.connect(lambda on:w.browser_control('public',enabled=on));page.addWidget(w.public_browser);w.dedicated_widgets.append(w.public_browser);page.addStretch()
    w.browser_tabs_state=[];w.browser_tabs_dialog=None
    desktop=QWidget();controls=QVBoxLayout(desktop);tabs.addTab(desktop,'Computer')
    w.access_mode=QComboBox();w.access_mode.addItems(['Selected Window','Entire Monitor']);w.access_mode.currentIndexChanged.connect(w.refresh_targets);controls.addWidget(w.access_mode)
    w.access_target=QComboBox();controls.addWidget(w.access_target)
    row=QHBoxLayout()
    for name,slot in [('Refresh',w.refresh_targets),('Enable Access',w.enable_access),('Revoke',w.revoke_desktop)]:row.addWidget(button(name,slot))
    controls.addLayout(row);w.launch_toggle=QCheckBox('Allow Program Launches');w.launch_toggle.toggled.connect(w.toggle_launches);controls.addWidget(w.launch_toggle)
    w.observation_indicator=QLabel('Observation OFF');controls.addWidget(w.observation_indicator);controls.addWidget(button('Preview approved screen',w.capture_preview));w.grants=QLabel();w.grants.setWordWrap(True);controls.addWidget(w.grants);controls.addWidget(button('File permissions',w.file_permissions));controls.addStretch()
    diagnostics=QWidget();tools=QVBoxLayout(diagnostics);tabs.addTab(diagnostics,'Diagnostics');tools.addWidget(QLabel('Opt-in local acceptance tests. No real publication.'));tools.addWidget(button('Run local builder test',w.synthetic_builder_workflow));tools.addWidget(button('Run local five-product test',w.synthetic_workflow));tools.addStretch()
    layout.addWidget(button('Close',dialog.close));w.control_center=dialog
    w.browser_mode.currentIndexChanged.connect(w.select_browser_mode)
    default=w.store.settings().get('browser_mode','Existing Chrome' if (w.store.directory/'chrome-host/settings.json').is_file() else 'Dedicated Browser')
    w.browser_mode.setCurrentText(default);w.select_browser_mode()
