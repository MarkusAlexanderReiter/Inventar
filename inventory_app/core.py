"""Reine Daten- und Filterlogik – bewusst ohne Qt-Abhängigkeiten.

Diese Funktionen kapseln die Geschäftslogik (Filtern, Nummernkreis,
Statusübersicht), damit sie unabhängig von der Oberfläche getestet und
sowohl von der Tabellenansicht als auch vom Export genutzt werden können.
"""

from __future__ import annotations

from typing import Iterable, Mapping

import pandas as pd

ALL_FIELDS = "Alle Felder"
ALL_STATUSES = "Alle"


def generate_next_device_id(existing_ids: Iterable[str], numbering: Mapping) -> str:
    """Ermittelt die nächste freie Gerätenummer für den konfigurierten Nummernkreis.

    Es wird die höchste vorhandene Nummer mit passendem Präfix fortgezählt;
    sind keine passenden Nummern vorhanden, wird der konfigurierte Startwert
    verwendet.
    """
    prefix = numbering.get("prefix", "IT") or ""
    separator = numbering.get("separator", "-") or ""
    padding = max(1, int(numbering.get("padding", 4)))
    start_value = max(1, int(numbering.get("start", 1)))

    prefix_full = f"{prefix}{separator}"
    numbers = []
    for device_id in existing_ids:
        device_id = str(device_id)
        if device_id.startswith(prefix_full):
            suffix = device_id[len(prefix_full):]
            if suffix.isdigit():
                numbers.append(int(suffix))

    next_number = max(numbers) + 1 if numbers else start_value
    return f"{prefix_full}{str(next_number).zfill(padding)}"


def filter_dataframe(
    df: pd.DataFrame,
    *,
    status: str = ALL_STATUSES,
    search_text: str = "",
    search_field: str = ALL_FIELDS,
    column_filters: Mapping[str, Iterable] | None = None,
) -> pd.DataFrame:
    """Wendet Status-, Volltext- und Spaltenfilter auf einen DataFrame an.

    Die Volltextsuche ist bewusst eine reine Teilstring-Suche (kein RegEx),
    damit Sonderzeichen im Suchbegriff nicht zu Fehlern führen.
    """
    result = df

    if status and status != ALL_STATUSES and "Status" in result.columns:
        result = result[result["Status"] == status]

    needle = (search_text or "").strip().lower()
    if needle:
        if search_field in (ALL_FIELDS, "", None):
            mask = (
                result.astype(str)
                .apply(lambda col: col.str.lower().str.contains(needle, regex=False))
                .any(axis=1)
            )
        elif search_field in result.columns:
            mask = result[search_field].astype(str).str.lower().str.contains(needle, regex=False)
        else:
            mask = pd.Series(True, index=result.index)
        result = result[mask]

    for column_name, allowed in (column_filters or {}).items():
        if column_name not in result.columns:
            continue
        allowed_values = {str(value) for value in allowed}
        series = result[column_name].fillna("").astype(str)
        result = result[series.isin(allowed_values)]

    return result


def build_status_summary(df: pd.DataFrame, master_statuses: Iterable[str]) -> list[tuple[str, int]]:
    """Zählt Geräte je Status; bekannte Stammdaten-Status zuerst, dann unbekannte."""
    master_statuses = list(master_statuses)
    if "Status" not in df.columns:
        return [(status, 0) for status in master_statuses]

    counts = df["Status"].value_counts()
    summary = [(status, int(counts.get(status, 0))) for status in master_statuses]

    known = set(master_statuses)
    for status, count in counts.items():
        if status not in known:
            summary.append((str(status), int(count)))

    return summary
