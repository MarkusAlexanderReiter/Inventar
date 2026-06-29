"""Unit-Tests für die reine Logik in ``inventory_app.core``."""

import pandas as pd
import pytest

from inventory_app import core

DEFAULT_NUMBERING = {"prefix": "IT", "separator": "-", "padding": 4, "start": 1}


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        [
            {"Gerätenummer": "IT-0001", "Gerätetyp": "Laptop", "Standort": "Hauptsitz", "Status": "Aktiv"},
            {"Gerätenummer": "IT-0002", "Gerätetyp": "Monitor", "Standort": "Hauptsitz", "Status": "Aktiv"},
            {"Gerätenummer": "IT-0003", "Gerätetyp": "Server", "Standort": "Außenlager", "Status": "Inaktiv"},
            {"Gerätenummer": "IT-0004", "Gerätetyp": "Laptop", "Standort": "Niederlassung", "Status": "Defekt"},
        ]
    )


# --- generate_next_device_id -------------------------------------------------

def test_next_id_uses_start_value_when_empty():
    assert core.generate_next_device_id([], DEFAULT_NUMBERING) == "IT-0001"


def test_next_id_respects_custom_start():
    numbering = {**DEFAULT_NUMBERING, "start": 100}
    assert core.generate_next_device_id([], numbering) == "IT-0100"


def test_next_id_continues_from_highest():
    assert core.generate_next_device_id(["IT-0001", "IT-0009", "IT-0003"], DEFAULT_NUMBERING) == "IT-0010"


def test_next_id_ignores_foreign_prefixes():
    assert core.generate_next_device_id(["PC-0050", "IT-0002"], DEFAULT_NUMBERING) == "IT-0003"


def test_next_id_honors_custom_prefix_separator_padding():
    numbering = {"prefix": "FW", "separator": "/", "padding": 2, "start": 1}
    assert core.generate_next_device_id(["FW/01", "FW/04"], numbering) == "FW/05"


def test_next_id_ignores_non_numeric_suffix():
    assert core.generate_next_device_id(["IT-ABC", "IT-0005"], DEFAULT_NUMBERING) == "IT-0006"


# --- filter_dataframe --------------------------------------------------------

def test_filter_no_criteria_returns_all(sample_df):
    assert len(core.filter_dataframe(sample_df)) == 4


def test_filter_by_status(sample_df):
    result = core.filter_dataframe(sample_df, status="Aktiv")
    assert list(result["Gerätenummer"]) == ["IT-0001", "IT-0002"]


def test_filter_search_all_fields_is_case_insensitive(sample_df):
    result = core.filter_dataframe(sample_df, search_text="server")
    assert list(result["Gerätenummer"]) == ["IT-0003"]


def test_filter_search_specific_field(sample_df):
    result = core.filter_dataframe(sample_df, search_text="Laptop", search_field="Gerätetyp")
    assert list(result["Gerätenummer"]) == ["IT-0001", "IT-0004"]


def test_filter_search_is_literal_not_regex(sample_df):
    # A bare "(" would raise if the search were treated as a regex.
    assert len(core.filter_dataframe(sample_df, search_text="(")) == 0


def test_filter_by_column_values(sample_df):
    result = core.filter_dataframe(sample_df, column_filters={"Standort": {"Hauptsitz"}})
    assert list(result["Gerätenummer"]) == ["IT-0001", "IT-0002"]


def test_filter_combines_criteria(sample_df):
    result = core.filter_dataframe(
        sample_df,
        status="Aktiv",
        column_filters={"Gerätetyp": {"Laptop"}},
    )
    assert list(result["Gerätenummer"]) == ["IT-0001"]


def test_filter_unknown_column_is_ignored(sample_df):
    assert len(core.filter_dataframe(sample_df, column_filters={"GibtEsNicht": {"x"}})) == 4


# --- build_status_summary ----------------------------------------------------

def test_status_summary_orders_known_statuses_first(sample_df):
    summary = core.build_status_summary(sample_df, ["Aktiv", "Inaktiv"])
    # Known statuses (in master-data order) come first, then any extra value found.
    assert summary[:2] == [("Aktiv", 2), ("Inaktiv", 1)]
    assert ("Defekt", 1) in summary


def test_status_summary_reports_zero_for_unused_status(sample_df):
    summary = dict(core.build_status_summary(sample_df, ["Aktiv", "Ausgemustert"]))
    assert summary["Ausgemustert"] == 0


def test_status_summary_empty_dataframe():
    empty = pd.DataFrame(columns=["Status"])
    assert core.build_status_summary(empty, ["Aktiv"]) == [("Aktiv", 0)]
