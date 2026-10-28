"""Disposable native UI fixture. No network, accounts or production files."""
import argparse
import json
import sys
from pathlib import Path
from PySide6.QtCore import Qt,QTimer
from PySide6.QtGui import QPainter,QColor,QFont
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QLabel,QLineEdit,QComboBox,QCheckBox,QPushButton


class Visual(QWidget):
    def __init__(self,code):
        super().__init__();self.code=code;self.setMinimumHeight(120)
    def paintEvent(self,event):
        p=QPainter(self);p.fillRect(self.rect(),QColor('#0f766e'));p.setPen(QColor('white'));p.setFont(QFont('Segoe UI',26));p.drawText(self.rect(),Qt.AlignCenter,self.code)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--state',required=True);parser.add_argument('--code',default='LIME-742');parser.add_argument('--manual-file');parser.add_argument('--title',default='Assistant Control Lab');parser.add_argument('--action-label',default='Apply draft');args=parser.parse_args()
    app=QApplication([]);window=QWidget();window.setWindowTitle(args.title);window.resize(640,500)
    layout=QVBoxLayout(window);layout.addWidget(QLabel('Disposable desktop verification'))
    layout.addWidget(Visual(args.code))
    name=QLineEdit();name.setAccessibleName('Greeting');name.setPlaceholderText('Greeting');layout.addWidget(name)
    theme=QComboBox();theme.setAccessibleName('Theme');theme.addItems(['Navy','Teal','Coral']);layout.addWidget(theme)
    check=QCheckBox('Ready');layout.addWidget(check)
    status=QLabel('Waiting');layout.addWidget(status)
    def save():
        value={'greeting':name.text(),'theme':theme.currentText(),'ready':check.isChecked()}
        Path(args.state).write_text(json.dumps(value));status.setText('Saved draft: '+name.text())
    action=QPushButton(args.action_label);action.clicked.connect(save);layout.addWidget(action)
    name.textChanged.connect(lambda text:None)
    # An owner-only test harness can simulate a manual edit while model control
    # is paused. This local fixture channel never exists in the shipped app.
    timer=QTimer(window)
    def manual():
        if not args.manual_file:return
        path=Path(args.manual_file)
        if path.exists():
            value=json.loads(path.read_text());name.setText(value['greeting']);path.unlink()
            path.with_suffix('.applied').write_text('manual edit applied')
    timer.timeout.connect(manual);timer.start(50)
    window.show();app.exec()


if __name__=='__main__':main()
