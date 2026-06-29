from __future__ import annotations

import os


def _asset_url(filename: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "assets", filename)
    return path.replace("\\", "/")


APP_STYLESHEET = """
QMainWindow, QDialog {
    background: #f5f7fa;
    color: #172033;
}

QMenuBar {
    background: #ffffff;
    border-bottom: 1px solid #d8dee8;
    padding: 3px 8px;
}

QMenuBar::item {
    padding: 5px 10px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background: #e9eff8;
    color: #172033;
}

QMenu {
    background: #ffffff;
    border: 1px solid #ccd4e0;
    padding: 5px;
}

QMenu::item {
    padding: 6px 24px 6px 10px;
}

QMenu::item:selected {
    background: #e9eff8;
    color: #172033;
}

QWidget#appRoot {
    background: #f5f7fa;
}

QFrame#toolbar,
QFrame#filterBar,
QFrame#tableBand,
QFrame#statusBand {
    background: #ffffff;
    border: 1px solid #d8dee8;
    border-radius: 6px;
}

QLabel#fieldLabel,
QLabel#mutedText {
    color: #5b6575;
}

QPushButton {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 5px;
    padding: 7px 12px;
    min-height: 22px;
}

QPushButton:hover {
    background: #f0f4f8;
    border-color: #94a3b8;
}

QPushButton:pressed {
    background: #e3e9f2;
}

QPushButton:disabled {
    color: #94a3b8;
    background: #f3f5f8;
    border-color: #dbe1ea;
}

QPushButton#primaryButton {
    background: #176b87;
    border-color: #176b87;
    color: #ffffff;
    font-weight: 600;
}

QPushButton#primaryButton:hover {
    background: #135a72;
    border-color: #135a72;
}

QLineEdit,
QTextEdit,
QSpinBox {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 5px;
    padding: 6px 8px;
    min-height: 22px;
}

QComboBox,
QDateEdit {
    background: #fbfcfe;
    border: 1px solid #b9c4d2;
    border-radius: 5px;
    padding: 6px 36px 6px 8px;
    min-height: 22px;
}

QLineEdit:focus,
QComboBox:focus,
QDateEdit:focus,
QTextEdit:focus,
QSpinBox:focus {
    border: 1px solid #176b87;
}

QComboBox::drop-down,
QDateEdit::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 30px;
    background: #eef2f6;
    border-left: 1px solid #b9c4d2;
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
}

QComboBox::drop-down:hover,
QDateEdit::drop-down:hover {
    background: #e3e8ef;
}

QComboBox::down-arrow,
QDateEdit::down-arrow {
    image: url("__DROPDOWN_ARROW__");
    width: 10px;
    height: 6px;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background: #ffffff;
    color: #172033;
    border: 1px solid #ccd4e0;
    selection-background-color: #d7ecf3;
    selection-color: #172033;
    outline: 0;
}

QTableWidget#inventoryTable,
QTableWidget {
    background: #ffffff;
    alternate-background-color: #f4f4f5;
    border: none;
    gridline-color: #dce3ec;
    selection-background-color: #d7ecf3;
    selection-color: #111827;
}

QTableWidget::item:selected {
    background: #d7ecf3;
    color: #111827;
}

QHeaderView::section {
    background: #eef3f8;
    color: #263244;
    border: none;
    border-right: 1px solid #d8dee8;
    border-bottom: 1px solid #cbd5e1;
    padding: 8px 8px;
    font-weight: 600;
}

QTableWidget::item {
    padding: 5px 7px;
}

QGroupBox {
    border: 1px solid #d8dee8;
    border-radius: 6px;
    margin-top: 12px;
    padding: 12px 8px 8px 8px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}
""".replace("__DROPDOWN_ARROW__", _asset_url("dropdown-arrow.svg"))
