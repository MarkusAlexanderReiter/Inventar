"""Tests für die Persistenzschicht ``InventoryRepository``."""

import pandas as pd

from inventory_app.constants import COLUMNS
from inventory_app.repository import InventoryRepository


def test_load_creates_empty_file_when_missing(tmp_path):
    csv_path = tmp_path / "inventory.csv"
    repo = InventoryRepository(str(csv_path))

    df = repo.load()

    assert csv_path.exists()
    assert list(df.columns) == COLUMNS
    assert df.empty


def test_save_then_load_roundtrip(tmp_path):
    csv_path = tmp_path / "inventory.csv"
    repo = InventoryRepository(str(csv_path))

    df = pd.DataFrame([{column: "" for column in COLUMNS}])
    df.loc[0, "Gerätenummer"] = "IT-0001"
    df.loc[0, "Status"] = "Aktiv"
    repo.save(df)

    loaded = repo.load()
    assert loaded.loc[0, "Gerätenummer"] == "IT-0001"
    assert loaded.loc[0, "Status"] == "Aktiv"


def test_load_aligns_to_schema_dropping_unknown_columns(tmp_path):
    csv_path = tmp_path / "legacy.csv"
    # A legacy file that still carries the removed "Kommentar" column and
    # is missing a current one ("Zeilenfarbe").
    legacy = pd.DataFrame(
        [{"Gerätenummer": "IT-0001", "Status": "Aktiv", "Kommentar": "alt", "Anmerkung": "x"}]
    )
    legacy.to_csv(csv_path, index=False)

    loaded = InventoryRepository(str(csv_path)).load()

    assert list(loaded.columns) == COLUMNS
    assert "Kommentar" not in loaded.columns
    assert loaded.loc[0, "Zeilenfarbe"] == ""
    assert loaded.loc[0, "Anmerkung"] == "x"


def test_load_preserves_string_values(tmp_path):
    csv_path = tmp_path / "inventory.csv"
    csv_path.write_text(
        "Gerätenummer,Seriennummer,Status\n"
        "IT-0001,000123,Aktiv\n",
        encoding="utf-8",
    )

    loaded = InventoryRepository(str(csv_path)).load()

    assert loaded.loc[0, "Gerätenummer"] == "IT-0001"
    assert loaded.loc[0, "Seriennummer"] == "000123"


def test_save_normalizes_schema(tmp_path):
    csv_path = tmp_path / "inventory.csv"
    repo = InventoryRepository(str(csv_path))
    df = pd.DataFrame(
        [
            {
                "Gerätenummer": "IT-0001",
                "Status": "Aktiv",
                "NichtMehrGenutzt": "soll nicht gespeichert werden",
            }
        ]
    )

    repo.save(df)
    loaded = pd.read_csv(csv_path, dtype=str, encoding="utf-8-sig", keep_default_na=False)

    assert list(loaded.columns) == COLUMNS
    assert "NichtMehrGenutzt" not in loaded.columns
    assert loaded.loc[0, "Gerätenummer"] == "IT-0001"
