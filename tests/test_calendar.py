"""Tests for the Howest Resto calendar platform."""

from __future__ import annotations

import datetime
from unittest.mock import AsyncMock

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.howest_resto.calendar import HowestRestoCalendar


async def test_calendar_created_and_events(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_client: AsyncMock,
) -> None:
    """Test calendar entity is created and returns events for menu days."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    calendar_state = hass.states.get("calendar.howest_resto_t_obeetje_menu_calendar")
    assert calendar_state is not None

    coordinator = mock_config_entry.runtime_data
    calendar_entity = HowestRestoCalendar(coordinator, mock_config_entry)

    start_date = dt_util.as_utc(datetime.datetime(2026, 10, 19, 0, 0, 0))
    end_date = dt_util.as_utc(datetime.datetime(2026, 10, 23, 23, 59, 59))

    events = await calendar_entity.async_get_events(hass, start_date, end_date)
    assert len(events) == 5

    monday_event = events[0]
    assert "Tomatensoep" in monday_event.summary
    assert "Vol-au-vent met frietjes" in monday_event.summary
    assert "Graaf Karel de Goedelaan 5, Kortrijk" in monday_event.location
    assert monday_event.start == datetime.date(2026, 10, 19)
    assert monday_event.end == datetime.date(2026, 10, 20)


def test_parse_menu_date() -> None:
    """Test date parsing logic for Dutch month names and various delimiters."""
    from custom_components.howest_resto.calendar import _parse_menu_date

    # Dutch text month without year
    d1 = _parse_menu_date("19 oktober")
    assert d1 is not None
    assert d1.day == 19
    assert d1.month == 10

    # Dutch text month with explicit year
    d2 = _parse_menu_date("23 oktober 2026")
    assert d2 == datetime.date(2026, 10, 23)

    # Short Dutch month abbreviation
    d3 = _parse_menu_date("5 mrt 2026")
    assert d3 == datetime.date(2026, 3, 5)

    # Slashes
    d4 = _parse_menu_date("19/10/2026")
    assert d4 == datetime.date(2026, 10, 19)

    # Hyphens
    d5 = _parse_menu_date("2026-10-19")
    assert d5 == datetime.date(2026, 10, 19)

    # Invalid / empty
    assert _parse_menu_date("") is None
    assert _parse_menu_date("invalid date") is None
