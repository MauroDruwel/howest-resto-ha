"""Config flow for Howest Resto integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback

from howest_resto import AsyncHowestRestoClient
from howest_resto.exceptions import APIError, CampusNotFoundError

from .const import (
    CAMPUS_CITIES,
    CAMPUS_NAMES,
    CAMPUS_OPTIONS,
    CONF_CAMPUS,
    CONF_LANGUAGE,
    CONF_SCAN_INTERVAL,
    DEFAULT_CAMPUS,
    DEFAULT_LANGUAGE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LANGUAGE_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)


class HowestRestoConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Howest Resto."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            campus = user_input[CONF_CAMPUS]
            unique_id = f"howest_resto_{campus.lower()}"

            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            client = AsyncHowestRestoClient()
            try:
                await client.get_menu(campus=campus)
            except CampusNotFoundError:
                errors["base"] = "invalid_campus"
            except APIError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception while validating Howest campus")
                errors["base"] = "unknown"
            else:
                resto_name = CAMPUS_NAMES.get(campus, campus)
                city = CAMPUS_CITIES.get(campus, "")
                title = f"Howest Resto - {resto_name} ({city})"
                return self.async_create_entry(title=title, data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_CAMPUS, default=DEFAULT_CAMPUS): vol.In(
                    CAMPUS_OPTIONS
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return HowestRestoOptionsFlowHandler(config_entry)


class HowestRestoOptionsFlowHandler(OptionsFlow):
    """Handle options flow for Howest Resto."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self._config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        current_language = self._config_entry.options.get(
            CONF_LANGUAGE, DEFAULT_LANGUAGE
        )

        schema = vol.Schema(
            {
                vol.Optional(CONF_SCAN_INTERVAL, default=current_interval): vol.All(
                    vol.Coerce(int), vol.Range(min=15, max=1440)
                ),
                vol.Optional(CONF_LANGUAGE, default=current_language): vol.In(
                    LANGUAGE_OPTIONS
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
