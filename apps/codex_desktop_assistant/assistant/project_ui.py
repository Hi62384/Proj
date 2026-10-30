"""Optional task dashboard; normal workflow remains chat → scope → results."""
import json
from PySide6.QtCore import Qt,QTimer,QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QTableWidget,QTableWidgetItem,QPushButton,QPlainTextEdit,QFileDialog,QInputDialog


class ProjectDashboard(QDialog):
    def __init__(self,window):
        super().__init__(window);self.window=window;self.queue=window.broker.projects.queue
        self.setWindowTitle('Projects and completed work');self.resize(1000,650)
        layout=QVBoxLayout(self);self.selector=QComboBox();layout.addWidget(self.selector)
        self.summary=QLabel();self.summary.setWordWrap(True);layout.addWidget(self.summary)
        self.table=QTableWidget(0,6);self.table.setHorizontalHeaderLabels(['Task','Stage','State','Priority','Attempts','Details']);self.table.setEditTriggers(QTableWidget.NoEditTriggers);layout.addWidget(self.table,1)
        row=QHBoxLayout()
        for title,callback in [('Start / Continue',lambda:self.control('resume')),('Pause',lambda:self.control('pause')),('Cancel project',lambda:self.control('cancel')),('Revoke launch',self.revoke),('Retry selected',self.retry),('Prioritize selected',self.prioritize),('Open deliverables',self.open_files),('Import task list',self.import_tasks)]:
            button=QPushButton(title);button.clicked.connect(callback);row.addWidget(button)
        layout.addLayout(row);self.detail=QPlainTextEdit();self.detail.setReadOnly(True);self.detail.setMaximumHeight(135);layout.addWidget(self.detail)
        revise=QPushButton('Change objective and pause affected work');revise.clicked.connect(self.revise);layout.addWidget(revise)
        self.offset=0;pages=QHBoxLayout()
        for label,change in [('Previous 100',-100),('Next 100',100)]:
            button=QPushButton(label);button.clicked.connect(lambda checked=False,n=change:self.page(n));pages.addWidget(button)
        layout.addLayout(pages);self.selector.currentIndexChanged.connect(self.changed);self.table.itemSelectionChanged.connect(self.inspect)
        synthetic=QPushButton('Run local five-product test');synthetic.clicked.connect(self.run_synthetic);layout.addWidget(synthetic)
        self.timer=QTimer(self);self.timer.timeout.connect(self.refresh);self.timer.start(1000);self.refresh()

    def page(self,change):self.offset=max(0,self.offset+change);self.refresh()
    def run_synthetic(self):self.window.synthetic_workflow();self.close()
    def changed(self):self.offset=0;self.refresh()
    def selected_project(self):
        project=self.selector.currentData()
        return self.queue.rows('SELECT * FROM projects WHERE id=?',(project,))[0] if project else None
    def refresh(self):
        projects=self.queue.rows('SELECT * FROM projects ORDER BY updated DESC LIMIT 100');selected=self.selector.currentData()
        if [self.selector.itemData(i) for i in range(self.selector.count())]!=[p['id'] for p in projects]:
            self.selector.blockSignals(True);self.selector.clear()
            for p in projects:self.selector.addItem(p['objective'].splitlines()[0][:100],p['id'])
            index=self.selector.findData(selected)
            if index>=0:self.selector.setCurrentIndex(index)
            self.selector.blockSignals(False)
        p=self.selected_project()
        if not p:self.summary.setText('Describe a large goal in chat to start a durable project.');return
        result=self.queue.summary(p['id'],p['conversation'],self.offset,100);counts=result['counts']
        self.summary.setText(p['state'].capitalize()+' · '+str(result['total'])+' tasks · '+', '.join(f'{k}: {v}' for k,v in counts.items())+'\nLocal checkpoints persist. Asleep/disconnected processes do not execute work. Blocked work requires resolving the specific missing condition.')
        selected_job=self.table.item(self.table.currentRow(),0).data(Qt.UserRole) if self.table.currentRow()>=0 and self.table.item(self.table.currentRow(),0) else None
        self.table.blockSignals(True);self.table.setRowCount(len(result['jobs']))
        for row,job in enumerate(result['jobs']):
            for col,value in enumerate([job['key'],job['kind'],job['state'],job['priority'],job['attempts'],job['error']]):
                item=QTableWidgetItem(str(value));item.setData(Qt.UserRole,job['id']);self.table.setItem(row,col,item)
            if job['id']==selected_job:self.table.selectRow(row)
        self.table.blockSignals(False);self.table.resizeColumnsToContents()
    def control(self,operation):
        p=self.selected_project()
        if p:
            try:
                if operation in ('pause','cancel'):self.interrupt_child(p)
                self.queue.control(p['id'],p['conversation'],operation);self.refresh()
            except Exception as error:self.detail.setPlainText(str(error))
    def interrupt_child(self,p):
        if self.window.engine.active and self.queue.rows("SELECT id FROM jobs WHERE project=? AND conversation=? AND state='waiting_ai'",(p['id'],self.window.engine.active)):
            self.window.engine.pause()
    def revise(self):
        p=self.selected_project()
        if not p:return
        text,accepted=QInputDialog.getMultiLineText(self,'Change project objective','Completed work is retained; remaining work and launch authorization will require review.',p['objective'])
        if accepted and text.strip():
            self.interrupt_child(p);self.queue.revise(p['id'],p['conversation'],text);self.refresh()
    def revoke(self):
        p=self.selected_project()
        if p:self.queue.revoke_scope(p['id'],p['conversation']);self.refresh()
    def job(self):return self.table.item(self.table.currentRow(),0)
    def retry(self):
        p=self.selected_project();item=self.job()
        if p and item:
            try:self.queue.retry(p['id'],p['conversation'],item.data(Qt.UserRole));self.refresh()
            except Exception as error:self.detail.setPlainText(str(error))
    def prioritize(self):
        p=self.selected_project();item=self.job()
        if p and item:self.queue.priority(p['id'],p['conversation'],item.data(Qt.UserRole),100);self.refresh()
    def open_files(self):
        p=self.selected_project()
        if p:
            path=self.queue.root/p['id']/'artifacts';path.mkdir(parents=True,exist_ok=True);QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
    def inspect(self):
        item=self.job();p=self.selected_project()
        if item and p:
            row=self.queue.rows('SELECT key,payload,result,error FROM jobs WHERE id=? AND project=?',(item.data(Qt.UserRole),p['id']))
            if row:self.detail.setPlainText(json.dumps(row[0],indent=2,ensure_ascii=False))
    def import_tasks(self):
        p=self.selected_project()
        if not p:return
        path,_=QFileDialog.getOpenFileName(self,'Import task list','','Task lists (*.txt *.md *.csv *.tsv *.json *.xlsx)')
        if not path:return
        try:
            record=self.window.attachments.add(path)
            self.window.store.add(p['conversation'],'user','Imported task list','saved',[record])
            self.queue.import_attachment(p['id'],p['conversation'],record,self.window.attachments);self.refresh()
        except Exception as error:self.detail.setPlainText(str(error))
