"""DataUpdateCoordinator for Howest Resto."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
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
from .helpers import parse_menu_date

_LOGGER = logging.getLogger(__name__)

type HowestRestoConfigEntry = ConfigEntry[HowestRestoCoordinator]

DAY_MAP: dict[int, str] = {
    1: "Ma",
    2: "Di",
    3: "Wo",
    4: "Do",
    5: "Vr",
}


@dataclass(slots=True)
class HowestRestoData:
    """Consolidated menu data for current and upcoming weeks."""

    current_week: WeeklyMenuResponse
    next_week: WeeklyMenuResponse | None = None
    days: list[DailyMenu] = field(default_factory=list)
    week: str = "current"


class HowestRestoCoordinator(DataUpdateCoordinator[HowestRestoData]):
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
        target_date = target_dt.date()
        target_abbr = DAY_MAP.get(target_dt.isoweekday())
        if not target_abbr:
            return None

        # 1. Primary match: exact parsed date
        for day_menu in self.data.days:
            parsed = parse_menu_date(day_menu.date)
            if parsed == target_date:
                return day_menu

        # 2. Fallback: match day abbreviation in current week
        if self.data.current_week and self.data.current_week.days:
            for day_menu in self.data.current_week.days:
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

    async def _async_update_data(self) -> HowestRestoData:
        """Fetch weekly menu from Howest website for current and next week."""
        try:
            current_week = await self.client.get_menu(
                campus=self.campus_code, week="current"
            )
        except CampusNotFoundError as err:
            raise ConfigEntryError(
                f"Campus {self.campus_code} is not recognized by Howest: {err}"
            ) from err
        except APIError as err:
            raise UpdateFailed(f"Error fetching Howest menu: {err}") from err

        next_week: WeeklyMenuResponse | None = None
        try:
            next_week = await self.client.get_menu(campus=self.campus_code, week="next")
        except Exception as exc:
            _LOGGER.debug(
                "Could not fetch next week's menu for campus %s: %s",
                self.campus_code,
                exc,
            )

        all_days: list[DailyMenu] = list(current_week.days)
        if next_week and next_week.days:
            all_days.extend(next_week.days)

        return HowestRestoData(
            current_week=current_week,
            next_week=next_week,
            days=all_days,
            week=current_week.week,
        )
