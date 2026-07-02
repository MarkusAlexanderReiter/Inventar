import copy

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from inventory_app.constants import DEFAULT_MASTER_DATA


class MasterDataDialog(QDialog):
    """Dialog zur Pflege der Stammdaten"""

    def __init__(self, parent=None, master_data=None):
        super(MasterDataDialog, self).__init__(parent)

        self.master_data = copy.deepcopy(master_data or DEFAULT_MASTER_DATA)
        self.list_widgets = {}
        self.list_labels = {}
        # Listen, die auch ohne Einträge gespeichert werden dürfen
        self.optional_lists = {"users"}

        self.setWindowTitle("Stammdaten verwalten")
        self.setMinimumWidth(650)
        self.setMinimumHeight(500)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self._add_list_tab("device_types", "Gerätetypen", self.master_data.get("device_types", []))
        self._add_list_tab("locations", "Standorte", self.master_data.get("locations", []))
        self._add_list_tab("offices", "Büros", self.master_data.get("offices", []))
        self._add_list_tab("users", "Benutzer", self.master_data.get("users", []))
        self._add_list_tab("conditions", "Zustände", self.master_data.get("conditions", []))
        self._add_list_tab("statuses", "Statuswerte", self.master_data.get("statuses", []))

        self.color_tab = RowColorTab(self.master_data.get("row_colors", []))
        self.tabs.addTab(self.color_tab, "Zeilenfarben")

        numbering_data = self.master_data.get("numbering", DEFAULT_MASTER_DATA["numbering"])
        self.numbering_tab = NumberingTab(numbering_data)
        self.tabs.addTab(self.numbering_tab, "Nummernkreis")

        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.handle_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _add_list_tab(self, key, label, items):
        widget = QWidget()
        tab_layout = QVBoxLayout(widget)

        list_widget = QListWidget()
        list_widget.addItems(items)
        tab_layout.addWidget(list_widget)

        button_layout = QHBoxLayout()
        add_btn = QPushButton("Hinzufügen")
        add_btn.clicked.connect(lambda: self._add_list_value(key))
        button_layout.addWidget(add_btn)

        edit_btn = QPushButton("Bearbeiten")
        edit_btn.clicked.connect(lambda: self._edit_list_value(key))
        button_layout.addWidget(edit_btn)

        remove_btn = QPushButton("Entfernen")
        remove_btn.clicked.connect(lambda: self._remove_list_value(key))
        button_layout.addWidget(remove_btn)

        button_layout.addStretch()
        tab_layout.addLayout(button_layout)

        self.list_widgets[key] = list_widget
        self.list_labels[key] = label
        self.tabs.addTab(widget, label)

    def _add_list_value(self, key):
        text, ok = QInputDialog.getText(self, "Eintrag hinzufügen", f"Neuer Eintrag für {self.list_labels[key]}:")
        if ok:
            value = text.strip()
            if value:
                self.list_widgets[key].addItem(value)

    def _edit_list_value(self, key):
        list_widget = self.list_widgets[key]
        current_item = list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Auswahl erforderlich", "Bitte wählen Sie einen Eintrag aus.")
            return

        text, ok = QInputDialog.getText(
            self,
            "Eintrag bearbeiten",
            f"Neuer Wert für {self.list_labels[key]}:",
            text=current_item.text(),
        )
        if ok:
            value = text.strip()
            if value:
                current_item.setText(value)

    def _remove_list_value(self, key):
        list_widget = self.list_widgets[key]
        row = list_widget.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Auswahl erforderlich", "Bitte wählen Sie einen Eintrag zum Entfernen aus.")
            return

        list_widget.takeItem(row)

    def handle_accept(self):
        for key, widget in self.list_widgets.items():
            values = [widget.item(i).text().strip() for i in range(widget.count()) if widget.item(i).text().strip()]
            if not values and key not in self.optional_lists:
                QMessageBox.warning(self, "Ungültige Eingabe", f"Die Liste '{self.list_labels[key]}' darf nicht leer sein.")
                return
            self.master_data[key] = values

        self.master_data["row_colors"] = self.color_tab.get_colors()
        self.master_data["numbering"] = self.numbering_tab.get_values()
        self.accept()

    def get_master_data(self):
        return copy.deepcopy(self.master_data)


class RowColorTab(QWidget):
    def __init__(self, colors=None):
        super(RowColorTab, self).__init__()
        self.colors = colors or []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Name", "Farbe"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        add_btn = QPushButton("Hinzufügen")
        add_btn.clicked.connect(self.add_color)
        button_layout.addWidget(add_btn)

        edit_btn = QPushButton("Bearbeiten")
        edit_btn.clicked.connect(self.edit_color)
        button_layout.addWidget(edit_btn)

        remove_btn = QPushButton("Entfernen")
        remove_btn.clicked.connect(self.remove_color)
        button_layout.addWidget(remove_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        for color_entry in self.colors:
            self._insert_color(color_entry)

    def _insert_color(self, color_entry, row=None):
        name = color_entry.get("name")
        color_value = color_entry.get("color", "#ffffff")
        if not name:
            return

        if row is None:
            for existing_row in range(self.table.rowCount()):
                existing_item = self.table.item(existing_row, 0)
                if existing_item and existing_item.text().lower() == name.lower():
                    row = existing_row
                    break

        if row is None:
            row = self.table.rowCount()
            self.table.insertRow(row)

        name_item = QTableWidgetItem(name)
        color_item = QTableWidgetItem(color_value.upper())
        preview_color = QColor(color_value)
        if preview_color.isValid():
            color_item.setBackground(preview_color)

        self.table.setItem(row, 0, name_item)
        self.table.setItem(row, 1, color_item)

    def add_color(self):
        dialog = ColorEditDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            entry = dialog.get_value()
            self._insert_color(entry)

    def edit_color(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Auswahl erforderlich", "Bitte wählen Sie eine Farbe aus.")
            return

        current_entry = {
            "name": self.table.item(row, 0).text(),
            "color": self.table.item(row, 1).text(),
        }
        dialog = ColorEditDialog(self, current_entry)
        if dialog.exec_() == QDialog.Accepted:
            self._insert_color(dialog.get_value(), row=row)

    def remove_color(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Auswahl erforderlich", "Bitte wählen Sie eine Farbe zum Entfernen aus.")
            return
        self.table.removeRow(row)

    def get_colors(self):
        colors = []
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            color_item = self.table.item(row, 1)
            if name_item and color_item:
                colors.append({"name": name_item.text(), "color": color_item.text()})
        return colors


class ColorEditDialog(QDialog):
    def __init__(self, parent=None, color_entry=None):
        super(ColorEditDialog, self).__init__(parent)

        self.color_entry = color_entry or {"name": "", "color": "#ffffff"}
        self.setWindowTitle("Zeilenfarbe bearbeiten")
        self.setMinimumWidth(300)

        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)

        self.name_edit = QLineEdit(self.color_entry.get("name", ""))
        layout.addRow("Name:", self.name_edit)

        self.color_hex = self.color_entry.get("color", "#ffffff")
        color_layout = QHBoxLayout()
        self.color_display = QLabel(self.color_hex.upper())
        self.color_display.setAlignment(Qt.AlignCenter)
        self.color_display.setMinimumHeight(30)
        self._update_preview()
        color_layout.addWidget(self.color_display)

        select_button = QPushButton("Farbe wählen")
        select_button.clicked.connect(self.choose_color)
        color_layout.addWidget(select_button)

        layout.addRow("Farbe:", color_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _update_preview(self):
        self.color_display.setText(self.color_hex.upper())
        self.color_display.setStyleSheet(f"background-color: {self.color_hex}; border: 1px solid #999;")

    def choose_color(self):
        color = QColorDialog.getColor(QColor(self.color_hex), self, "Farbe auswählen")
        if color.isValid():
            self.color_hex = color.name()
            self._update_preview()

    def accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Pflichtfeld", "Bitte geben Sie einen Namen für die Farbe ein.")
            return
        super().accept()

    def get_value(self):
        return {
            "name": self.name_edit.text().strip(),
            "color": self.color_hex,
        }


class NumberingTab(QWidget):
    def __init__(self, numbering=None):
        super(NumberingTab, self).__init__()
        self.numbering = copy.deepcopy(DEFAULT_MASTER_DATA["numbering"])
        if numbering:
            self.numbering.update(numbering)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)

        self.prefix_edit = QLineEdit(self.numbering.get("prefix", "IT"))
        layout.addRow("Prefix:", self.prefix_edit)

        self.separator_edit = QLineEdit(self.numbering.get("separator", "-"))
        self.separator_edit.setMaxLength(3)
        layout.addRow("Trenner:", self.separator_edit)

        self.padding_spin = QSpinBox()
        self.padding_spin.setRange(1, 8)
        self.padding_spin.setValue(int(self.numbering.get("padding", 4)))
        layout.addRow("Stellen:", self.padding_spin)

        self.start_spin = QSpinBox()
        self.start_spin.setRange(1, 999999)
        self.start_spin.setValue(int(self.numbering.get("start", 1)))
        layout.addRow("Startwert:", self.start_spin)

        self.preview_label = QLabel()
        layout.addRow("Vorschau:", self.preview_label)

        for widget in (self.prefix_edit, self.separator_edit):
            widget.textChanged.connect(self.update_preview)
        self.padding_spin.valueChanged.connect(self.update_preview)
        self.start_spin.valueChanged.connect(self.update_preview)

        self.update_preview()

    def update_preview(self):
        prefix = self.prefix_edit.text().strip()
        separator = self.separator_edit.text()
        padding = self.padding_spin.value()
        example_number = str(self.start_spin.value()).zfill(padding)
        preview = f"{prefix}{separator}{example_number}" if prefix or separator else example_number
        self.preview_label.setText(preview)

    def get_values(self):
        return {
            "prefix": self.prefix_edit.text().strip(),
            "separator": self.separator_edit.text(),
            "padding": self.padding_spin.value(),
            "start": self.start_spin.value(),
        }
