from datetime import datetime

import pandas as pd
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from inventory_app.constants import DEFAULT_MASTER_DATA


class DeviceDialog(QDialog):
    """Dialog zum Hinzufügen oder Bearbeiten eines Geräts"""

    def __init__(self, parent=None, edit_values=None):
        super(DeviceDialog, self).__init__(parent)

        self._owner = parent
        self.edit_values = edit_values

        if edit_values:
            self.setWindowTitle("Gerät bearbeiten")
        else:
            self.setWindowTitle("Neues Gerät hinzufügen")

        self.setMinimumWidth(600)
        self.init_ui()

        if self.edit_values:
            self.populate_fields()
        else:
            self.suggest_next_device_id()

    def suggest_next_device_id(self):
        if hasattr(self._owner, "generate_next_device_id"):
            next_id = self._owner.generate_next_device_id()
            if next_id:
                self.device_id.setText(next_id)

    def init_ui(self):
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.device_id = QLineEdit()
        form_layout.addRow("Gerätenummer:", self.device_id)

        self.device_type = QComboBox()
        self.device_type.setEditable(True)
        self.device_type.addItems(self._get_master_values("device_types"))
        form_layout.addRow("Gerätetyp:", self.device_type)

        self.brand = QLineEdit()
        form_layout.addRow("Marke:", self.brand)

        self.model = QLineEdit()
        form_layout.addRow("Modell:", self.model)

        self.serial = QLineEdit()
        form_layout.addRow("Seriennummer:", self.serial)

        self.assigned_user = QLineEdit()
        form_layout.addRow("Zugewiesener Benutzer:", self.assigned_user)

        self.location = QComboBox()
        self.location.setEditable(True)
        self.location.addItems(self._get_master_values("locations"))
        form_layout.addRow("Standort:", self.location)

        self.office = QComboBox()
        self.office.setEditable(True)
        self.office.addItems(self._get_master_values("offices"))
        form_layout.addRow("Büro:", self.office)

        self.purchase_date = QDateEdit()
        self.purchase_date.setCalendarPopup(True)
        self.purchase_date.setDate(QDate.currentDate())
        form_layout.addRow("Kaufdatum:", self.purchase_date)

        self.condition = QComboBox()
        self.condition.addItems(self._get_master_values("conditions"))
        form_layout.addRow("Zustand:", self.condition)

        self.status = QComboBox()
        self.status.addItems(self._get_master_values("statuses"))
        form_layout.addRow("Status:", self.status)

        self.notes = QTextEdit()
        self.notes.setMaximumHeight(100)
        form_layout.addRow("Anmerkung:", self.notes)

        self.row_color = QComboBox()
        row_color_names = self._get_row_color_names()
        self.row_color.addItems(["Keine"] + row_color_names)
        form_layout.addRow("Zeilenfarbe:", self.row_color)

        layout.addLayout(form_layout)

        template_group = QGroupBox("Vorlagen")
        template_layout = QHBoxLayout()

        self.template_combo = QComboBox()
        self.load_templates()
        template_layout.addWidget(QLabel("Vorlage:"))
        template_layout.addWidget(self.template_combo, 1)

        self.apply_template_btn = QPushButton("Anwenden")
        self.apply_template_btn.clicked.connect(self.apply_template)
        template_layout.addWidget(self.apply_template_btn)

        self.save_template_btn = QPushButton("Speichern als...")
        self.save_template_btn.clicked.connect(self.save_as_template)
        template_layout.addWidget(self.save_template_btn)

        self.manage_templates_btn = QPushButton("Verwalten")
        self.manage_templates_btn.clicked.connect(self.manage_templates)
        template_layout.addWidget(self.manage_templates_btn)

        template_group.setLayout(template_layout)
        layout.addWidget(template_group)

        button_layout = QHBoxLayout()

        cancel_button = QPushButton("Abbrechen")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        save_button = QPushButton("Speichern")
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

    def load_templates(self):
        self.template_combo.clear()
        self.template_combo.addItem("-- Vorlage auswählen --")

        if hasattr(self._owner, "config") and "templates" in self._owner.config:
            templates = self._owner.config["templates"]
            for template_name in templates.keys():
                self.template_combo.addItem(template_name)

    def apply_template(self):
        template_name = self.template_combo.currentText()
        if template_name == "-- Vorlage auswählen --":
            return

        if hasattr(self._owner, "config") and "templates" in self._owner.config:
            templates = self._owner.config["templates"]
            if template_name in templates:
                template_data = templates[template_name]

                device_type = template_data.get("Gerätetyp", "")
                index = self.device_type.findText(device_type)
                if index >= 0:
                    self.device_type.setCurrentIndex(index)
                else:
                    self.device_type.setEditText(device_type)

                self.brand.setText(template_data.get("Marke", ""))
                self.model.setText(template_data.get("Modell", ""))
                self.serial.setText(template_data.get("Seriennummer", ""))
                self.assigned_user.setText(template_data.get("Zugewiesener_Benutzer", ""))

                location = template_data.get("Standort", "")
                index = self.location.findText(location)
                if index >= 0:
                    self.location.setCurrentIndex(index)
                else:
                    self.location.setEditText(location)

                office = template_data.get("Büro", "")
                index = self.office.findText(office)
                if index >= 0:
                    self.office.setCurrentIndex(index)
                else:
                    self.office.setEditText(office)

                condition = template_data.get("Zustand", "")
                self._set_combo_value(self.condition, condition)

                status = template_data.get("Status", "")
                self._set_combo_value(self.status, status)

                self.notes.setText(template_data.get("Anmerkung", ""))

                row_color = template_data.get("Zeilenfarbe", "Keine")
                self._set_combo_value(self.row_color, row_color)

                QMessageBox.information(self, "Vorlage angewendet", f"Die Vorlage '{template_name}' wurde erfolgreich angewendet.")

    def save_as_template(self):
        template_name, ok = QInputDialog.getText(self, "Vorlage speichern", "Name der Vorlage:")

        if ok and template_name:
            field_selection_dialog = TemplateFieldSelectionDialog(self)
            if field_selection_dialog.exec_() == QDialog.Accepted:
                selected_fields = field_selection_dialog.get_selected_fields()

                template_data = {}
                all_values = self.get_values()

                for field in selected_fields:
                    if field in all_values:
                        template_data[field] = all_values[field]

                for key in ("Gerätenummer", "Kaufdatum", "Letzte_Aktualisierung"):
                    template_data.pop(key, None)

                if "templates" not in self._owner.config:
                    self._owner.config["templates"] = {}

                self._owner.config["templates"][template_name] = template_data
                self._owner.save_config()

                self.load_templates()

                QMessageBox.information(self, "Vorlage gespeichert", f"Die Vorlage '{template_name}' wurde erfolgreich gespeichert.")

    def manage_templates(self):
        dialog = TemplateManagerDialog(self._owner, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_templates()

    def populate_fields(self):
        self.device_id.setText(str(self.edit_values.get("Gerätenummer", "")))
        self.device_id.setReadOnly(True)

        device_type = str(self.edit_values.get("Gerätetyp", ""))
        index = self.device_type.findText(device_type)
        if index >= 0:
            self.device_type.setCurrentIndex(index)
        else:
            self.device_type.setEditText(device_type)

        self.brand.setText(str(self.edit_values.get("Marke", "")))
        self.model.setText(str(self.edit_values.get("Modell", "")))
        self.serial.setText(str(self.edit_values.get("Seriennummer", "")))
        self.assigned_user.setText(str(self.edit_values.get("Zugewiesener_Benutzer", "")))
        self.location.setEditText(str(self.edit_values.get("Standort", "")))
        self.office.setEditText(str(self.edit_values.get("Büro", "")))

        if "Kaufdatum" in self.edit_values and pd.notna(self.edit_values["Kaufdatum"]):
            try:
                date_parts = self.edit_values["Kaufdatum"].split("-")
                if len(date_parts) == 3:
                    self.purchase_date.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
            except (ValueError, TypeError, AttributeError):
                pass

        condition = str(self.edit_values.get("Zustand", ""))
        self._set_combo_value(self.condition, condition)

        status = str(self.edit_values.get("Status", ""))
        self._set_combo_value(self.status, status)

        self.notes.setText(str(self.edit_values.get("Anmerkung", "")))

        row_color = str(self.edit_values.get("Zeilenfarbe", "Keine"))
        self._set_combo_value(self.row_color, row_color)

    def get_values(self):
        values = {
            "Gerätenummer": self.device_id.text(),
            "Gerätetyp": self.device_type.currentText(),
            "Marke": self.brand.text(),
            "Modell": self.model.text(),
            "Seriennummer": self.serial.text(),
            "Zugewiesener_Benutzer": self.assigned_user.text(),
            "Standort": self.location.currentText(),
            "Büro": self.office.currentText(),
            "Kaufdatum": self.purchase_date.date().toString("yyyy-MM-dd"),
            "Zustand": self.condition.currentText(),
            "Status": self.status.currentText(),
            "Anmerkung": self.notes.toPlainText(),
            "Zeilenfarbe": self.row_color.currentText(),
            "Letzte_Aktualisierung": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        return values

    def accept(self):
        if not self.device_id.text() or not self.device_type.currentText():
            QMessageBox.warning(self, "Pflichtfelder", "Bitte füllen Sie alle Pflichtfelder aus.")
            return

        if not self.edit_values and hasattr(self._owner, "df") and not self._owner.df.empty:
            existing_ids = self._owner.df["Gerätenummer"].astype(str).tolist()
            if self.device_id.text() in existing_ids:
                QMessageBox.warning(
                    self,
                    "Doppelte Gerätenummer",
                    "Diese Gerätenummer existiert bereits. Bitte wählen Sie eine andere.",
                )
                return

        super().accept()

    def reject(self):
        super().reject()

    def _get_master_values(self, key):
        if self._owner and hasattr(self._owner, "get_master_list"):
            configured = self._owner.get_master_list(key)
            if configured:
                return configured
        return list(DEFAULT_MASTER_DATA.get(key, []))

    def _get_row_color_names(self):
        if self._owner and hasattr(self._owner, "get_row_color_names"):
            names = self._owner.get_row_color_names()
            if names:
                return names
        return [entry.get("name") for entry in DEFAULT_MASTER_DATA["row_colors"]]

    def _set_combo_value(self, combo, value):
        if not value:
            return
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            combo.addItem(value)
            combo.setCurrentText(value)


class TemplateFieldSelectionDialog(QDialog):
    """Dialog zur Auswahl der Felder, die in einer Vorlage gespeichert werden sollen"""

    def __init__(self, parent=None):
        super(TemplateFieldSelectionDialog, self).__init__(parent)

        self.setWindowTitle("Felder für Vorlage auswählen")
        self.setMinimumWidth(400)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Wählen Sie die Felder aus, die in der Vorlage gespeichert werden sollen:"))

        self.checkboxes = {}

        fields_layout = QVBoxLayout()

        available_fields = [
            "Gerätetyp",
            "Marke",
            "Modell",
            "Seriennummer",
            "Zugewiesener_Benutzer",
            "Standort",
            "Büro",
            "Zustand",
            "Status",
            "Anmerkung",
        ]

        default_selected = ["Gerätetyp", "Marke", "Modell", "Standort", "Zustand", "Status"]

        for field in available_fields:
            checkbox = QCheckBox(field)
            checkbox.setChecked(field in default_selected)
            self.checkboxes[field] = checkbox
            fields_layout.addWidget(checkbox)

        layout.addLayout(fields_layout)

        button_layout = QHBoxLayout()

        select_all_button = QPushButton("Alle auswählen")
        select_all_button.clicked.connect(self.select_all)
        button_layout.addWidget(select_all_button)

        select_none_button = QPushButton("Keine auswählen")
        select_none_button.clicked.connect(self.select_none)
        button_layout.addWidget(select_none_button)

        button_layout.addStretch()

        cancel_button = QPushButton("Abbrechen")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)

    def select_all(self):
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)

    def select_none(self):
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)

    def get_selected_fields(self):
        selected_fields = []
        for field, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                selected_fields.append(field)
        return selected_fields


class TemplateManagerDialog(QDialog):
    """Dialog zur Verwaltung von Gerätevorlagen"""

    def __init__(self, parent=None, device_dialog=None):
        super(TemplateManagerDialog, self).__init__(parent)

        self._owner = parent
        self.device_dialog = device_dialog
        self.setWindowTitle("Vorlagen verwalten")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        self.init_ui()
        self.load_templates()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Vorlagenname", "Aktionen"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        close_button = QPushButton("Schließen")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def load_templates(self):
        self.table.setRowCount(0)

        if hasattr(self._owner, "config") and "templates" in self._owner.config:
            templates = self._owner.config["templates"]

            for template_name in templates.keys():
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)

                self.table.setItem(row_position, 0, QTableWidgetItem(template_name))

                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)

                edit_button = QPushButton("Bearbeiten")
                edit_button.clicked.connect(lambda checked, name=template_name: self.edit_template(name))
                actions_layout.addWidget(edit_button)

                delete_button = QPushButton("Löschen")
                delete_button.clicked.connect(lambda checked, name=template_name: self.delete_template(name))
                actions_layout.addWidget(delete_button)

                self.table.setCellWidget(row_position, 1, actions_widget)

    def edit_template(self, template_name):
        if hasattr(self._owner, "config") and "templates" in self._owner.config:
            templates = self._owner.config["templates"]
            if template_name in templates:
                template_data = templates[template_name]

                master_data = getattr(self._owner, "config", {}).get("master_data", DEFAULT_MASTER_DATA)
                dialog = TemplateEditDialog(self, template_name, template_data, master_data=master_data)
                if dialog.exec_() == QDialog.Accepted:
                    new_name, new_data = dialog.get_values()

                    if new_name != template_name:
                        del self._owner.config["templates"][template_name]

                    self._owner.config["templates"][new_name] = new_data
                    self._owner.save_config()

                    self.load_templates()

                    if self.device_dialog:
                        self.device_dialog.load_templates()

    def delete_template(self, template_name):
        reply = QMessageBox.question(
            self,
            "Vorlage löschen",
            f"Möchten Sie die Vorlage '{template_name}' wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            if hasattr(self._owner, "config") and "templates" in self._owner.config:
                if template_name in self._owner.config["templates"]:
                    del self._owner.config["templates"][template_name]
                    self._owner.save_config()

                    self.load_templates()

                    if self.device_dialog:
                        self.device_dialog.load_templates()


class TemplateEditDialog(QDialog):
    """Dialog zum Bearbeiten einer Vorlage"""

    def __init__(self, parent=None, template_name="", template_data=None, master_data=None):
        super(TemplateEditDialog, self).__init__(parent)

        self.template_name = template_name
        self.template_data = template_data or {}
        self.master_data = master_data or DEFAULT_MASTER_DATA

        self.setWindowTitle("Vorlage bearbeiten")
        self.setMinimumWidth(500)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Vorlagenname:"))
        self.name_edit = QLineEdit(self.template_name)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        form_layout = QFormLayout()

        self.device_type = QComboBox()
        self.device_type.setEditable(True)
        self.device_type.addItems(self.master_data.get("device_types", DEFAULT_MASTER_DATA["device_types"]))
        device_type = self.template_data.get("Gerätetyp", "")
        index = self.device_type.findText(device_type)
        if index >= 0:
            self.device_type.setCurrentIndex(index)
        else:
            self.device_type.setEditText(device_type)
        form_layout.addRow("Gerätetyp:", self.device_type)

        self.brand = QLineEdit(self.template_data.get("Marke", ""))
        form_layout.addRow("Marke:", self.brand)

        self.model = QLineEdit(self.template_data.get("Modell", ""))
        form_layout.addRow("Modell:", self.model)

        self.serial = QLineEdit(self.template_data.get("Seriennummer", ""))
        form_layout.addRow("Seriennummer:", self.serial)

        self.assigned_user = QLineEdit(self.template_data.get("Zugewiesener_Benutzer", ""))
        form_layout.addRow("Zugewiesener Benutzer:", self.assigned_user)

        self.location = QComboBox()
        self.location.setEditable(True)
        self.location.addItems(self.master_data.get("locations", DEFAULT_MASTER_DATA["locations"]))
        location = self.template_data.get("Standort", "")
        index = self.location.findText(location)
        if index >= 0:
            self.location.setCurrentIndex(index)
        else:
            self.location.setEditText(location)
        form_layout.addRow("Standort:", self.location)

        self.office = QComboBox()
        self.office.setEditable(True)
        self.office.addItems(self.master_data.get("offices", DEFAULT_MASTER_DATA["offices"]))
        office = self.template_data.get("Büro", "")
        index = self.office.findText(office)
        if index >= 0:
            self.office.setCurrentIndex(index)
        else:
            self.office.setEditText(office)
        form_layout.addRow("Büro:", self.office)

        self.condition = QComboBox()
        self.condition.addItems(self.master_data.get("conditions", DEFAULT_MASTER_DATA["conditions"]))
        condition = self.template_data.get("Zustand", "")
        index = self.condition.findText(condition)
        if index >= 0:
            self.condition.setCurrentIndex(index)
        form_layout.addRow("Zustand:", self.condition)

        self.status = QComboBox()
        self.status.addItems(self.master_data.get("statuses", DEFAULT_MASTER_DATA["statuses"]))
        status = self.template_data.get("Status", "")
        index = self.status.findText(status)
        if index >= 0:
            self.status.setCurrentIndex(index)
        form_layout.addRow("Status:", self.status)

        self.notes = QTextEdit()
        self.notes.setMaximumHeight(100)
        self.notes.setText(self.template_data.get("Anmerkung", ""))
        form_layout.addRow("Anmerkung:", self.notes)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        cancel_button = QPushButton("Abbrechen")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        save_button = QPushButton("Speichern")
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

    def get_values(self):
        values = {
            "Gerätetyp": self.device_type.currentText(),
            "Marke": self.brand.text(),
            "Modell": self.model.text(),
            "Seriennummer": self.serial.text(),
            "Zugewiesener_Benutzer": self.assigned_user.text(),
            "Standort": self.location.currentText(),
            "Büro": self.office.currentText(),
            "Zustand": self.condition.currentText(),
            "Status": self.status.currentText(),
            "Anmerkung": self.notes.toPlainText(),
        }
        return self.name_edit.text(), values
