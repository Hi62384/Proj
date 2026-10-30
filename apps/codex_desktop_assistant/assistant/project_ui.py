"""Optional task dashboard; normal workflow remains chat → scope → results."""
import json
from PySide6.QtCore import Qt,QTimer,QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QTableWidget,QTableWidgetItem,QPushButton,QPlainTextEdit,QFileDialog,QInputDialog
from PySide6.QtWidgets import QListWidget,QListWidgetItem,QSplitter,QWidget,QProgressBar,QTreeWidget,QTreeWidgetItem,QScrollArea


class ProjectDashboard(QDialog):
    def __init__(self,window):
        super().__init__(window);self.window=window;self.queue=window.broker.projects.queue;self.current=None;self.card_signature=None
        self.setWindowTitle('Projects');self.resize(1100,730)
        layout=QVBoxLayout(self);header=QHBoxLayout();title=QLabel('Your projects');title.setObjectName('panelTitle');header.addWidget(title);header.addStretch();advanced=QPushButton('Advanced');advanced.clicked.connect(self.advanced);header.addWidget(advanced);layout.addLayout(header)
        split=QSplitter();layout.addWidget(split,1);self.cards=QListWidget();self.cards.setMinimumWidth(300);split.addWidget(self.cards)
        body=QWidget();detail=QVBoxLayout(body);self.heading=QLabel('Describe a goal in chat');self.heading.setObjectName('panelTitle');self.heading.setWordWrap(True);detail.addWidget(self.heading)
        self.objective=QLabel('Projects are created and managed by Codex. Use this overview to follow progress and review results.');self.objective.setWordWrap(True);detail.addWidget(self.objective)
        self.summary=QLabel();self.summary.setWordWrap(True);detail.addWidget(self.summary);self.progress=QProgressBar();detail.addWidget(self.progress)
        controls=QHBoxLayout();self.controls={}
        for text,method in [('View Results',self.results),('Pause Project',lambda:self.control('pause')),('Resume Project',lambda:self.control('resume')),('Stop Project',self.stop)]:
            button=QPushButton(text);button.clicked.connect(method);controls.addWidget(button);self.controls[text]=button
        detail.addLayout(controls);self.products=QTreeWidget();self.products.setHeaderLabels(['Products and results','Progress','Status']);self.products.itemClicked.connect(self.preview_product);detail.addWidget(self.products,1)
        self.preview=QLabel('Select a product to view its generated preview.');self.preview.setAlignment(Qt.AlignCenter);self.preview.setMinimumHeight(150);self.preview.hide();detail.addWidget(self.preview)
        self.blockers=QLabel();self.blockers.setWordWrap(True);detail.addWidget(self.blockers)
        split.addWidget(body);split.setSizes([340,720]);self.cards.currentItemChanged.connect(self.select)
        self.timer=QTimer(self);self.timer.timeout.connect(self.refresh);self.timer.start(1000);self.refresh()

    def selected_project(self):
        rows=self.queue.rows('SELECT * FROM projects WHERE id=?',(self.current,))
        return rows[0] if rows else None

    def refresh(self):
        projects=self.queue.rows('SELECT * FROM projects ORDER BY updated DESC LIMIT 200')
        summaries={p['id']:self.queue.summary(p['id'],p['conversation'],limit=1) for p in projects}
        signature=tuple((p['id'],p['state'],tuple(sorted(summaries[p['id']]['counts'].items()))) for p in projects)
        if signature!=self.card_signature:
            self.card_signature=signature;self.cards.blockSignals(True);self.cards.clear()
            for p in projects:
                counts=summaries[p['id']]['counts'];done=counts.get('completed',0);total=summaries[p['id']]['total'];item=QListWidgetItem()
                item.setData(Qt.UserRole,p['id']);card=QWidget();box=QVBoxLayout(card);name=QLabel(p['objective'].splitlines()[0][:68]);name.setWordWrap(True);name.setStyleSheet('font-weight:600');box.addWidget(name)
                from .status import resolve
                status=resolve(project=summaries[p['id']]);box.addWidget(QLabel(f'{status} · {done}/{total} tasks · {max(0,total-done)} remaining'))
                generated=self.queue.rows("SELECT kind,COUNT(*) count FROM jobs WHERE project=? AND state='completed' AND kind IN ('package','verify') GROUP BY kind",(p['id'],));stages={r['kind']:r['count'] for r in generated}
                box.addWidget(QLabel(f"Products: {stages.get('package',0)} · Launched: {stages.get('verify',0)} · Blocked: {counts.get('blocked',0)+counts.get('review',0)}"))
                import datetime
                box.addWidget(QLabel('Last activity '+datetime.datetime.fromtimestamp(p['updated']).strftime('%b %d, %H:%M')))
                bar=QProgressBar();bar.setValue(round(100*done/max(1,total)));box.addWidget(bar);item.setSizeHint(card.sizeHint());self.cards.addItem(item);self.cards.setItemWidget(item,card)
                if p['id']==self.current:self.cards.setCurrentItem(item)
            self.cards.blockSignals(False)
            if self.current is None and self.cards.count():self.cards.setCurrentRow(0)
        p=self.selected_project()
        if not p:return
        result=summaries[p['id']];counts=result['counts'];self.heading.setText(p['objective'].splitlines()[0][:90]);self.objective.setText(p['objective'][:1500]);self.summary.setText(f"{result['total']} tasks · {counts.get('completed',0)} completed · {counts.get('running',0)+counts.get('waiting_ai',0)} running · {counts.get('blocked',0)+counts.get('review',0)} blocked");self.progress.setValue(round(100*counts.get('completed',0)/max(1,result['total'])))
        for name,button in self.controls.items():button.setVisible(name=='View Results' or (name=='Pause Project' and p['state']=='running') or (name=='Resume Project' and p['state'] in ('draft','paused','blocked')) or (name=='Stop Project' and p['state']=='running'))
        jobs=self.queue.rows('SELECT key,kind,state,payload,error FROM jobs WHERE project=? ORDER BY rowid',(p['id'],));grouped={};errors=[]
        for job in jobs:
            product=json.loads(job['payload']).get('product',{});key=product.get('id') or job['key'];grouped.setdefault(key,[]).append((job,product))
            if job['error'] and job['state'] in ('blocked','failed','review'):errors.append(job['key']+': '+job['error'])
        tree_signature=tuple((j['key'],j['state']) for j in jobs)
        if getattr(self,'tree_signature',None)!=(self.current,tree_signature):
            self.tree_signature=(self.current,tree_signature);self.products.clear()
            for key,entries in grouped.items():
                title=entries[0][1].get('title') or key;done=sum(job['state']=='completed' for job,_ in entries);row=QTreeWidgetItem([title,f'{done}/{len(entries)}','Completed' if done==len(entries) else 'Working' if any(j['state']=='running' for j,_ in entries) else 'Needs attention' if any(j['state'] in ('blocked','failed','review') for j,_ in entries) else 'Planned']);row.setData(0,Qt.UserRole,key);self.products.addTopLevelItem(row)
                for job,_ in entries:QTreeWidgetItem(row,[{'generate':'Create files','validate':'Quality checks','package':'Package delivery','publish':'Prepare listing','verify':'Verify result'}.get(job['kind'],'Research / planning'),'',job['state']])
            self.products.resizeColumnToContents(0)
        self.blockers.setText(('Needs attention\n'+'\n'.join(errors[:3])) if errors else 'No unresolved blockers.');self.blockers.setVisible(bool(errors))

    def select(self,item,previous):
        if item:self.current=item.data(Qt.UserRole);self.refresh()

    def preview_product(self,item,column):
        if item.parent():item=item.parent()
        p=self.selected_project()
        if not p:return
        try:
            result=self.queue.result(p['id'],p['conversation'],item.data(0,Qt.UserRole)+':validate')
            if result['state']!='completed':return
            from .products import ProductFactory
            from PySide6.QtGui import QPixmap
            factory=ProductFactory(self.queue.root/p['id']/'artifacts');path=factory.path(result['result']['previews'][0]);self.preview.setPixmap(QPixmap(str(path)).scaled(620,230,Qt.KeepAspectRatio,Qt.SmoothTransformation));self.preview.show()
        except (ValueError,KeyError):self.preview.setText('Preview not available yet.')

    def control(self,operation):
        p=self.selected_project()
        if not p:return
        try:
            if operation=='pause' and self.window.engine.active and self.queue.rows("SELECT id FROM jobs WHERE project=? AND conversation=? AND state='waiting_ai'",(p['id'],self.window.engine.active)):self.window.engine.pause()
            self.queue.control(p['id'],p['conversation'],operation);self.refresh()
        except Exception as error:self.blockers.setText(str(error));self.blockers.show()
    def stop(self):
        p=self.selected_project()
        if p:self.control('pause');self.queue.revoke_scope(p['id'],p['conversation'])
    def results(self):
        p=self.selected_project()
        if p:
            path=self.queue.root/p['id']/'artifacts';path.mkdir(parents=True,exist_ok=True);QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
    def advanced(self):
        self.advanced_dialog=AdvancedProjectDashboard(self.window);self.advanced_dialog.show()

    def closeEvent(self,event):
        self.timer.stop()
        if getattr(self,'advanced_dialog',None):self.advanced_dialog.close()
        super().closeEvent(event)


class AdvancedProjectDashboard(QDialog):
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
    def closeEvent(self,event):self.timer.stop();super().closeEvent(event)
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
