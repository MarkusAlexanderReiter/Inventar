import copy

DEFAULT_MASTER_DATA = {
    "device_types": [
        "PC",
        "Laptop",
        "Monitor",
        "Drucker",
        "Scanner",
        "Telefon",
        "Diensthandy",
        "Router",
        "Server",
        "Sonstiges",
    ],
    "locations": ["Hauptsitz", "Niederlassung", "Außenlager"],
    "offices": ["Büro 1", "Büro 2", "Büro 3", "Serverraum"],
    "users": [],
    "conditions": ["Neu", "Sehr gut", "Gut", "Akzeptabel", "Schlecht", "Defekt"],
    "statuses": ["Aktiv", "Inaktiv"],
    "row_colors": [
        {"name": "Gelb", "color": "#fffac8"},
        {"name": "Orange", "color": "#ffdcb4"},
        {"name": "Rot", "color": "#ffc8c8"},
        {"name": "Grün", "color": "#c8ffd0"},
        {"name": "Blau", "color": "#c8dcff"},
        {"name": "Lila", "color": "#e6c8ff"},
    ],
    "numbering": {"prefix": "IT", "separator": "-", "padding": 4, "start": 1},
}

# Canonical column schema for the inventory table and CSV storage.
# Defined once here so the data layer and the UI never drift apart.
COLUMNS = [
    "Gerätenummer",
    "Gerätetyp",
    "Marke",
    "Modell",
    "Seriennummer",
    "Zugewiesener_Benutzer",
    "Standort",
    "Büro",
    "Kaufdatum",
    "Zustand",
    "Status",
    "Anmerkung",
    "Zeilenfarbe",
    "Letzte_Aktualisierung",
]


def get_default_master_data():
    """Provide a deep copy so callers can mutate safely."""
    return copy.deepcopy(DEFAULT_MASTER_DATA)
