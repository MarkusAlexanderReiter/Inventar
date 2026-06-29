from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)


class HeaderFilterDialog(QDialog):
    """Dialog that mimics Excel-style column value filtering."""

    EMPTY_PLACEHOLDER = "— Leer —"

    def __init__(self, column_name, values, selected_values=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Filter: {column_name}")
        self.resize(320, 420)

        self._values = list(values)
        self._selected_values = set(selected_values) if selected_values else None

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Werte auswählen:"))

        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        layout.addWidget(self.list_widget)

        for value in self._values:
            display_value = value if value else self.EMPTY_PLACEHOLDER
            item = QListWidgetItem(display_value)
            item.setData(Qt.UserRole, value)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)

            if self._selected_values is None:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Checked if value in self._selected_values else Qt.Unchecked)

            self.list_widget.addItem(item)

        control_layout = QHBoxLayout()
        select_all_btn = QPushButton("Alle auswählen")
        select_all_btn.clicked.connect(self.select_all)
        control_layout.addWidget(select_all_btn)

        clear_all_btn = QPushButton("Alle abwählen")
        clear_all_btn.clicked.connect(self.clear_all)
        control_layout.addWidget(clear_all_btn)

        layout.addLayout(control_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def select_all(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(Qt.Checked)

    def clear_all(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(Qt.Unchecked)

    def get_selected_values(self):
        values = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.Checked:
                values.append(item.data(Qt.UserRole))
        return values
