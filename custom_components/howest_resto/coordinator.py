"""DataUpdateCoordinator for Howest Resto."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from howest_resto import AsyncHowestRestoClient
from howest_resto.exceptions import APIError, CampusNotFoundError
from howest_resto.models import DailyMenu, WeeklyMenuResponse

from .const import (
    CAMPUS_CITIES,
    CAMPUS_NAMES,
    CAMPUS_OPTIONS,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

type HowestRestoConfigEntry = ConfigEntry[HowestRestoCoordinator]

DAY_MAP: dict[int, str] = {
    1: "Ma",
    2: "Di",
    3: "Wo",
    4: "Do",
    5: "Vr",
}


class HowestRestoCoordinator(DataUpdateCoordinator[WeeklyMenuResponse]):
    """Class to manage fetching Howest Resto menu data."""

    config_entry: HowestRestoConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: HowestRestoConfigEntry,
        client: AsyncHowestRestoClient,
        campus_code: str,
    ) -> None:
        """Initialize coordinator."""
        self.client = client
        self.campus_code = campus_code

        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_{campus_code.lower()}",
            update_interval=timedelta(minutes=scan_interval),
        )

    @property
    def campus_name(self) -> str:
        """Return short restaurant name."""
        return CAMPUS_NAMES.get(self.campus_code, self.campus_code)

    @property
    def campus_full_name(self) -> str:
        """Return full campus name with address."""
        return CAMPUS_OPTIONS.get(self.campus_code, self.campus_code)

    @property
    def city(self) -> str:
        """Return campus city."""
        return CAMPUS_CITIES.get(self.campus_code, "")

    def get_daily_menu_for_offset(self, day_offset: int = 0) -> DailyMenu | None:
        """Return daily menu for a specific day offset from today (0 = today, 1 = tomorrow)."""
        if not self.data or not self.data.days:
            return None

        target_dt = dt_util.now() + timedelta(days=day_offset)
        target_abbr = DAY_MAP.get(target_dt.isoweekday())
        if not target_abbr:
            return None

        # Primary match by day abbreviation (Ma, Di, Wo, Do, Vr)
        for day_menu in self.data.days:
            if day_menu.day == target_abbr:
                return day_menu

        return None

    @property
    def today_menu(self) -> DailyMenu | None:
        """Return today's menu if available."""
        return self.get_daily_menu_for_offset(0)

    @property
    def tomorrow_menu(self) -> DailyMenu | None:
        """Return tomorrow's menu if available."""
        return self.get_daily_menu_for_offset(1)

    async def _async_update_data(self) -> WeeklyMenuResponse:
        """Fetch weekly menu from Howest website."""
        try:
            return await self.client.get_menu(campus=self.campus_code)
        except CampusNotFoundError as err:
            raise ConfigEntryError(
                f"Campus {self.campus_code} is not recognized by Howest: {err}"
            ) from err
        except APIError as err:
            raise UpdateFailed(f"Error fetching Howest menu: {err}") from err
