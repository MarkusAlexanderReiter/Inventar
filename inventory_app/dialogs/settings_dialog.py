from PyQt5.QtWidgets import (
    QFileDialog,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)

        self._owner = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.csv_path = QLineEdit()
        self.csv_path.setText(self._owner.csv_file)
        browse_button = QPushButton("Durchsuchen...")
        browse_button.clicked.connect(self.browse_csv_path)
        csv_layout = QHBoxLayout()
        csv_layout.addWidget(QLabel("CSV-Dateipfad:"))
        csv_layout.addWidget(self.csv_path)
        csv_layout.addWidget(browse_button)
        layout.addLayout(csv_layout)

        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.clicked.connect(self.reject)
        self.save_button = QPushButton("Speichern")
        self.save_button.clicked.connect(self.accept)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def browse_csv_path(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "CSV-Datei auswählen", "", "CSV Dateien (*.csv)", options=options
        )

        if file_name:
            self.csv_path.setText(file_name)

    def get_csv_path(self):
        return self.csv_path.text()
