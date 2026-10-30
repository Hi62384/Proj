"""Unresolved owner requests; opening this panel never normalizes the main window."""
from PySide6.QtCore import Qt,QTimer
from PySide6.QtWidgets import QDialog,QVBoxLayout,QLabel,QScrollArea,QWidget,QGroupBox,QHBoxLayout,QPushButton
from .status import pending


class RequestsPanel(QDialog):
    def __init__(self,window):
        super().__init__(window);self.window=window;self.setWindowTitle('Requests');self.resize(580,520)
        layout=QVBoxLayout(self);heading=QLabel('Needs your attention');heading.setObjectName('panelTitle');layout.addWidget(heading)
        scroll=QScrollArea();scroll.setWidgetResizable(True);self.body=QWidget();self.rows=QVBoxLayout(self.body);scroll.setWidget(self.body);layout.addWidget(scroll)
        self.signature=None;self.timer=QTimer(self);self.timer.timeout.connect(self.refresh);self.timer.start(300);self.refresh()
    def refresh(self):
        requests=pending(self.window.requests,self.window.permissions);signature=tuple(id(r) for r in requests)
        if signature==self.signature:return
        self.signature=signature
        while self.rows.count():
            item=self.rows.takeAt(0)
            if item.widget():item.widget().deleteLater()
        if not requests:
            message=QLabel('All clear. There are no unresolved requests.');message.setWordWrap(True);self.rows.addWidget(message)
        for request in requests:
            args=request['args'];box=QGroupBox('Human step' if args.get('manual_step') else 'Approval');form=QVBoxLayout(box)
            title=QLabel(request['label']);title.setTextFormat(Qt.PlainText);title.setWordWrap(True);form.addWidget(title)
            target=args.get('origin') or args.get('path') or args.get('target_context',{}).get('page_url') or args.get('target_context',{}).get('application','')
            explanation=QLabel(('Where: '+target+'\n' if target else '')+'Why: '+str(args.get('approval_reason') or args.get('reason') or 'This action needs an owner decision.')+'\nWhat to do: '+('Complete the step privately, then choose Done — Continue.' if args.get('manual_step') else 'Review this exact action and allow or deny it.')+'\nCodex will receive your decision and verify the current state before continuing.')
            explanation.setTextFormat(Qt.PlainText);explanation.setWordWrap(True);form.addWidget(explanation)
            original=next((card for r,card in self.window.request_cards if r is request),None)
            buttons=QHBoxLayout()
            if original:
                for source in original.findChildren(QPushButton):
                    if source.text() not in ('Allow Once','Allow for This Session','Done — Continue','Deny','Cannot complete'):continue
                    button=QPushButton(source.text());button.clicked.connect(source.click);buttons.addWidget(button)
            form.addLayout(buttons);self.rows.addWidget(box)
        self.rows.addStretch()

    def closeEvent(self,event):self.timer.stop();super().closeEvent(event)
