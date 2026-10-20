"""Helpers and utilities for Howest Resto."""

from __future__ import annotations

import datetime
import re

from homeassistant.util import dt as dt_util

DUTCH_MONTHS: dict[str, int] = {
    "januari": 1,
    "jan": 1,
    "january": 1,
    "februari": 2,
    "feb": 2,
    "february": 2,
    "maart": 3,
    "mrt": 3,
    "mar": 3,
    "march": 3,
    "april": 4,
    "apr": 4,
    "mei": 5,
    "may": 5,
    "juni": 6,
    "jun": 6,
    "june": 6,
    "juli": 7,
    "jul": 7,
    "july": 7,
    "augustus": 8,
    "aug": 8,
    "august": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "oktober": 10,
    "okt": 10,
    "oct": 10,
    "october": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}


def parse_menu_date(raw_date: str) -> datetime.date | None:
    """Parse Howest menu date string into datetime.date.

    Supports Dutch text dates (e.g. '19 oktober', '19 oktober 2026')
    as well as delimiter-separated formats (e.g. '19/10/2026', '19-10', '2026-10-19').
    """
    if not raw_date:
        return None

    cleaned = raw_date.strip().lower()

    # 1. Text month: '19 oktober' or '19 oktober 2026'
    match = re.match(r"^(\d{1,2})\s+([a-zA-Z]+)(?:\s+(\d{4}))?$", cleaned)
    if match:
        day = int(match.group(1))
        month = DUTCH_MONTHS.get(match.group(2))
        if not month:
            return None

        now = dt_util.now()
        year = int(match.group(3)) if match.group(3) else now.year
        if not match.group(3):
            if now.month == 12 and month == 1:
                year += 1
            elif now.month == 1 and month == 12:
                year -= 1

        try:
            return datetime.date(year, month, day)
        except ValueError:
            return None

    # 2. Delimiter separated ('19/10/2026', '19/10', '2026-10-19')
    for sep in ("/", "-", "."):
        if sep in cleaned:
            parts = cleaned.split(sep)
            try:
                if len(parts) == 3:
                    if len(parts[0]) == 4:
                        return datetime.date(
                            int(parts[0]), int(parts[1]), int(parts[2])
                        )
                    return datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))
                if len(parts) == 2:
                    return datetime.date(
                        dt_util.now().year, int(parts[1]), int(parts[0])
                    )
            except (ValueError, IndexError):
                return None

    return None
