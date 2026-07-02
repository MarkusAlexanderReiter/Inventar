from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from inventory_app.constants import DEFAULT_MASTER_DATA


class BulkUpdateDialog(QDialog):
    """Dialog zum gleichzeitigen Anpassen mehrerer Geräte"""

    def __init__(self, parent=None, master_data=None):
        super(BulkUpdateDialog, self).__init__(parent)

        self.setWindowTitle("Mehrfachänderung durchführen")
        self.setMinimumWidth(500)
        
        # Load master data or use defaults
        self.master_data = master_data if master_data else DEFAULT_MASTER_DATA
        self.status_values = self.master_data.get("statuses", DEFAULT_MASTER_DATA["statuses"])
        self.row_color_values = [entry["name"] for entry in self.master_data.get("row_colors", DEFAULT_MASTER_DATA["row_colors"])]
        self.device_types = self.master_data.get("device_types", DEFAULT_MASTER_DATA["device_types"])
        self.locations = self.master_data.get("locations", DEFAULT_MASTER_DATA["locations"])
        self.offices = self.master_data.get("offices", DEFAULT_MASTER_DATA["offices"])
        self.conditions = self.master_data.get("conditions", DEFAULT_MASTER_DATA["conditions"])
        self.users = self.master_data.get("users", DEFAULT_MASTER_DATA["users"])

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Wählen Sie aus, welche Felder für alle markierten Geräte geändert werden sollen."))

        form_layout = QFormLayout()

        # Gerätetyp
        self.type_checkbox = QCheckBox("Gerätetyp ändern")
        self.type_combo = QComboBox()
        self.type_combo.setEditable(True)
        self.type_combo.addItems(self.device_types)
        self.type_combo.setEnabled(False)
        self.type_checkbox.toggled.connect(self.type_combo.setEnabled)
        form_layout.addRow(self.type_checkbox, self.type_combo)

        # Marke
        self.brand_checkbox = QCheckBox("Marke ändern")
        self.brand_input = QLineEdit()
        self.brand_input.setEnabled(False)
        self.brand_checkbox.toggled.connect(self.brand_input.setEnabled)
        form_layout.addRow(self.brand_checkbox, self.brand_input)

        # Modell
        self.model_checkbox = QCheckBox("Modell ändern")
        self.model_input = QLineEdit()
        self.model_input.setEnabled(False)
        self.model_checkbox.toggled.connect(self.model_input.setEnabled)
        form_layout.addRow(self.model_checkbox, self.model_input)

        # Seriennummer
        self.serial_checkbox = QCheckBox("Seriennummer ändern")
        self.serial_input = QLineEdit()
        self.serial_input.setEnabled(False)
        self.serial_checkbox.toggled.connect(self.serial_input.setEnabled)
        form_layout.addRow(self.serial_checkbox, self.serial_input)

        # Zugewiesener Benutzer
        self.user_checkbox = QCheckBox("Zugewiesener Benutzer ändern")
        self.user_combo = QComboBox()
        self.user_combo.setEditable(True)
        self.user_combo.addItems([""] + self.users)
        self.user_combo.setEnabled(False)
        self.user_checkbox.toggled.connect(self.user_combo.setEnabled)
        form_layout.addRow(self.user_checkbox, self.user_combo)

        # Standort
        self.location_checkbox = QCheckBox("Standort ändern")
        self.location_combo = QComboBox()
        self.location_combo.setEditable(True)
        self.location_combo.addItems(self.locations)
        self.location_combo.setEnabled(False)
        self.location_checkbox.toggled.connect(self.location_combo.setEnabled)
        form_layout.addRow(self.location_checkbox, self.location_combo)

        # Büro
        self.office_checkbox = QCheckBox("Büro ändern")
        self.office_combo = QComboBox()
        self.office_combo.setEditable(True)
        self.office_combo.addItems(self.offices)
        self.office_combo.setEnabled(False)
        self.office_checkbox.toggled.connect(self.office_combo.setEnabled)
        form_layout.addRow(self.office_checkbox, self.office_combo)

        # Kaufdatum
        self.date_checkbox = QCheckBox("Kaufdatum ändern")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setEnabled(False)
        self.date_checkbox.toggled.connect(self.date_input.setEnabled)
        form_layout.addRow(self.date_checkbox, self.date_input)

        # Zustand
        self.condition_checkbox = QCheckBox("Zustand ändern")
        self.condition_combo = QComboBox()
        self.condition_combo.addItems(self.conditions)
        self.condition_combo.setEnabled(False)
        self.condition_checkbox.toggled.connect(self.condition_combo.setEnabled)
        form_layout.addRow(self.condition_checkbox, self.condition_combo)

        # Status
        self.status_checkbox = QCheckBox("Status ändern")
        self.status_combo = QComboBox()
        self.status_combo.addItems(self.status_values)
        self.status_combo.setEnabled(False)
        self.status_checkbox.toggled.connect(self.status_combo.setEnabled)
        form_layout.addRow(self.status_checkbox, self.status_combo)

        # Anmerkung
        self.note_checkbox = QCheckBox("Anmerkung setzen")
        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(80)
        self.note_input.setEnabled(False)
        self.note_checkbox.toggled.connect(self.note_input.setEnabled)
        form_layout.addRow(self.note_checkbox, self.note_input)

        # Zeilenfarbe
        self.color_checkbox = QCheckBox("Zeilenfarbe ändern")
        self.color_combo = QComboBox()
        self.color_combo.addItems(["Keine"] + self.row_color_values)
        self.color_combo.setEnabled(False)
        self.color_checkbox.toggled.connect(self.color_combo.setEnabled)
        form_layout.addRow(self.color_checkbox, self.color_combo)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        cancel_button = QPushButton("Abbrechen")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        apply_button = QPushButton("Übernehmen")
        apply_button.clicked.connect(self.accept)
        button_layout.addWidget(apply_button)

        layout.addLayout(button_layout)

    def get_updates(self):
        updates = {}
        if self.type_checkbox.isChecked():
            updates["Gerätetyp"] = self.type_combo.currentText()
        if self.brand_checkbox.isChecked():
            updates["Marke"] = self.brand_input.text()
        if self.model_checkbox.isChecked():
            updates["Modell"] = self.model_input.text()
        if self.serial_checkbox.isChecked():
            updates["Seriennummer"] = self.serial_input.text()
        if self.user_checkbox.isChecked():
            updates["Zugewiesener_Benutzer"] = self.user_combo.currentText()
        if self.location_checkbox.isChecked():
            updates["Standort"] = self.location_combo.currentText()
        if self.office_checkbox.isChecked():
            updates["Büro"] = self.office_combo.currentText()
        if self.date_checkbox.isChecked():
            updates["Kaufdatum"] = self.date_input.date().toString("yyyy-MM-dd")
        if self.condition_checkbox.isChecked():
            updates["Zustand"] = self.condition_combo.currentText()
        if self.status_checkbox.isChecked():
            updates["Status"] = self.status_combo.currentText()
        if self.note_checkbox.isChecked():
            updates["Anmerkung"] = self.note_input.toPlainText()
        if self.color_checkbox.isChecked():
            updates["Zeilenfarbe"] = self.color_combo.currentText()
        return updates

    def accept(self):
        if not self.get_updates():
            QMessageBox.warning(self, "Keine Auswahl", "Bitte wählen Sie mindestens ein Feld zur Aktualisierung aus.")
            return
        super().accept()
