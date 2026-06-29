"""Persistenzschicht für die Inventardaten.

Kapselt das Laden und Speichern der CSV-Datei, damit die Oberfläche
(``InventoryManager``) nichts über das Dateiformat wissen muss.
"""

from __future__ import annotations

import os
import tempfile

import pandas as pd

from inventory_app.constants import COLUMNS


class InventoryRepository:
    """Lädt und speichert den Gerätebestand als CSV-Datei."""

    def __init__(self, csv_file: str):
        self.csv_file = csv_file

    def exists(self) -> bool:
        return os.path.exists(self.csv_file)

    def load(self) -> pd.DataFrame:
        """Liest die CSV-Datei und richtet sie am kanonischen Schema aus.

        Fehlende Spalten werden ergänzt, nicht mehr genutzte (z. B. das alte
        ``Kommentar``) verworfen. Existiert noch keine Datei, wird eine leere
        Tabelle angelegt und gespeichert.
        """
        if self.exists():
            df = pd.read_csv(
                self.csv_file,
                dtype=str,
                encoding="utf-8-sig",
                keep_default_na=False,
            ).fillna("")
            return df.reindex(columns=COLUMNS, fill_value="")

        df = pd.DataFrame(columns=COLUMNS)
        self.save(df)
        return df

    def save(self, df: pd.DataFrame) -> None:
        target_dir = os.path.dirname(os.path.abspath(self.csv_file))
        os.makedirs(target_dir, exist_ok=True)

        normalized_df = df.reindex(columns=COLUMNS, fill_value="").fillna("")
        fd, temp_path = tempfile.mkstemp(prefix=".inventory-", suffix=".csv", dir=target_dir)
        try:
            with os.fdopen(fd, "w", encoding="utf-8-sig", newline="") as temp_file:
                normalized_df.to_csv(temp_file, index=False, na_rep="")
            os.replace(temp_path, self.csv_file)
        except Exception:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            raise
