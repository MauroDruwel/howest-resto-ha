"""Constants for the Howest Resto integration."""

from __future__ import annotations

DOMAIN = "howest_resto"

CONF_CAMPUS = "campus"
CONF_CAMPUS_NAME = "campus_name"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_LANGUAGE = "language"

DEFAULT_SCAN_INTERVAL = 60  # minutes
DEFAULT_CAMPUS = "GKG"
DEFAULT_LANGUAGE = "dutch"

LANGUAGE_OPTIONS = ["dutch", "english", "both"]

CAMPUS_OPTIONS: dict[str, str] = {
    "GKG": "'t Obeetje (Graaf Karel de Goedelaan 5, Kortrijk)",
    "PENTA": "Plaza (Sint-Martens-Latemlaan 1B, Kortrijk)",
    "RSS": "YUM (Rijselstraat 5, Brugge)",
    "RSS1": "DAD (Spoorwegstraat 4, Brugge)",
    "SIC": "BSI (Nijverheidsstraat 112, Brugge)",
    "TS": "The Square (Luipaardstraat 12A, Kortrijk)",
}

CAMPUS_NAMES: dict[str, str] = {
    "GKG": "'t Obeetje",
    "PENTA": "Plaza",
    "RSS": "YUM",
    "RSS1": "DAD",
    "SIC": "BSI",
    "TS": "The Square",
}

CAMPUS_CITIES: dict[str, str] = {
    "GKG": "Kortrijk",
    "PENTA": "Kortrijk",
    "RSS": "Brugge",
    "RSS1": "Brugge",
    "SIC": "Brugge",
    "TS": "Kortrijk",
}

ATTR_CAMPUS = "campus"
ATTR_CAMPUS_NAME = "campus_name"
ATTR_DATE = "date"
ATTR_DAY = "day"
ATTR_DISHES = "dishes"
ATTR_DUTCH_DISHES = "dutch_dishes"
ATTR_ENGLISH_DISHES = "english_dishes"
ATTR_WEEK = "week"
ATTR_DAYS = "days"
