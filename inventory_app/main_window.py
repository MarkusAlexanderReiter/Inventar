from __future__ import annotations

import copy
import json
import os
from datetime import datetime

import pandas as pd
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QAction,
    QFileDialog,
    QFrame,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QHBoxLayout,
    QDialog,
    QStyle,
)

from inventory_app import core
from inventory_app.constants import COLUMNS, DEFAULT_MASTER_DATA
from inventory_app.repository import InventoryRepository
from inventory_app.dialogs.bulk_update_dialog import BulkUpdateDialog
from inventory_app.dialogs.device_dialog import DeviceDialog
from inventory_app.dialogs.master_data_dialog import MasterDataDialog
from inventory_app.dialogs.settings_dialog import SettingsDialog
from inventory_app.dialogs.header_filter_dialog import HeaderFilterDialog


class InventoryManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Geräte-Inventarsystem")

        self.config_file = "inventory_config.json"
        self.load_config()
        self.ensure_master_data_defaults()
        self.column_filters = {}

        if "window_geometry" in self.config:
            self.setGeometry(
                self.config["window_geometry"].get("x", 100),
                self.config["window_geometry"].get("y", 100),
                self.config["window_geometry"].get("width", 1280),
                self.config["window_geometry"].get("height", 800),
            )
        else:
            self.setGeometry(100, 100, 1280, 800)

        self.load_data()
        self.seed_users_from_inventory()
        self.init_ui()

    def load_config(self) -> None:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, OSError):
                self.create_default_config()
        else:
            self.create_default_config()

    def create_default_config(self) -> None:
        self.config = {
            "csv_file": "inventory.csv",
            "window_geometry": {
                "x": 100,
                "y": 100,
                "width": 1280,
                "height": 800,
            },
            "column_widths": {},
            "master_data": copy.deepcopy(DEFAULT_MASTER_DATA),
        }
        self.save_config()

    def save_config(self) -> None:
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def save_window_geometry(self) -> None:
        geometry = self.geometry()
        self.config["window_geometry"] = {
            "x": geometry.x(),
            "y": geometry.y(),
            "width": geometry.width(),
            "height": geometry.height(),
        }
        self.save_config()

    def save_column_widths(self) -> None:
        column_widths = {}
        for i in range(self.table.columnCount()):
            column_name = self.table_headers[i]
            column_widths[column_name] = self.table.columnWidth(i)
        self.config["column_widths"] = column_widths
        self.save_config()

    def ensure_master_data_defaults(self) -> None:
        if "master_data" not in self.config:
            self.config["master_data"] = copy.deepcopy(DEFAULT_MASTER_DATA)
            self.save_config()
            return

        master_data = self.config["master_data"]
        updated = False

        for key, value in DEFAULT_MASTER_DATA.items():
            if key not in master_data:
                master_data[key] = copy.deepcopy(value)
                updated = True
            elif isinstance(value, dict):
                for inner_key, inner_value in value.items():
                    if inner_key not in master_data[key]:
                        master_data[key][inner_key] = copy.deepcopy(inner_value)
                        updated = True

        if updated:
            self.save_config()

    def seed_users_from_inventory(self) -> None:
        """Befüllt die Benutzer-Stammdaten einmalig aus den vorhandenen Inventardaten."""
        if self.config.get("users_seeded"):
            return

        users = set(self.get_master_list("users"))
        if hasattr(self, "df") and not self.df.empty and "Zugewiesener_Benutzer" in self.df:
            for value in self.df["Zugewiesener_Benutzer"].dropna().astype(str):
                value = value.strip()
                if value:
                    users.add(value)

        self.config["master_data"]["users"] = sorted(users, key=str.casefold)
        self.config["users_seeded"] = True
        self.save_config()

    def get_master_list(self, key: str) -> list:
        master_data = self.config.get("master_data", {})
        values = master_data.get(key)
        if values is None:
            values = DEFAULT_MASTER_DATA.get(key, [])
        return list(values)

    def get_row_color_entries(self) -> list:
        master_data = self.config.get("master_data", {})
        return master_data.get("row_colors", DEFAULT_MASTER_DATA["row_colors"])

    def get_row_color_names(self) -> list:
        return [entry.get("name") for entry in self.get_row_color_entries() if entry.get("name")]

    def get_row_color_map(self) -> dict:
        color_map = {}
        for entry in self.get_row_color_entries():
            name = entry.get("name")
            color_value = entry.get("color")
            if name and color_value:
                qcolor = QColor(color_value)
                if qcolor.isValid():
                    color_map[name] = qcolor
        return color_map

    def get_numbering_settings(self) -> dict:
        master_data = self.config.get("master_data", {})
        settings = master_data.get("numbering", {})
        merged = copy.deepcopy(DEFAULT_MASTER_DATA["numbering"])
        merged.update(settings)
        return merged

    def generate_next_device_id(self) -> str:
        existing_ids = []
        if hasattr(self, "df") and not self.df.empty and "Gerätenummer" in self.df:
            existing_ids = self.df["Gerätenummer"].astype(str).tolist()
        return core.generate_next_device_id(existing_ids, self.get_numbering_settings())

    def closeEvent(self, event):
        self.save_window_geometry()
        self.save_column_widths()
        event.accept()

    def load_data(self) -> None:
        self.csv_file = self.config["csv_file"]
        self.repository = InventoryRepository(self.csv_file)
        self.df = self.repository.load()

    def save_data(self) -> None:
        self.repository.save(self.df)

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("appRoot")
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(14, 12, 14, 12)
        main_layout.setSpacing(10)

        self.create_menu()

        toolbar_frame = QFrame()
        toolbar_frame.setObjectName("toolbar")
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(10, 9, 10, 9)
        toolbar_layout.setSpacing(8)

        self.add_button = self._create_action_button(
            "Neues Gerät",
            QStyle.SP_FileDialogNewFolder,
            self.show_add_dialog,
            primary=True,
        )
        toolbar_layout.addWidget(self.add_button)

        self.edit_button = self._create_action_button("Bearbeiten", QStyle.SP_FileDialogDetailedView, self.edit_selected_item)
        toolbar_layout.addWidget(self.edit_button)

        self.copy_button = self._create_action_button("Kopieren", QStyle.SP_FileIcon, self.copy_selected_item)
        toolbar_layout.addWidget(self.copy_button)

        self.bulk_update_button = self._create_action_button(
            "Mehrfach ändern",
            QStyle.SP_DialogApplyButton,
            self.show_bulk_update_dialog,
        )
        toolbar_layout.addWidget(self.bulk_update_button)

        self.export_button = self._create_action_button("Exportieren", QStyle.SP_DialogSaveButton, self.export_data)
        toolbar_layout.addWidget(self.export_button)

        toolbar_layout.addStretch()

        self.clear_filters_button = self._create_action_button(
            "Filter löschen",
            QStyle.SP_DialogResetButton,
            self.clear_all_column_filters,
        )
        self.clear_filters_button.setMinimumWidth(130)
        toolbar_layout.addWidget(self.clear_filters_button)

        main_layout.addWidget(toolbar_frame)

        filter_frame = QFrame()
        filter_frame.setObjectName("filterBar")
        search_layout = QHBoxLayout(filter_frame)
        search_layout.setContentsMargins(10, 9, 10, 9)
        search_layout.setSpacing(8)

        search_label = QLabel("Suche")
        search_label.setObjectName("fieldLabel")
        search_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Suchbegriff eingeben...")
        self.search_input.setMinimumWidth(280)
        self.search_input.textChanged.connect(self.refresh_table)
        search_layout.addWidget(self.search_input, 1)

        self.filter_field = QComboBox()
        self.filter_field.setMinimumWidth(170)
        self.filter_field.addItems(
            [
                "Alle Felder",
                "Gerätenummer",
                "Gerätetyp",
                "Marke",
                "Modell",
                "Seriennummer",
                "Zugewiesener_Benutzer",
                "Standort",
                "Büro",
            ]
        )
        self.filter_field.currentIndexChanged.connect(self.refresh_table)
        search_layout.addWidget(self.filter_field)

        self.status_filter = QComboBox()
        self.status_filter.setMinimumWidth(130)
        self.status_filter.addItem("Alle")
        for status in self.get_master_list("statuses"):
            self.status_filter.addItem(status)
        self.status_filter.currentIndexChanged.connect(self.refresh_table)
        search_layout.addWidget(self.status_filter)

        main_layout.addWidget(filter_frame)

        table_frame = QFrame()
        table_frame.setObjectName("tableBand")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(1, 1, 1, 1)
        table_layout.setSpacing(0)
        self.table = QTableWidget()
        self.table.setObjectName("inventoryTable")
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.edit_selected_item)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(34)
        self.table.setShowGrid(True)

        self.table_headers = list(COLUMNS)

        self.table.setColumnCount(len(self.table_headers))
        self.table.setHorizontalHeaderLabels(self.table_headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self._update_filter_ui_state()

        if "column_widths" in self.config:
            for i, header in enumerate(self.table_headers):
                if header in self.config["column_widths"]:
                    self.table.setColumnWidth(i, self.config["column_widths"][header])
                else:
                    self.table.setColumnWidth(i, 120)
        else:
            for i in range(len(self.table_headers)):
                self.table.setColumnWidth(i, 120)

        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.horizontalHeader().customContextMenuRequested.connect(self.show_header_context_menu)

        table_layout.addWidget(self.table)
        main_layout.addWidget(table_frame, 1)

        status_frame = QFrame()
        status_frame.setObjectName("statusBand")
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(10, 8, 10, 8)
        status_layout.setSpacing(12)
        self.status_summary = QLabel("Statusübersicht: -")
        self.status_summary.setObjectName("mutedText")
        self.total_count = QLabel("Gesamt: 0")
        self.total_count.setObjectName("mutedText")

        status_layout.addWidget(self.status_summary)
        status_layout.addWidget(self.total_count)
        status_layout.addStretch()

        main_layout.addWidget(status_frame)

        self.refresh_table()

    def _create_action_button(self, text, icon_id, callback, primary=False):
        button = QPushButton(text)
        button.setIcon(self.style().standardIcon(icon_id))
        button.setIconSize(QSize(16, 16))
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(36)
        button.clicked.connect(callback)
        if primary:
            button.setObjectName("primaryButton")
        return button

    def show_header_context_menu(self, pos):
        header = self.table.horizontalHeader()
        column_index = header.logicalIndexAt(pos)

        menu = QMenu(self)

        sort_asc_action = QAction("Aufsteigend sortieren", self)
        sort_asc_action.triggered.connect(lambda: self.sort_table(column_index, Qt.AscendingOrder))
        menu.addAction(sort_asc_action)

        sort_desc_action = QAction("Absteigend sortieren", self)
        sort_desc_action.triggered.connect(lambda: self.sort_table(column_index, Qt.DescendingOrder))
        menu.addAction(sort_desc_action)

        reset_width_action = QAction("Spaltenbreite zurücksetzen", self)
        reset_width_action.triggered.connect(lambda: self.table.setColumnWidth(column_index, 120))
        menu.addAction(reset_width_action)

        filter_action = QAction("Filter...", self)
        filter_action.triggered.connect(lambda: self.show_header_filter_dialog(column_index))
        menu.addAction(filter_action)

        column_name = self.table_headers[column_index]
        if column_name in self.column_filters:
            clear_filter_action = QAction("Filter entfernen", self)
            clear_filter_action.triggered.connect(lambda: self.clear_column_filter(column_index))
            menu.addAction(clear_filter_action)

        menu.exec_(header.mapToGlobal(pos))

    def sort_table(self, column, order):
        self.table.sortItems(column, order)

    def get_column_unique_values(self, column_name):
        if column_name not in self.df.columns:
            return []

        series = self.df[column_name].fillna("").astype(str)
        return sorted(series.unique().tolist(), key=lambda value: value.lower())

    def show_header_filter_dialog(self, column_index):
        column_name = self.table_headers[column_index]
        values = self.get_column_unique_values(column_name)
        selected_values = self.column_filters.get(column_name)

        dialog = HeaderFilterDialog(column_name, values, selected_values, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            chosen_values = dialog.get_selected_values()
            normalized = [value if value is not None else "" for value in chosen_values]

            if len(normalized) == len(values):
                self.column_filters.pop(column_name, None)
            else:
                self.column_filters[column_name] = set(normalized)

            self.refresh_table()
            self._update_filter_ui_state()

    def clear_column_filter(self, column_index):
        column_name = self.table_headers[column_index]
        if column_name in self.column_filters:
            self.column_filters.pop(column_name, None)
            self.refresh_table()
            self._update_filter_ui_state()

    def clear_all_column_filters(self):
        changed = bool(self.column_filters)
        if self.column_filters:
            self.column_filters.clear()

        if hasattr(self, "search_input") and self.search_input.text():
            changed = True
            self.search_input.blockSignals(True)
            self.search_input.clear()
            self.search_input.blockSignals(False)

        if hasattr(self, "filter_field") and self.filter_field.currentIndex() != 0:
            changed = True
            self.filter_field.blockSignals(True)
            self.filter_field.setCurrentIndex(0)
            self.filter_field.blockSignals(False)

        if hasattr(self, "status_filter") and self.status_filter.currentIndex() != 0:
            changed = True
            self.status_filter.blockSignals(True)
            self.status_filter.setCurrentIndex(0)
            self.status_filter.blockSignals(False)

        if changed:
            self.refresh_table()
        self._update_filter_ui_state()

    def _has_active_filters(self):
        return (
            bool(self.column_filters)
            or (hasattr(self, "search_input") and bool(self.search_input.text()))
            or (hasattr(self, "filter_field") and self.filter_field.currentIndex() != 0)
            or (hasattr(self, "status_filter") and self.status_filter.currentIndex() != 0)
        )

    def _current_filtered_dataframe(self) -> pd.DataFrame:
        """Wendet die aktuell in der Oberfläche gewählten Filter an.

        Wird sowohl von der Tabellenansicht als auch vom Export genutzt, damit
        exportierte Daten immer exakt der angezeigten Auswahl entsprechen.
        """
        return core.filter_dataframe(
            self.df,
            status=self.status_filter.currentText(),
            search_text=self.search_input.text(),
            search_field=self.filter_field.currentText(),
            column_filters=self.column_filters,
        )

    def _update_filter_ui_state(self):
        header = self.table.horizontalHeader()
        indicator = " *"
        for i, column_name in enumerate(self.table_headers):
            header_item = self.table.horizontalHeaderItem(i)
            if header_item is None:
                header_item = QTableWidgetItem()
                self.table.setHorizontalHeaderItem(i, header_item)

            text = f"{column_name}{indicator}" if column_name in self.column_filters else column_name
            if header_item.text() != text:
                header_item.setText(text)

        if hasattr(self, "clear_filters_button"):
            self.clear_filters_button.setEnabled(self._has_active_filters())

    def refresh_table(self):
        sort_column = self.table.horizontalHeader().sortIndicatorSection()
        sort_order = self.table.horizontalHeader().sortIndicatorOrder()

        self.table.setRowCount(0)
        filtered_df = self._current_filtered_dataframe()

        color_map = self.get_row_color_map()
        status_column_index = self.table_headers.index("Status")

        for _, row in filtered_df.iterrows():
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            row_color_value = row.get("Zeilenfarbe", "Keine") if "Zeilenfarbe" in row else "Keine"
            if pd.isna(row_color_value) or row_color_value in ("", "nan"):
                row_color_value = "Keine"

            for j, value in enumerate(row):
                if pd.isna(value) or value in ("nan", ""):
                    item = QTableWidgetItem("")
                else:
                    item = QTableWidgetItem(str(value))

                if row_color_value in color_map:
                    item.setBackground(color_map[row_color_value])
                elif j == status_column_index:
                    if value == "Aktiv":
                        item.setBackground(QColor(200, 255, 200))
                    elif value == "Inaktiv":
                        item.setBackground(QColor(255, 200, 200))

                self.table.setItem(row_position, j, item)

        self.table.sortItems(sort_column, sort_order)

        total_count = len(self.df)
        self.total_count.setText(f"Datensätze: {total_count}")

        summary = core.build_status_summary(filtered_df, self.get_master_list("statuses"))
        if summary:
            parts = [f"{status}: {count}" for status, count in summary]
            self.status_summary.setText("Status: " + " | ".join(parts))
        else:
            self.status_summary.setText("Status: keine Daten")

        self._update_filter_ui_state()

    def show_add_dialog(self):
        dialog = DeviceDialog(parent=self)
        if dialog.exec_():
            new_row = dialog.get_values()
            self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
            self.save_data()
            self.refresh_table()

    def edit_selected_item(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warnung", "Bitte wählen Sie ein Gerät aus.")
            return

        row_index = selected_rows[0].row()
        device_id = self.table.item(row_index, 0).text()
        device_df_index = self.df[self.df["Gerätenummer"] == device_id].index[0]

        dialog = DeviceDialog(parent=self, edit_values=self.df.iloc[device_df_index].to_dict())

        if dialog.exec_():
            new_values = dialog.get_values()
            for key, value in new_values.items():
                self.df.at[device_df_index, key] = value

            self.save_data()
            self.refresh_table()

    def copy_selected_item(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warnung", "Bitte wählen Sie ein Gerät zum Kopieren aus.")
            return

        row_index = selected_rows[0].row()
        device_id = self.table.item(row_index, 0).text()
        device_df_index = self.df[self.df["Gerätenummer"] == device_id].index[0]

        copied_values = self.df.iloc[device_df_index].to_dict()
        copied_values["Gerätenummer"] = ""
        copied_values["Seriennummer"] = ""
        current_date = datetime.now().strftime("%Y-%m-%d")
        copied_values["Letzte_Aktualisierung"] = current_date

        dialog = DeviceDialog(parent=self, edit_values=copied_values)
        dialog.suggest_next_device_id()

        if dialog.exec_():
            new_row = dialog.get_values()
            self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
            self.save_data()
            self.refresh_table()

    def show_bulk_update_dialog(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warnung", "Bitte wählen Sie mindestens ein Gerät aus.")
            return

        selected_ids = []
        for model_index in selected_rows:
            item = self.table.item(model_index.row(), 0)
            if item:
                selected_ids.append(item.text())

        selected_ids = [device_id for device_id in selected_ids if device_id]
        if not selected_ids:
            QMessageBox.warning(self, "Warnung", "Konnte keine gültigen Gerätenummern ermitteln.")
            return

        dialog = BulkUpdateDialog(self, master_data=self.config.get("master_data"))
        if dialog.exec_():
            updates = dialog.get_updates()
            if not updates:
                QMessageBox.information(self, "Keine Änderungen", "Es wurden keine Felder zur Aktualisierung ausgewählt.")
                return

            mask = self.df["Gerätenummer"].astype(str).isin(selected_ids)
            updated_count = int(mask.sum())

            if updated_count == 0:
                QMessageBox.warning(self, "Warnung", "Keine der ausgewählten Geräte wurden gefunden.")
                return

            for column, value in updates.items():
                self.df.loc[mask, column] = value

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.df.loc[mask, "Letzte_Aktualisierung"] = timestamp

            self.save_data()
            self.refresh_table()

            QMessageBox.information(self, "Änderung abgeschlossen", f"{updated_count} Geräte wurden aktualisiert.")

    def export_data(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Daten exportieren", "", "CSV Dateien (*.csv)", options=options
        )

        if file_name:
            filtered_df = self._current_filtered_dataframe()
            filtered_df.to_csv(file_name, index=False, encoding="utf-8-sig")
            QMessageBox.information(self, "Export abgeschlossen", f"Daten wurden nach {file_name} exportiert.")

    def create_menu(self):
        menubar = self.menuBar()

        settings_action = QAction("Einstellungen", self)
        settings_action.triggered.connect(self.show_settings_dialog)
        menubar.addAction(settings_action)

        master_data_action = QAction("Stammdaten", self)
        master_data_action.triggered.connect(self.show_master_data_dialog)
        menubar.addAction(master_data_action)

        export_action = QAction("Exportieren", self)
        export_action.triggered.connect(self.export_data)
        menubar.addAction(export_action)

        exit_action = QAction("Beenden", self)
        exit_action.triggered.connect(self.close)
        menubar.addAction(exit_action)

    def show_settings_dialog(self):
        dialog = SettingsDialog(self)
        if dialog.exec_():
            new_csv_file = dialog.get_csv_path()

            if new_csv_file != self.csv_file:
                reply = QMessageBox.question(
                    self,
                    "Daten speichern?",
                    "Möchten Sie die aktuellen Daten speichern, bevor Sie zu einer anderen Datei wechseln?",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                )

                if reply == QMessageBox.Cancel:
                    return

                if reply == QMessageBox.Yes:
                    self.save_data()

                self.config["csv_file"] = new_csv_file
                self.save_config()

                self.load_data()
                self.refresh_table()

                self.setWindowTitle(f"Geräte-Inventarsystem - {os.path.basename(self.csv_file)}")

    def show_master_data_dialog(self):
        dialog = MasterDataDialog(self, self.config.get("master_data", {}))
        if dialog.exec_() == QDialog.Accepted:
            self.config["master_data"] = dialog.get_master_data()
            self.save_config()
            self._reload_status_filter()
            self.refresh_table()

    def _reload_status_filter(self):
        if not hasattr(self, "status_filter"):
            return

        current_value = self.status_filter.currentText()
        self.status_filter.blockSignals(True)
        self.status_filter.clear()
        self.status_filter.addItem("Alle")
        statuses = self.get_master_list("statuses")
        for status in statuses:
            self.status_filter.addItem(status)

        if current_value in statuses:
            self.status_filter.setCurrentText(current_value)
        else:
            self.status_filter.setCurrentIndex(0)

        self.status_filter.blockSignals(False)
