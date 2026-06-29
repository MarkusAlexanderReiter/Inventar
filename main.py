import os
import sys

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication

from inventory_app.main_window import InventoryManager
from inventory_app.styles import APP_STYLESHEET


def _resolve_icon_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.dirname(__file__))


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    font = QFont("Segoe UI", 9)
    app.setFont(font)
    app.setStyleSheet(APP_STYLESHEET)

    base_path = _resolve_icon_path()
    icon_path = os.path.join(base_path, "logistics.ico")
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)

    window = InventoryManager()
    window.setWindowIcon(app_icon)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
