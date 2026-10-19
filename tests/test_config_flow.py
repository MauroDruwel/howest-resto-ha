"""Tests for the Howest Resto config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock

from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from howest_resto.exceptions import APIError, CampusNotFoundError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.howest_resto.const import (
    CONF_CAMPUS,
    CONF_LANGUAGE,
    CONF_SCAN_INTERVAL,
    DOMAIN,
)


async def test_flow_user_success(hass: HomeAssistant, mock_client: AsyncMock) -> None:
    """Test successful user step creating a config entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_CAMPUS: "GKG"},
    )
    assert result2["type"] is FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Howest Resto - 't Obeetje (Kortrijk)"
    assert result2["data"][CONF_CAMPUS] == "GKG"
    assert result2["result"].unique_id == "howest_resto_gkg"


async def test_flow_user_cannot_connect(
    hass: HomeAssistant, mock_client: AsyncMock
) -> None:
    """Test handling of connection error during validation."""
    mock_client.get_menu.side_effect = APIError("Network down")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_CAMPUS: "GKG"},
    )
    assert result2["type"] is FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_flow_user_invalid_campus(
    hass: HomeAssistant, mock_client: AsyncMock
) -> None:
    """Test handling of invalid campus error during validation."""
    mock_client.get_menu.side_effect = CampusNotFoundError("Unknown campus")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_CAMPUS: "GKG"},
    )
    assert result2["type"] is FlowResultType.FORM
    assert result2["errors"] == {"base": "invalid_campus"}


async def test_flow_user_already_configured(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_client: AsyncMock
) -> None:
    """Test abort when campus is already configured."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_CAMPUS: "GKG"},
    )
    assert result2["type"] is FlowResultType.ABORT
    assert result2["reason"] == "already_configured"


async def test_options_flow(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test options flow to update scan interval and language."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_SCAN_INTERVAL: 120,
            CONF_LANGUAGE: "english",
        },
    )
    assert result2["type"] is FlowResultType.CREATE_ENTRY
    assert mock_config_entry.options[CONF_SCAN_INTERVAL] == 120
    assert mock_config_entry.options[CONF_LANGUAGE] == "english"
