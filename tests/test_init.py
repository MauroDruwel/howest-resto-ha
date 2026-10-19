"""Tests for the Howest Resto integration setup and unload."""

from __future__ import annotations

from unittest.mock import AsyncMock

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from howest_resto.exceptions import APIError
from pytest_homeassistant_custom_component.common import MockConfigEntry


async def test_setup_and_unload_entry(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_client: AsyncMock,
) -> None:
    """Test successful setup and unload of the config entry."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert mock_config_entry.runtime_data is not None

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED


async def test_setup_entry_network_failure(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_client: AsyncMock,
) -> None:
    """Test setup retries when network fails during initial refresh."""
    mock_client.get_menu.side_effect = APIError("Temporary connection failure")
    mock_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY
