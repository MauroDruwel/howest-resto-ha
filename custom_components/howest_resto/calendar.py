"""Calendar platform for Howest Resto."""

from __future__ import annotations

import datetime

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from howest_resto.models import DailyMenu

from .const import DOMAIN
from .coordinator import HowestRestoConfigEntry, HowestRestoCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HowestRestoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Howest Resto calendar entity based on a config entry."""
    coordinator = entry.runtime_data
    async_add_entities([HowestRestoCalendar(coordinator, entry)])


def _parse_menu_date(raw_date: str) -> datetime.date | None:
    """Parse Howest menu date string into datetime.date."""
    if not raw_date:
        return None
    try:
        parts = raw_date.strip().split("/")
        if len(parts) == 3:
            return datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))
        if len(parts) == 2:
            return datetime.date(dt_util.now().year, int(parts[1]), int(parts[0]))
    except (ValueError, IndexError):
        return None
    return None


class HowestRestoCalendar(CoordinatorEntity[HowestRestoCoordinator], CalendarEntity):
    """Calendar entity displaying Howest student restaurant menus."""

    _attr_has_entity_name = True
    _attr_translation_key = "menu_calendar"
    _attr_icon = "mdi:food-fork-drink"

    def __init__(
        self,
        coordinator: HowestRestoCoordinator,
        entry: HowestRestoConfigEntry,
    ) -> None:
        """Initialize the calendar entity."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = (
            f"howest_resto_{coordinator.campus_code.lower()}_calendar"
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.campus_code.lower())},
            name=f"Howest Resto {self.coordinator.campus_name}",
            manufacturer="Howest",
            model=self.coordinator.campus_full_name,
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://resto.howest.be/MenuWeekly.aspx",
        )

    def _menu_to_event(self, daily: DailyMenu) -> CalendarEvent | None:
        """Convert a DailyMenu to a CalendarEvent."""
        event_date = _parse_menu_date(daily.date)
        if not event_date or (not daily.dutch_dishes and not daily.all_raw_items):
            return None

        dish_summary = (
            ", ".join(daily.dutch_dishes)
            if daily.dutch_dishes
            else ", ".join(daily.all_raw_items)
        )
        desc_lines = [f"Campus: {self.coordinator.campus_full_name}", ""]
        if daily.dutch_dishes:
            desc_lines.append("Menu (NL):")
            for dish in daily.dutch_dishes:
                desc_lines.append(f"  • {dish}")
        if daily.english_dishes:
            desc_lines.append("")
            desc_lines.append("Menu (EN):")
            for dish in daily.english_dishes:
                desc_lines.append(f"  • {dish}")

        return CalendarEvent(
            start=event_date,
            end=event_date + datetime.timedelta(days=1),
            summary=f"🍽️ {self.coordinator.campus_name}: {dish_summary}",
            description="\n".join(desc_lines),
            location=self.coordinator.campus_full_name,
        )

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming calendar event."""
        if not self.coordinator.data or not self.coordinator.data.days:
            return None

        today = dt_util.now().date()
        for daily in self.coordinator.data.days:
            event_date = _parse_menu_date(daily.date)
            if event_date and event_date >= today:
                return self._menu_to_event(daily)

        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        events: list[CalendarEvent] = []
        if not self.coordinator.data or not self.coordinator.data.days:
            return events

        start_d = start_date.date()
        end_d = end_date.date()

        for daily in self.coordinator.data.days:
            event_date = _parse_menu_date(daily.date)
            if event_date and start_d <= event_date <= end_d:
                ev = self._menu_to_event(daily)
                if ev:
                    events.append(ev)

        return events
