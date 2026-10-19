"""Tests for the Howest Resto sensor platform."""

from __future__ import annotations

from unittest.mock import AsyncMock

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.howest_resto.const import (
    CONF_CAMPUS,
    CONF_LANGUAGE,
    CONF_SCAN_INTERVAL,
    DOMAIN,
)


async def test_sensors_created(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_client: AsyncMock,
) -> None:
    """Test sensors are created and have correct state and attributes."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Verify today & tomorrow sensors exist
    today_state = hass.states.get("sensor.howest_resto_t_obeetje_today_s_menu")
    assert today_state is not None
    assert today_state.attributes["campus"] == "GKG"
    assert today_state.attributes["campus_name"] == "'t Obeetje"
    assert "days" in today_state.attributes
    assert len(today_state.attributes["days"]) == 5

    tomorrow_state = hass.states.get("sensor.howest_resto_t_obeetje_tomorrow_s_menu")
    assert tomorrow_state is not None
    assert tomorrow_state.attributes["campus"] == "GKG"

    # Verify redundant weekly sensor is removed
    assert hass.states.get("sensor.howest_resto_t_obeetje_weekly_menu") is None


async def test_sensor_english_language(
    hass: HomeAssistant,
    mock_client: AsyncMock,
) -> None:
    """Test sensor with english language option."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Howest Resto - 't Obeetje (Kortrijk)",
        data={CONF_CAMPUS: "GKG"},
        options={CONF_SCAN_INTERVAL: 60, CONF_LANGUAGE: "english"},
        unique_id="howest_resto_gkg",
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    today_state = hass.states.get("sensor.howest_resto_t_obeetje_today_s_menu")
    assert today_state is not None
    assert "days" in today_state.attributes
