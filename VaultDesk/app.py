"""VaultDesk — private, local-only business/password vault with a Qt interface."""
from __future__ import annotations

import copy
import secrets
import sys
import time
import uuid
from collections import Counter
from pathlib import Path
from typing import Any

from PySide6.QtCore import QEvent, QLockFile, QSize, Qt, QTimer, QUrl
from PySide6.QtGui import QAction, QColor, QDesktopServices, QFont, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog,
    QFormLayout, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QMessageBox, QPlainTextEdit, QProgressBar,
    QPushButton, QScrollArea, QSizePolicy, QSlider, QSpinBox, QStackedWidget,
    QToolButton, QVBoxLayout, QWidget,
)

from vault_core import AuthenticationError, Vault, VaultError, default_vault_path, utc_now

APP_NAME = "VaultDesk"

TYPES = {
    "Login": {
        "symbol": "◈", "color": "#8F84FF",
        "fields": [
            ("username", "Username or email", False),
            ("password", "Password", True),
            ("website", "Website URL", False),
            ("two_factor", "2FA recovery code", True),
        ],
    },
    "API Key": {
        "symbol": "⌘", "color": "#59D9C6",
        "fields": [
            ("service", "Service / provider", False),
            ("api_key", "API key / token", True),
            ("endpoint", "Project / endpoint", False),
            ("expires", "Expiry / renewal", False),
        ],
    },
    "Business": {
        "symbol": "▣", "color": "#FFBC7D",
        "fields": [
            ("legal_name", "Legal business name", False),
            ("registration", "Registration / tax ID", True),
            ("website", "Website URL", False),
            ("contact", "Primary contact", False),
        ],
    },
    "Finance": {
        "symbol": "◉", "color": "#76B8FF",
        "fields": [
            ("institution", "Institution / provider", False),
            ("account_number", "Account number / identifier", True),
            ("routing", "Routing / transit number", True),
            ("username", "Online account username", False),
        ],
    },
    "License": {
        "symbol": "◇", "color": "#E5A4FC",
        "fields": [
            ("product", "Product / subscription", False),
            ("license_key", "License key", True),
            ("renewal", "Renewal date", False),
            ("website", "Vendor website", False),
        ],
    },
    "Secure Note": {
        "symbol": "≡", "color": "#D0DBEE",
        "fields": [],
    },
}

STYLE = """
QWidget {
    background: #0B1120; color: #DFE7F5; font-family: 'Segoe UI', 'Arial'; font-size: 13px;
}
QMainWindow, QDialog { background: #0B1120; }
QLabel { background: transparent; }
QLabel#brand { font-size: 21px; font-weight: 800; color: #F4F7FF; }
QLabel#headline { font-size: 26px; font-weight: 800; color: #F4F7FF; }
QLabel#sectionTitle { font-size: 19px; font-weight: 750; color: #F4F7FF; }
QLabel#eyebrow { font-size: 10px; font-weight: 800; letter-spacing: 1px; color: #75859F; }
QLabel#muted { color: #8394AC; }
QLabel#detailValue { font-size: 14px; color: #EAF0FA; }
QLabel#largeNumber { font-size: 25px; font-weight: 750; color: #FAFBFF; }
QFrame#topbar { background: #10182A; border-bottom: 1px solid #253149; }
QFrame#side { background: #10182A; border-right: 1px solid #26334B; }
QFrame#listPanel { background: #0F1626; border-right: 1px solid #26334B; }
QFrame#detailPanel { background: #0B1120; }
QFrame#card { background: #151F32; border: 1px solid #2D3A53; border-radius: 14px; }
QFrame#statCard { background: #151F32; border: 1px solid #28364E; border-radius: 14px; }
QFrame#itemCard { background: #19253A; border: 1px solid #364761; border-radius: 11px; }
QFrame#itemCardActive { background: #25284A; border: 1px solid #897DFF; border-radius: 11px; }
QLineEdit, QPlainTextEdit, QSpinBox, QComboBox {
    background: #151F32; color: #F1F5FC; border: 1px solid #32415B;
    border-radius: 9px; padding: 9px 11px; selection-background-color: #615AD4;
}
QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus { border: 1px solid #8B7FFF; }
QLineEdit:disabled, QComboBox:disabled { color: #7889A0; }
QComboBox::drop-down { border: 0; width: 27px; }
QComboBox QAbstractItemView {
    background: #1C293E; border: 1px solid #4A5874;
    color: #F4F6FC; selection-background-color: #414D76;
}
QPushButton {
    background: #24324B; color: #E1E8F5; border: 1px solid #3A4B67;
    border-radius: 9px; padding: 9px 14px; font-weight: 650;
}
QPushButton:hover { background: #30415F; border-color: #5E7090; }
QPushButton:pressed { background: #202E43; }
QPushButton:disabled { color: #6B7990; background: #1A2639; border-color: #29364C; }
QPushButton#primary { background: #7969E9; color: white; border: 1px solid #8D80F8; }
QPushButton#primary:hover { background: #8F7FFF; }
QPushButton#danger { background: #3D202C; color: #FFB8BF; border-color: #6B3549; }
QPushButton#danger:hover { background: #592938; }
QPushButton#quiet { background: transparent; border: 1px solid transparent; color: #A5B3CC; }
QPushButton#quiet:hover { background: #223149; color: #E6ECFA; }
QPushButton#nav { background: transparent; border: 0px; border-radius: 9px;
    padding: 11px 15px; color: #B6C3D8; text-align: left; font-weight: 600; }
QPushButton#nav:hover { background: #22324A; color: #F1F5FF; }
QPushButton#navActive { background: #2D3159; border: 1px solid #645FA7;
    border-radius: 9px; padding: 10px 14px; color: #E2DFFF; text-align: left; font-weight: 750; }
QToolButton { background: #223149; border: 1px solid #364763; color: #D2DCF0;
    padding: 7px 10px; border-radius: 8px; }
QToolButton:hover { background: #344764; }
QListWidget { border: 0; background: transparent; outline: none; }
QListWidget::item { border: 0; margin: 0px; padding: 3px 5px; background: transparent; }
QListWidget::item:selected { background: transparent; }
QScrollArea { border: 0; background: transparent; }
QScrollBar:vertical { background: #10192A; width: 10px; border: 0; }
QScrollBar::handle:vertical { background: #3D4F68; border-radius: 5px; min-height: 24px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { height: 9px; background: #10192A; }
QScrollBar::handle:horizontal { background: #3D4F68; border-radius: 4px; }
QCheckBox { spacing: 8px; }
QCheckBox::indicator { width: 17px; height: 17px; }
QSlider::groove:horizontal { background: #34445E; height: 6px; border-radius: 3px; }
QSlider::handle:horizontal { background: #9588FF; width: 17px; height: 17px; margin: -6px 0; border-radius: 8px; }
QProgressBar { border-radius: 4px; border: 0; background: #26354C; text-align: center; }
QProgressBar::chunk { background: #65CDBF; border-radius: 4px; }
"""


def lbl(text: str, role: str | None = None, *, word_wrap: bool = False) -> QLabel:
    label = QLabel(text)
    label.setTextFormat(Qt.TextFormat.PlainText)
    if role:
        label.setObjectName(role)
    label.setWordWrap(word_wrap)
    return label


def btn(text: str, role: str | None = None) -> QPushButton:
    button = QPushButton(text)
    if role:
        button.setObjectName(role)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    return button


def spacer(height: int = 12) -> QWidget:
    w = QWidget()
    w.setFixedHeight(height)
    return w


def safe_text(text: Any) -> str:
    return text if isinstance(text, str) else ""


def make_password(length: int, uppercase: bool, lowercase: bool, digits: bool, symbols: bool) -> str:
    groups = []
    if uppercase:
        groups.append("ABCDEFGHJKLMNPQRSTUVWXYZ")
    if lowercase:
        groups.append("abcdefghijkmnopqrstuvwxyz")
    if digits:
        groups.append("23456789")
    if symbols:
        groups.append("!@#$%^&*()-_=+[]{}:,.?")
    if not groups:
        raise ValueError("Choose at least one character group.")
    if length < len(groups):
        raise ValueError("Length is too short for those character groups.")
    output = [secrets.choice(group) for group in groups]
    all_chars = "".join(groups)
    output.extend(secrets.choice(all_chars) for _ in range(length - len(output)))
    secrets.SystemRandom().shuffle(output)
    return "".join(output)


class SecretEdit(QWidget):
    def __init__(self, placeholder: str = "", *, generator: bool = False, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)
        self.field = QLineEdit()
        self.field.setPlaceholderText(placeholder)
        self.field.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.field, 1)
        self.reveal = QToolButton()
        self.reveal.setText("Show")
        self.reveal.setToolTip("Show or hide secret")
        self.reveal.clicked.connect(self.toggle)
        layout.addWidget(self.reveal)
        if generator:
            generate = QToolButton()
            generate.setText("Generate")
            generate.clicked.connect(self.generate)
            layout.addWidget(generate)

    def toggle(self):
        hidden = self.field.echoMode() == QLineEdit.EchoMode.Password
        self.field.setEchoMode(QLineEdit.EchoMode.Normal if hidden else QLineEdit.EchoMode.Password)
        self.reveal.setText("Hide" if hidden else "Show")

    def generate(self):
        dlg = GeneratorDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.field.setText(dlg.generated)

    def text(self) -> str:
        return self.field.text()

    def setText(self, text: str) -> None:
        self.field.setText(text)


class GeneratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate a secure password")
        self.setMinimumWidth(450)
        self.generated = ""
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 23, 24, 22)
        root.setSpacing(14)
        root.addWidget(lbl("Password generator", "sectionTitle"))
        root.addWidget(lbl("Random passwords are created locally using the operating system's secure random source.", "muted", word_wrap=True))
        length_row = QHBoxLayout()
        length_row.addWidget(lbl("Length"))
        self.length_value = lbl("24")
        self.length_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        length_row.addWidget(self.length_value)
        root.addLayout(length_row)
        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setRange(12, 64)
        self.length_slider.setValue(24)
        self.length_slider.valueChanged.connect(lambda x: (self.length_value.setText(str(x)), self.regenerate()))
        root.addWidget(self.length_slider)
        opts = QGridLayout()
        self.upper = QCheckBox("Uppercase A–Z")
        self.lower = QCheckBox("Lowercase a–z")
        self.numbers = QCheckBox("Numbers 2–9")
        self.symbols = QCheckBox("Symbols")
        for box in [self.upper, self.lower, self.numbers, self.symbols]:
            box.setChecked(True)
            box.stateChanged.connect(self.regenerate)
        opts.addWidget(self.upper, 0, 0)
        opts.addWidget(self.lower, 0, 1)
        opts.addWidget(self.numbers, 1, 0)
        opts.addWidget(self.symbols, 1, 1)
        root.addLayout(opts)
        self.display = SecretEdit(generator=False)
        root.addWidget(self.display)
        action_row = QHBoxLayout()
        new_btn = btn("↻  Regenerate")
        new_btn.clicked.connect(self.regenerate)
        action_row.addWidget(new_btn)
        action_row.addStretch()
        copy_button = btn("Copy")
        copy_button.clicked.connect(self.copy)
        action_row.addWidget(copy_button)
        root.addLayout(action_row)
        footer = QHBoxLayout()
        footer.addStretch()
        cancel = btn("Cancel", "quiet")
        cancel.clicked.connect(self.reject)
        footer.addWidget(cancel)
        use = btn("Use password", "primary")
        use.clicked.connect(self.accept_generated)
        footer.addWidget(use)
        root.addLayout(footer)
        self.regenerate()

    def regenerate(self, *_):
        try:
            self.generated = make_password(
                self.length_slider.value(), self.upper.isChecked(), self.lower.isChecked(),
                self.numbers.isChecked(), self.symbols.isChecked(),
            )
            self.display.setText(self.generated)
        except ValueError:
            self.generated = ""
            self.display.setText("Choose at least one character set")

    def copy(self):
        if self.generated:
            copy_with_timeout(self.display.text())

    def accept_generated(self):
        if self.generated:
            self.generated = self.display.text()
            self.accept()


def copy_with_timeout(value: str):
    """Clipboard remains OS-accessible until cleared; only clear if unchanged."""
    clip = QApplication.clipboard()
    clip.setText(value)

    def clear_if_unchanged():
        # Other applications can read copied secrets during this brief window.
        if clip.text() == value:
            clip.clear()

    QTimer.singleShot(30_000, clear_if_unchanged)


class CustomField(QWidget):
    def __init__(self, name="", value="", secret=False, parent=None):
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(7)
        self.key = QLineEdit(name)
        self.key.setPlaceholderText("Field name")
        self.key.setMaximumWidth(180)
        row.addWidget(self.key)
        self.value = SecretEdit() if secret else QLineEdit()
        self.value.setText(value)
        self.value.setPlaceholderText("Value")
        row.addWidget(self.value, 1)
        self.secret = QCheckBox("Secret")
        self.secret.setChecked(secret)
        row.addWidget(self.secret)
        self.secret.stateChanged.connect(self.change_mode)
        self.remove_button = QToolButton()
        self.remove_button.setText("✕")
        self.remove_button.setToolTip("Remove this field")
        row.addWidget(self.remove_button)
        self.removed = False
        self.remove_button.clicked.connect(self.mark_removed)

    def mark_removed(self):
        self.removed = True
        self.hide()

    def change_mode(self):
        desired = bool(self.secret.isChecked())
        actual = isinstance(self.value, SecretEdit)
        if desired == actual:
            return
        old_widget = self.value
        old_value = old_widget.text()
        self.value = SecretEdit() if desired else QLineEdit()
        self.value.setText(old_value)
        self.layout().replaceWidget(old_widget, self.value)
        old_widget.hide()
        old_widget.deleteLater()

    def record(self) -> dict[str, Any] | None:
        name = self.key.text().strip()
        if not name:
            return None
        return {"name": name, "value": self.value.text(), "secret": self.secret.isChecked()}


class EntryDialog(QDialog):
    def __init__(self, businesses: list[str], current: dict | None = None, initial_type="Login", parent=None):
        super().__init__(parent)
        self.current = current
        self.field_widgets: dict[str, QWidget] = {}
        self.extra_rows: list[CustomField] = []
        self.setWindowTitle("Edit entry" if current else "New entry")
        self.resize(640, 700)
        self.setMinimumWidth(540)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        body_scroll = QScrollArea()
        body_scroll.setWidgetResizable(True)
        body = QWidget()
        self.body_layout = QVBoxLayout(body)
        self.body_layout.setContentsMargins(30, 28, 30, 24)
        self.body_layout.setSpacing(13)
        self.body_layout.addWidget(lbl("Edit record" if current else "Add a record", "headline"))
        self.body_layout.addWidget(lbl("Everything you save here will be encrypted, including names and notes.", "muted", word_wrap=True))
        self.body_layout.addWidget(spacer(4))
        self.body_layout.addWidget(lbl("RECORD DETAILS", "eyebrow"))
        self.body_layout.addWidget(lbl("Category"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(list(TYPES))
        self.type_combo.setCurrentText(current.get("type", initial_type) if current else initial_type)
        self.type_combo.setEnabled(current is None)  # Changing categories should not silently drop fields.
        self.body_layout.addWidget(self.type_combo)
        self.body_layout.addWidget(lbl("Title *"))
        self.title_field = QLineEdit(safe_text(current.get("title", "")) if current else "")
        self.title_field.setPlaceholderText("e.g. Stripe dashboard, Company registration")
        self.body_layout.addWidget(self.title_field)
        self.body_layout.addWidget(lbl("Business / workspace"))
        self.business_combo = QComboBox()
        self.business_combo.setEditable(True)
        self.business_combo.addItems([""] + businesses)
        self.business_combo.setCurrentText(safe_text(current.get("business", "")) if current else "")
        self.business_combo.lineEdit().setPlaceholderText("Personal or enter business name")
        self.body_layout.addWidget(self.business_combo)
        self.body_layout.addWidget(lbl("Tags (separate with commas)"))
        self.tags_field = QLineEdit(", ".join(current.get("tags", [])) if current else "")
        self.tags_field.setPlaceholderText("client, marketing, important")
        self.body_layout.addWidget(self.tags_field)
        self.favorite_field = QCheckBox("★  Pin to favorites")
        self.favorite_field.setChecked(bool(current.get("favorite", False)) if current else False)
        self.body_layout.addWidget(self.favorite_field)
        self.body_layout.addWidget(spacer(5))
        self.body_layout.addWidget(lbl("ACCOUNT / BUSINESS FIELDS", "eyebrow"))
        self.fields_container = QWidget()
        self.fields_layout = QVBoxLayout(self.fields_container)
        self.fields_layout.setContentsMargins(0, 0, 0, 0)
        self.fields_layout.setSpacing(10)
        self.body_layout.addWidget(self.fields_container)
        self.type_combo.currentTextChanged.connect(self.rebuild_fields)
        self.rebuild_fields(self.type_combo.currentText())
        self.body_layout.addWidget(spacer(5))
        self.body_layout.addWidget(lbl("CUSTOM FIELDS", "eyebrow"))
        self.extra_container = QWidget()
        self.extra_layout = QVBoxLayout(self.extra_container)
        self.extra_layout.setSpacing(9)
        self.extra_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.addWidget(self.extra_container)
        for item in (current.get("custom_fields", []) if current else []):
            if isinstance(item, dict):
                self.add_custom(safe_text(item.get("name")), safe_text(item.get("value")), bool(item.get("secret")))
        add = btn("+  Add custom field", "quiet")
        add.clicked.connect(lambda: self.add_custom())
        self.body_layout.addWidget(add)
        self.body_layout.addWidget(spacer(6))
        self.body_layout.addWidget(lbl("SECURE NOTES", "eyebrow"))
        self.notes_field = QPlainTextEdit(safe_text(current.get("notes", "")) if current else "")
        self.notes_field.setPlaceholderText("Instructions, recovery details, contacts, or any other confidential information…")
        self.notes_field.setMinimumHeight(105)
        self.body_layout.addWidget(self.notes_field)
        self.body_layout.addStretch()
        body_scroll.setWidget(body)
        root.addWidget(body_scroll)
        buttons = QHBoxLayout()
        buttons.setContentsMargins(30, 12, 30, 18)
        buttons.addStretch()
        cancel = btn("Cancel", "quiet")
        cancel.clicked.connect(self.reject)
        buttons.addWidget(cancel)
        save = btn("Save encrypted record", "primary")
        save.clicked.connect(self.validate_and_accept)
        save.setDefault(True)
        buttons.addWidget(save)
        root.addLayout(buttons)

    def rebuild_fields(self, type_name: str):
        while self.fields_layout.count():
            item = self.fields_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.field_widgets.clear()
        previous = self.current.get("fields", {}) if self.current else {}
        for key, human_name, secret in TYPES[type_name]["fields"]:
            wrapper = QWidget()
            form = QVBoxLayout(wrapper)
            form.setSpacing(5)
            form.setContentsMargins(0, 0, 0, 0)
            form.addWidget(lbl(human_name))
            field = SecretEdit(generator=(key == "password")) if secret else QLineEdit()
            field.setPlaceholderText(human_name)
            field.setText(safe_text(previous.get(key, "")))
            form.addWidget(field)
            self.field_widgets[key] = field
            self.fields_layout.addWidget(wrapper)
        if not self.field_widgets:
            self.fields_layout.addWidget(lbl("This category has no predefined fields. Use notes or custom fields below.", "muted", word_wrap=True))

    def add_custom(self, name="", value="", secret=False):
        widget = CustomField(name, value, secret)
        self.extra_rows.append(widget)
        self.extra_layout.addWidget(widget)

    def validate_and_accept(self):
        if not self.title_field.text().strip():
            QMessageBox.warning(self, "A title is required", "Give the entry a descriptive title.")
            self.title_field.setFocus()
            return
        self.accept()

    def record(self) -> dict[str, Any]:
        timestamp = utc_now()
        old = self.current or {}
        tags = list(dict.fromkeys(x.strip() for x in self.tags_field.text().split(",") if x.strip()))
        return {
            "id": old.get("id", str(uuid.uuid4())),
            "type": self.type_combo.currentText(),
            "title": self.title_field.text().strip(),
            "business": self.business_combo.currentText().strip(),
            "tags": tags,
            "favorite": self.favorite_field.isChecked(),
            "fields": {key: widget.text() for key, widget in self.field_widgets.items()},
            "custom_fields": [row.record() for row in self.extra_rows if not row.removed and row.record()],
            "notes": self.notes_field.toPlainText(),
            "created": old.get("created", timestamp),
            "updated": timestamp,
        }


class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change master password")
        self.setMinimumWidth(485)
        root = QVBoxLayout(self)
        root.setContentsMargins(25, 25, 25, 20)
        root.setSpacing(11)
        root.addWidget(lbl("Change master password", "sectionTitle"))
        root.addWidget(lbl("This re-encrypts the vault with a new random salt. All automatic backup ciphertext is updated too.", "muted", word_wrap=True))
        self.old = SecretEdit("Current master password")
        self.new = SecretEdit("New master password (12+ characters)")
        self.confirm = SecretEdit("Confirm new master password")
        for label, editor in [
            ("Current master password", self.old),
            ("New master password", self.new),
            ("Repeat new master password", self.confirm),
        ]:
            root.addWidget(lbl(label))
            root.addWidget(editor)
        root.addWidget(lbl("If you forget your new password, it cannot be reset.", "muted"))
        actions = QHBoxLayout()
        actions.addStretch()
        cancel = btn("Cancel", "quiet")
        cancel.clicked.connect(self.reject)
        actions.addWidget(cancel)
        submit = btn("Change password", "primary")
        submit.clicked.connect(self.verify)
        actions.addWidget(submit)
        root.addLayout(actions)

    def verify(self):
        if len(self.new.text()) < 12:
            QMessageBox.warning(self, "Too short", "Use at least 12 characters for the new password.")
        elif self.new.text() != self.confirm.text():
            QMessageBox.warning(self, "Passwords do not match", "Confirm the new master password exactly.")
        elif self.new.text() == self.old.text():
            QMessageBox.warning(self, "Unchanged password", "Choose a different master password.")
        else:
            self.accept()


class SettingsDialog(QDialog):
    def __init__(self, main: 'VaultWindow'):
        super().__init__(main)
        self.main = main
        self.setWindowTitle("Vault settings")
        self.setMinimumWidth(530)
        root = QVBoxLayout(self)
        root.setContentsMargins(26, 24, 26, 22)
        root.setSpacing(13)
        root.addWidget(lbl("Vault settings", "sectionTitle"))
        root.addWidget(lbl("SECURITY", "eyebrow"))
        root.addWidget(lbl("Lock automatically after inactivity"))
        self.timeout = QComboBox()
        for val in [1, 2, 5, 10, 15, 30]:
            self.timeout.addItem(f"{val} minute{'s' if val != 1 else ''}", val)
        current = int(main.vault.data.get("settings", {}).get("auto_lock_minutes", 5))
        index = self.timeout.findData(current)
        self.timeout.setCurrentIndex(index if index >= 0 else 2)
        root.addWidget(self.timeout)
        self.timeout.currentIndexChanged.connect(self.change_timeout)
        change = btn("Change master password")
        change.clicked.connect(self.change_password)
        root.addWidget(change)
        root.addWidget(spacer(8))
        root.addWidget(lbl("ENCRYPTED BACKUPS", "eyebrow"))
        root.addWidget(lbl("Backups contain only encrypted vault data. Save a copy to a USB drive or another safe location.", "muted", word_wrap=True))
        backups = QHBoxLayout()
        export = btn("Save encrypted backup")
        export.clicked.connect(self.export_backup)
        backups.addWidget(export)
        restore = btn("Restore backup", "danger")
        restore.clicked.connect(self.restore)
        backups.addWidget(restore)
        root.addLayout(backups)
        root.addWidget(spacer(5))
        root.addWidget(lbl("VAULT FILE", "eyebrow"))
        path_label = lbl(str(main.vault.path), "muted", word_wrap=True)
        path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        root.addWidget(path_label)
        open_folder = btn("Open encrypted vault folder")
        open_folder.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(main.vault.path.parent))))
        root.addWidget(open_folder)
        root.addWidget(lbl("VaultDesk does not sync data, transmit secrets, or have password recovery. Keep a separate encrypted backup.", "muted", word_wrap=True))
        actions = QHBoxLayout()
        actions.addStretch()
        close = btn("Close", "primary")
        close.clicked.connect(self.accept)
        actions.addWidget(close)
        root.addLayout(actions)

    def change_timeout(self):
        val = self.timeout.currentData()
        if self.main.vault and isinstance(val, int):
            def update():
                self.main.vault.data.setdefault("settings", {})["auto_lock_minutes"] = val
            self.main.apply_and_save(update)

    def change_password(self):
        dlg = ChangePasswordDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.main.vault.change_master_password(dlg.old.text(), dlg.new.text())
            QMessageBox.information(self, "Password changed", "Your vault and automatic recovery file are now protected by the new master password. Update your backup copies.")
        except VaultError as error:
            QMessageBox.warning(self, "Could not change password", str(error))
        except OSError:
            QMessageBox.critical(self, "Unable to save", "A disk error prevented changing the master password.")

    def export_backup(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save encrypted vault backup", "VaultDesk-backup.vdesk", "Encrypted Vault (*.vdesk);;All files (*)"
        )
        if not path:
            return
        try:
            self.main.vault.backup_to(Path(path))
            QMessageBox.information(self, "Backup saved", "Encrypted backup created. You will need the matching master password to reopen it.")
        except (OSError, VaultError) as error:
            QMessageBox.warning(self, "Backup failed", str(error))

    def restore(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose an encrypted backup", "", "Vault files (*.vdesk *.bak);;All files (*)")
        if not path:
            return
        if Path(path).resolve() == self.main.vault.path.resolve():
            QMessageBox.warning(self, "Same vault", "This is already the active vault.")
            return
        password, ok = prompt_secret(self, "Backup master password", "Enter the password used to encrypt that backup:")
        if not ok:
            return
        try:
            recovered = Vault.open(Path(path), password)
        except (VaultError, OSError) as error:
            QMessageBox.warning(self, "Backup could not be opened", str(error))
            return
        result = QMessageBox.question(
            self, "Replace current vault records?",
            "This replaces ALL current records with those from the backup. A recovery copy of the current vault will be saved automatically. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if result != QMessageBox.StandardButton.Yes:
            return
        snapshot = copy.deepcopy(self.main.vault.data)
        try:
            self.main.vault.data = copy.deepcopy(recovered.data)
            self.main.vault.save()
        except (VaultError, OSError) as error:
            self.main.vault.data = snapshot
            QMessageBox.critical(self, "Restore failed", str(error))
            return
        self.main.refresh()
        QMessageBox.information(self, "Restored", "The backup's records are restored and protected by your current master password.")
        self.accept()


def prompt_secret(parent: QWidget, title: str, message: str) -> tuple[str, bool]:
    dlg = QDialog(parent)
    dlg.setWindowTitle(title)
    dlg.setMinimumWidth(410)
    root = QVBoxLayout(dlg)
    root.setContentsMargins(22, 21, 22, 20)
    root.setSpacing(13)
    root.addWidget(lbl(message, word_wrap=True))
    inp = SecretEdit()
    root.addWidget(inp)
    actions = QHBoxLayout()
    actions.addStretch()
    cancel = btn("Cancel", "quiet")
    cancel.clicked.connect(dlg.reject)
    actions.addWidget(cancel)
    ok = btn("Unlock", "primary")
    ok.clicked.connect(dlg.accept)
    actions.addWidget(ok)
    root.addLayout(actions)
    inp.field.setFocus()
    result = dlg.exec() == QDialog.DialogCode.Accepted
    return inp.text(), result


def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        elif item.layout() is not None:
            clear_layout(item.layout())


class VaultWindow(QMainWindow):
    def __init__(self, path: Path | None = None):
        super().__init__()
        self.path = path or default_vault_path()
        self.vault: Vault | None = None
        self.scope = ("all", "")
        self.selected_id: str | None = None
        self.last_activity = time.monotonic()
        self.active_dialog: QDialog | None = None
        self.setWindowTitle("VaultDesk  •  Private business vault")
        self.resize(1240, 800)
        self.setMinimumSize(925, 610)
        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)
        self.auto_timer = QTimer(self)
        self.auto_timer.timeout.connect(self.check_inactivity)
        self.auto_timer.start(1000)
        QApplication.instance().installEventFilter(self)
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self.new_entry)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self.lock)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=self.focus_search)
        if self.path.exists():
            self.show_unlock()
        else:
            self.show_setup()

    def eventFilter(self, obj, event):
        if event.type() in (
            QEvent.Type.KeyPress, QEvent.Type.MouseButtonPress, QEvent.Type.Wheel,
            QEvent.Type.TouchBegin,
        ):
            self.last_activity = time.monotonic()
        return super().eventFilter(obj, event)

    def check_inactivity(self):
        if not self.vault:
            return
        try:
            timeout_minutes = int(self.vault.data.get("settings", {}).get("auto_lock_minutes", 5))
        except (ValueError, TypeError):
            timeout_minutes = 5
        timeout_minutes = max(1, min(30, timeout_minutes))
        if time.monotonic() - self.last_activity >= timeout_minutes * 60:
            self.lock()

    def set_page(self, page: QWidget):
        while self.pages.count():
            old = self.pages.widget(0)
            self.pages.removeWidget(old)
            old.hide()
            old.deleteLater()
        self.pages.addWidget(page)
        self.pages.setCurrentWidget(page)

    def auth_page(self, symbol: str, title: str, description: str):
        page = QWidget()
        vertical = QVBoxLayout(page)
        vertical.setContentsMargins(28, 30, 28, 30)
        vertical.addStretch()
        card = QFrame()
        card.setObjectName("card")
        card.setMaximumWidth(490)
        body = QVBoxLayout(card)
        body.setContentsMargins(35, 29, 35, 31)
        body.setSpacing(12)
        brand = QHBoxLayout()
        mark = QLabel("◆")
        mark.setStyleSheet("color:#A093FF;font-size:29px;font-weight:900")
        brand.addWidget(mark)
        brand.addWidget(lbl("VaultDesk", "brand"))
        brand.addStretch()
        body.addLayout(brand)
        body.addWidget(spacer(8))
        pill = lbl(symbol, "muted")
        body.addWidget(pill)
        body.addWidget(lbl(title, "headline"))
        body.addWidget(lbl(description, "muted", word_wrap=True))
        body.addWidget(spacer(12))
        vertical.addWidget(card, alignment=Qt.AlignmentFlag.AlignHCenter)
        vertical.addStretch()
        bottom = lbl("OFFLINE ONLY    •    ARGON2ID + AES-256-GCM    •    NO CLOUD ACCOUNT", "eyebrow")
        bottom.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        vertical.addWidget(bottom)
        return page, body

    def show_setup(self):
        page, area = self.auth_page(
            "●  FIRST-TIME SETUP",
            "Create your private vault",
            "Choose a master password. It becomes the basis for the encryption key that protects every saved record.",
        )
        area.addWidget(lbl("Master password"))
        self.setup_password = SecretEdit("At least 12 characters")
        area.addWidget(self.setup_password)
        area.addWidget(lbl("Confirm master password"))
        self.setup_confirm = SecretEdit("Repeat master password")
        area.addWidget(self.setup_confirm)
        area.addWidget(lbl("Use a long, unique passphrase. Your master password cannot be recovered if forgotten.", "muted", word_wrap=True))
        area.addWidget(spacer(2))
        create = btn("Create encrypted vault  →", "primary")
        create.setMinimumHeight(47)
        create.clicked.connect(self.create_vault)
        area.addWidget(create)
        self.setup_confirm.field.returnPressed.connect(self.create_vault)
        self.set_page(page)
        self.setup_password.field.setFocus()

    def create_vault(self):
        password = self.setup_password.text()
        if len(password) < 12:
            QMessageBox.warning(self, "Choose a longer password", "Your master password must have at least 12 characters. A long passphrase is recommended.")
            return
        if password != self.setup_confirm.text():
            QMessageBox.warning(self, "Passwords don't match", "Repeat the master password exactly.")
            return
        try:
            self.vault = Vault.create(self.path, password)
        except (OSError, VaultError) as e:
            QMessageBox.critical(self, "Could not create vault", str(e))
            return
        self.setup_password.setText("")
        self.setup_confirm.setText("")
        self.scope = ("all", "")
        self.selected_id = None
        self.last_activity = time.monotonic()
        self.show_workspace()

    def show_unlock(self):
        page, area = self.auth_page(
            "●  ENCRYPTED & LOCKED",
            "Welcome back",
            "Enter your master password to unlock your private records. Nothing is stored unencrypted on disk.",
        )
        area.addWidget(lbl("Master password"))
        self.login_password = SecretEdit("Enter your master password")
        area.addWidget(self.login_password)
        area.addWidget(spacer(6))
        unlock = btn("Unlock vault  →", "primary")
        unlock.setMinimumHeight(47)
        unlock.clicked.connect(self.unlock)
        area.addWidget(unlock)
        self.login_password.field.returnPressed.connect(self.unlock)
        area.addWidget(lbl("No account recovery or password reset. If you have an encrypted backup, it requires the password used when that backup was created.", "muted", word_wrap=True))
        self.set_page(page)
        self.login_password.field.setFocus()

    def unlock(self):
        password = self.login_password.text()
        try:
            self.vault = Vault.open(self.path, password)
        except (VaultError, OSError) as error:
            self.login_password.setText("")
            QMessageBox.warning(self, "Unable to unlock", str(error))
            return
        self.login_password.setText("")
        self.scope = ("all", "")
        self.selected_id = None
        self.last_activity = time.monotonic()
        self.show_workspace()

    def lock(self):
        if not self.vault:
            return
        modal = QApplication.activeModalWidget()
        if modal is not None and modal != self:
            # Dismiss editors/settings so secrets cannot remain in an open dialog.
            if isinstance(modal, QDialog):
                modal.reject()
            if QApplication.activeModalWidget() is not None:
                return
        self.vault.forget_key()
        self.vault = None
        self.selected_id = None
        self.show_unlock()

    def closeEvent(self, event):
        if self.vault:
            self.vault.forget_key()
            self.vault = None
        super().closeEvent(event)

    def show_workspace(self):
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setSpacing(0)
        outer.setContentsMargins(0, 0, 0, 0)
        top = QFrame()
        top.setObjectName("topbar")
        top.setFixedHeight(72)
        head = QHBoxLayout(top)
        head.setContentsMargins(23, 0, 23, 0)
        head.setSpacing(13)
        mark = lbl("◆")
        mark.setStyleSheet("color:#9A8EFF;font-size:25px;font-weight:800")
        head.addWidget(mark)
        head.addWidget(lbl("VaultDesk", "brand"))
        head.addWidget(lbl("/  PRIVATE WORKSPACE", "eyebrow"))
        head.addStretch()
        status = lbl("●  ENCRYPTED LOCALLY", "eyebrow")
        status.setStyleSheet("color:#65D9C4;font-weight:750;font-size:11px")
        head.addWidget(status)
        new = btn("+  New record", "primary")
        new.clicked.connect(self.new_entry)
        head.addWidget(new)
        lock = btn("⌁  Lock", "quiet")
        lock.clicked.connect(self.lock)
        head.addWidget(lock)
        outer.addWidget(top)
        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)
        sidebar = QFrame()
        sidebar.setObjectName("side")
        sidebar.setFixedWidth(226)
        self.sidebar_layout = QVBoxLayout(sidebar)
        self.sidebar_layout.setContentsMargins(13, 20, 13, 18)
        self.sidebar_layout.setSpacing(4)
        content.addWidget(sidebar)
        list_panel = QFrame()
        list_panel.setObjectName("listPanel")
        list_panel.setFixedWidth(360)
        middle = QVBoxLayout(list_panel)
        middle.setContentsMargins(17, 20, 17, 10)
        middle.setSpacing(9)
        self.current_title = lbl("All records", "sectionTitle")
        middle.addWidget(self.current_title)
        self.list_count = lbl("0 entries", "muted")
        middle.addWidget(self.list_count)
        middle.addWidget(spacer(3))
        self.search = QLineEdit()
        self.search.setPlaceholderText("⌕  Search titles, accounts, tags…")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.refresh_list)
        middle.addWidget(self.search)
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("Sort: Recently updated", "recent")
        self.sort_combo.addItem("Sort: A to Z", "name")
        self.sort_combo.addItem("Sort: Category", "type")
        self.sort_combo.addItem("Sort: Oldest", "oldest")
        self.sort_combo.currentIndexChanged.connect(self.refresh_list)
        middle.addWidget(self.sort_combo)
        self.records_list = QListWidget()
        self.records_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.records_list.setSpacing(3)
        self.records_list.currentItemChanged.connect(self.change_selection)
        middle.addWidget(self.records_list, 1)
        footer = lbl("Tip: Ctrl+N new  ·  Ctrl+F search  ·  Ctrl+L lock", "muted")
        footer.setStyleSheet("color:#667791;font-size:10px")
        middle.addWidget(footer)
        content.addWidget(list_panel)
        detail_panel = QFrame()
        detail_panel.setObjectName("detailPanel")
        detail_layout = QVBoxLayout(detail_panel)
        detail_layout.setSpacing(0)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        self.details_scroll = QScrollArea()
        self.details_scroll.setWidgetResizable(True)
        detail_layout.addWidget(self.details_scroll)
        content.addWidget(detail_panel, 1)
        outer.addLayout(content, 1)
        self.set_page(page)
        self.refresh()

    def entries(self) -> list[dict[str, Any]]:
        if not self.vault:
            return []
        return [x for x in self.vault.data.get("entries", []) if isinstance(x, dict)]

    def businesses(self) -> list[str]:
        return sorted({safe_text(entry.get("business")).strip() for entry in self.entries() if safe_text(entry.get("business")).strip()}, key=str.casefold)

    def count_type(self, key: str) -> int:
        return sum(1 for x in self.entries() if x.get("type") == key)

    def nav(self, text: str, scope: tuple[str, str], total: int | None = None):
        shown = f"{text}" if total is None else f"{text}    ({total})"
        selected = self.scope == scope
        b = btn(shown, "navActive" if selected else "nav")
        b.setToolTip(text)
        b.clicked.connect(lambda: self.change_scope(scope))
        self.sidebar_layout.addWidget(b)

    def build_sidebar(self):
        clear_layout(self.sidebar_layout)
        self.sidebar_layout.addWidget(lbl("LIBRARY", "eyebrow"))
        self.sidebar_layout.addWidget(spacer(3))
        self.nav("▦    All records", ("all", ""), len(self.entries()))
        self.nav("★    Favorites", ("favorites", ""), sum(bool(e.get("favorite")) for e in self.entries()))
        self.sidebar_layout.addWidget(spacer(15))
        self.sidebar_layout.addWidget(lbl("CATEGORIES", "eyebrow"))
        self.sidebar_layout.addWidget(spacer(2))
        for type_name, meta in TYPES.items():
            self.nav(f"{meta['symbol']}    {type_name}", ("type", type_name), self.count_type(type_name))
        self.sidebar_layout.addWidget(spacer(16))
        self.sidebar_layout.addWidget(lbl("BUSINESSES", "eyebrow"))
        business_names = self.businesses()
        if not business_names:
            note = lbl("Businesses appear here when you assign them to records.", "muted", word_wrap=True)
            note.setStyleSheet("color:#697A95;font-size:11px;padding:8px 5px")
            self.sidebar_layout.addWidget(note)
        else:
            for name in business_names[:20]:
                display_name = name if len(name) <= 19 else name[:17] + "…"
                total = sum(x.get("business") == name for x in self.entries())
                self.nav(f"▸    {display_name}", ("business", name), total)
            if len(business_names) > 20:
                self.sidebar_layout.addWidget(lbl("Use search for additional businesses", "muted", word_wrap=True))
        self.sidebar_layout.addStretch()
        settings = btn("⚙    Settings & backups", "nav")
        settings.clicked.connect(self.open_settings)
        self.sidebar_layout.addWidget(settings)

    def change_scope(self, scope: tuple[str, str]):
        self.scope = scope
        self.selected_id = None
        self.refresh()

    def scope_title(self) -> str:
        kind, detail = self.scope
        if kind == "favorites":
            return "Favorites"
        if kind == "type":
            return detail
        if kind == "business":
            return detail
        return "All records"

    def filtered_entries(self):
        kind, value = self.scope
        result = []
        query = self.search.text().casefold().strip()
        for item in self.entries():
            if kind == "favorites" and not item.get("favorite"):
                continue
            if kind == "type" and item.get("type") != value:
                continue
            if kind == "business" and item.get("business") != value:
                continue
            if query:
                fields = item.get("fields", {})
                field_search = []
                if isinstance(fields, dict):
                    for field_name in ("username", "website", "service", "institution", "product", "legal_name", "contact", "endpoint"):
                        field_search.append(safe_text(fields.get(field_name)))
                haystack = " ".join([
                    safe_text(item.get("title")), safe_text(item.get("business")),
                    safe_text(item.get("type")), safe_text(item.get("notes")),
                    " ".join(x for x in item.get("tags", []) if isinstance(x, str)),
                    *field_search,
                ]).casefold()
                if query not in haystack:
                    continue
            result.append(item)
        sorting = self.sort_combo.currentData()
        if sorting == "name":
            result.sort(key=lambda x: safe_text(x.get("title")).casefold())
        elif sorting == "type":
            result.sort(key=lambda x: (safe_text(x.get("type")), safe_text(x.get("title")).casefold()))
        elif sorting == "oldest":
            result.sort(key=lambda x: safe_text(x.get("created")))
        else:
            result.sort(key=lambda x: safe_text(x.get("updated")), reverse=True)
        return result

    def refresh(self):
        if not self.vault:
            return
        self.build_sidebar()
        self.refresh_list()

    def refresh_list(self, *_):
        if not self.vault or not hasattr(self, "records_list"):
            return
        records = self.filtered_entries()
        self.current_title.setText(self.scope_title())
        self.list_count.setText(f"{len(records)} record{'s' if len(records) != 1 else ''}")
        self.records_list.blockSignals(True)
        self.records_list.clear()
        target_row = -1
        for i, item in enumerate(records):
            meta = TYPES.get(item.get("type"), TYPES["Secure Note"])
            row = QListWidgetItem()
            row.setData(Qt.ItemDataRole.UserRole, item.get("id"))
            row.setSizeHint(QSize(315, 73))
            wrapper = QFrame()
            wrapper.setObjectName("itemCardActive" if item.get("id") == self.selected_id else "itemCard")
            line = QHBoxLayout(wrapper)
            line.setContentsMargins(10, 7, 10, 7)
            line.setSpacing(9)
            emblem = QLabel(meta["symbol"])
            emblem.setFixedSize(35, 38)
            emblem.setAlignment(Qt.AlignmentFlag.AlignCenter)
            emblem.setStyleSheet(f"color:{meta['color']};font-size:22px;font-weight:bold;background:#29364B;border-radius:9px")
            line.addWidget(emblem)
            right = QVBoxLayout()
            right.setSpacing(3)
            title_row = QHBoxLayout()
            title = lbl(safe_text(item.get("title")) or "Untitled")
            title.setStyleSheet("color:#F4F6FF;font-weight:700;font-size:12px")
            title.setToolTip(safe_text(item.get("title")))
            title_row.addWidget(title, 1)
            if item.get("favorite"):
                star = lbl("★")
                star.setStyleSheet("color:#FFC778;font-size:14px")
                title_row.addWidget(star)
            right.addLayout(title_row)
            subtext = safe_text(item.get("business")) or safe_text(item.get("type"))
            subtitle = lbl(subtext if len(subtext) < 33 else subtext[:31] + "…", "muted")
            subtitle.setStyleSheet("color:#8CA0BA;font-size:11px")
            right.addWidget(subtitle)
            line.addLayout(right, 1)
            self.records_list.addItem(row)
            self.records_list.setItemWidget(row, wrapper)
            if item.get("id") == self.selected_id:
                target_row = i
        if target_row >= 0:
            self.records_list.setCurrentRow(target_row)
        elif self.selected_id is not None:
            self.selected_id = None
        self.records_list.blockSignals(False)
        self.update_details()

    def change_selection(self, current: QListWidgetItem | None, previous=None):
        self.selected_id = current.data(Qt.ItemDataRole.UserRole) if current else None
        self.refresh_list_selection()
        self.update_details()

    def refresh_list_selection(self):
        for i in range(self.records_list.count()):
            item = self.records_list.item(i)
            widget = self.records_list.itemWidget(item)
            if widget:
                widget.setObjectName("itemCardActive" if item.data(Qt.ItemDataRole.UserRole) == self.selected_id else "itemCard")
                widget.style().unpolish(widget)
                widget.style().polish(widget)
                widget.update()

    def selected_entry(self):
        for entry in self.entries():
            if entry.get("id") == self.selected_id:
                return entry
        return None

    def details_body(self):
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(32, 30, 32, 28)
        layout.setSpacing(15)
        return root, layout

    def update_details(self):
        if not self.vault or not hasattr(self, "details_scroll"):
            return
        record = self.selected_entry()
        if not record:
            self.show_overview()
        else:
            self.show_record(record)

    def show_overview(self):
        view, root = self.details_body()
        root.addWidget(spacer(38))
        brand = lbl("◆")
        brand.setStyleSheet("font-size:44px;color:#8D81FA")
        brand.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        root.addWidget(brand)
        title = lbl("Your private command center", "headline")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        root.addWidget(title)
        message = lbl("Organize accounts, credentials, API keys, business details and secure notes in one encrypted place.", "muted", word_wrap=True)
        message.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        root.addWidget(message)
        root.addWidget(spacer(16))
        stats = QHBoxLayout()
        for number, name in [
            (len(self.entries()), "Total records"),
            (len(self.businesses()), "Businesses"),
            (sum(e.get("favorite", False) for e in self.entries()), "Favorites"),
        ]:
            card = QFrame()
            card.setObjectName("statCard")
            contents = QVBoxLayout(card)
            contents.setContentsMargins(16, 16, 16, 14)
            contents.setSpacing(4)
            contents.addWidget(lbl(str(number), "largeNumber"))
            contents.addWidget(lbl(name, "muted"))
            stats.addWidget(card)
        root.addLayout(stats)
        root.addWidget(spacer(13))
        start = btn("+  Add your first record" if not self.entries() else "+  Add another record", "primary")
        start.setMaximumWidth(240)
        start.clicked.connect(self.new_entry)
        root.addWidget(start, alignment=Qt.AlignmentFlag.AlignHCenter)
        root.addWidget(spacer(8))
        tips = QFrame()
        tips.setObjectName("card")
        t = QVBoxLayout(tips)
        t.setContentsMargins(21, 19, 21, 19)
        t.setSpacing(9)
        t.addWidget(lbl("GETTING STARTED", "eyebrow"))
        t.addWidget(lbl("01    Create a record and choose its category."))
        t.addWidget(lbl("02    Assign a business name to group related records."))
        t.addWidget(lbl("03    Save an encrypted backup in Settings."))
        root.addWidget(tips)
        root.addStretch(1)
        self.details_scroll.setWidget(view)

    def detail_field(self, layout: QVBoxLayout, title: str, value: str, secret: bool):
        if not value:
            return
        box = QFrame()
        box.setObjectName("card")
        outside = QVBoxLayout(box)
        outside.setSpacing(8)
        outside.setContentsMargins(14, 10, 14, 12)
        outside.addWidget(lbl(title.upper(), "eyebrow"))
        line = QHBoxLayout()
        if secret:
            entry = QLineEdit(value)
            entry.setEchoMode(QLineEdit.EchoMode.Password)
            entry.setReadOnly(True)
            entry.setMinimumWidth(80)
            line.addWidget(entry, 1)
            reveal = btn("Show", "quiet")
            def change_reveal():
                hidden = entry.echoMode() == QLineEdit.EchoMode.Password
                entry.setEchoMode(QLineEdit.EchoMode.Normal if hidden else QLineEdit.EchoMode.Password)
                reveal.setText("Hide" if hidden else "Show")
            reveal.clicked.connect(change_reveal)
            line.addWidget(reveal)
        else:
            description = lbl(value, "detailValue", word_wrap=True)
            description.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            line.addWidget(description, 1)
        copy_button = btn("Copy", "quiet")
        copy_button.clicked.connect(lambda: copy_with_timeout(value))
        line.addWidget(copy_button)
        outside.addLayout(line)
        layout.addWidget(box)

    def show_record(self, record: dict[str, Any]):
        view, root = self.details_body()
        meta = TYPES.get(record.get("type"), TYPES["Secure Note"])
        header = QHBoxLayout()
        symbol = QLabel(meta["symbol"])
        symbol.setAlignment(Qt.AlignmentFlag.AlignCenter)
        symbol.setFixedSize(56, 56)
        symbol.setStyleSheet(f"color:{meta['color']};background:#1E2C43;border:1px solid #33445F;border-radius:13px;font-size:30px;font-weight:bold")
        header.addWidget(symbol)
        heading = QVBoxLayout()
        heading.setSpacing(3)
        title = lbl(safe_text(record.get("title")), "headline", word_wrap=True)
        title.setMaximumHeight(80)
        heading.addWidget(title)
        business = safe_text(record.get("business"))
        heading.addWidget(lbl(f"{record.get('type', 'Record')}  •  {business or 'Personal'}", "muted"))
        header.addLayout(heading, 1)
        root.addLayout(header)
        root.addWidget(spacer(2))
        action_bar = QHBoxLayout()
        edit = btn("✎  Edit record")
        edit.clicked.connect(self.edit_entry)
        action_bar.addWidget(edit)
        favorite = btn("★  Unfavorite" if record.get("favorite") else "☆  Favorite")
        favorite.clicked.connect(self.toggle_favorite)
        action_bar.addWidget(favorite)
        action_bar.addStretch()
        delete = btn("Delete", "danger")
        delete.clicked.connect(self.delete_entry)
        action_bar.addWidget(delete)
        root.addLayout(action_bar)
        tags = record.get("tags", [])
        if tags:
            tags_row = QHBoxLayout()
            for tag in tags[:7]:
                if not isinstance(tag, str):
                    continue
                badge = lbl("#" + tag)
                badge.setStyleSheet("color:#C2BFFF;background:#292B51;border:1px solid #424471;border-radius:8px;padding:5px 9px")
                tags_row.addWidget(badge)
            tags_row.addStretch()
            root.addLayout(tags_row)
        root.addWidget(spacer(6))
        fields = record.get("fields", {})
        field_specs = TYPES.get(record.get("type"), TYPES["Secure Note"])["fields"]
        if any(fields.get(key) for key, *_ in field_specs) or any(x.get("value") for x in record.get("custom_fields", []) if isinstance(x, dict)):
            root.addWidget(lbl("SAVED FIELDS", "eyebrow"))
            for key, caption, secret in field_specs:
                self.detail_field(root, caption, safe_text(fields.get(key)), secret)
            for extra in record.get("custom_fields", []):
                if isinstance(extra, dict):
                    self.detail_field(root, safe_text(extra.get("name")) or "Custom field", safe_text(extra.get("value")), bool(extra.get("secret")))
        notes = safe_text(record.get("notes"))
        if notes:
            root.addWidget(spacer(3))
            root.addWidget(lbl("SECURE NOTES", "eyebrow"))
            field = QPlainTextEdit()
            field.setReadOnly(True)
            field.setPlainText(notes)
            field.setMinimumHeight(118)
            field.setMaximumHeight(280)
            root.addWidget(field)
        if not fields and not notes:
            root.addWidget(lbl("No details yet. Choose Edit record to add information.", "muted", word_wrap=True))
        root.addWidget(spacer(4))
        created = safe_text(record.get("created"))[:10]
        updated = safe_text(record.get("updated"))[:10]
        root.addWidget(lbl(f"Created {created or 'unknown'}    •    Updated {updated or 'unknown'}", "muted"))
        root.addStretch(1)
        self.details_scroll.setWidget(view)

    def new_entry(self):
        if not self.vault:
            return
        initial_type = self.scope[1] if self.scope[0] == "type" else "Login"
        dlg = EntryDialog(self.businesses(), initial_type=initial_type, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted or not self.vault:
            return
        record = dlg.record()
        if self.apply_and_save(lambda: self.vault.data["entries"].append(record)):
            self.selected_id = record["id"]
            self.scope = ("all", "")
            self.refresh()

    def edit_entry(self):
        if not self.vault:
            return
        item = self.selected_entry()
        if not item:
            return
        dialog = EntryDialog(self.businesses(), current=item, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted or not self.vault:
            return
        changed = dialog.record()
        def update():
            for i, existing in enumerate(self.vault.data["entries"]):
                if existing.get("id") == item.get("id"):
                    self.vault.data["entries"][i] = changed
                    break
        if self.apply_and_save(update):
            self.refresh()

    def toggle_favorite(self):
        if not self.vault:
            return
        record = self.selected_entry()
        if record:
            def update():
                record["favorite"] = not bool(record.get("favorite"))
                record["updated"] = utc_now()
            if self.apply_and_save(update):
                self.refresh()

    def delete_entry(self):
        if not self.vault:
            return
        item = self.selected_entry()
        if not item:
            return
        question = QMessageBox.question(
            self, "Delete this encrypted entry?",
            f"Remove '{safe_text(item.get('title'))}' from the active vault? An older encrypted backup may still contain this record.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if question != QMessageBox.StandardButton.Yes:
            return
        old_id = item.get("id")
        if self.apply_and_save(lambda: self.vault.data.__setitem__(
            "entries", [x for x in self.entries() if x.get("id") != old_id]
        )):
            self.selected_id = None
            self.refresh()

    def apply_and_save(self, updater) -> bool:
        if not self.vault:
            return False
        snapshot = copy.deepcopy(self.vault.data)
        try:
            updater()
            self.vault.save()
            return True
        except (OSError, VaultError, ValueError, TypeError) as e:
            self.vault.data = snapshot
            QMessageBox.critical(self, "Could not save changes", f"Your last change was not saved. {e}")
            return False

    def focus_search(self):
        if self.vault and hasattr(self, "search"):
            self.search.setFocus()
            self.search.selectAll()

    def open_settings(self):
        if self.vault:
            dlg = SettingsDialog(self)
            dlg.exec()
            if self.vault:
                self.refresh()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("VaultDesk")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    location = default_vault_path()
    try:
        location.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        QMessageBox.critical(None, "VaultDesk cannot start", f"Could not access the encrypted vault directory: {error}")
        return 1
    # Prevent two app instances from overwriting one another's vault changes.
    instance_lock = QLockFile(str(location) + ".instance.lock")
    if not instance_lock.tryLock(200):
        QMessageBox.warning(None, "VaultDesk is already running", "Another VaultDesk window is using this encrypted vault. Close the other window first.")
        return 1
    window = VaultWindow(location)
    window.show()
    code = app.exec()
    instance_lock.unlock()
    return code


if __name__ == "__main__":
    sys.exit(main())
