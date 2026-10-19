"""Sensor platform for Howest Resto."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from howest_resto.models import DailyMenu

from .const import (
    ATTR_CAMPUS,
    ATTR_CAMPUS_NAME,
    ATTR_DATE,
    ATTR_DAY,
    ATTR_DAYS,
    ATTR_DISHES,
    ATTR_DUTCH_DISHES,
    ATTR_ENGLISH_DISHES,
    ATTR_WEEK,
    CONF_LANGUAGE,
    DEFAULT_LANGUAGE,
    DOMAIN,
)
from .coordinator import HowestRestoConfigEntry, HowestRestoCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HowestRestoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Howest Resto sensor entities based on a config entry."""
    coordinator = entry.runtime_data

    async_add_entities(
        [
            HowestRestoTodaySensor(coordinator, entry),
            HowestRestoTomorrowSensor(coordinator, entry),
        ]
    )


class HowestRestoBaseSensor(CoordinatorEntity[HowestRestoCoordinator], SensorEntity):
    """Base class for Howest Resto sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HowestRestoCoordinator,
        entry: HowestRestoConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entry = entry

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

    def _format_dish_state(self, daily: DailyMenu | None) -> str:
        """Format the sensor state according to language preference."""
        if not daily or (not daily.dutch_dishes and not daily.all_raw_items):
            return "Closed"

        lang = self.entry.options.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
        if lang == "dutch" and daily.dutch_dishes:
            return ", ".join(daily.dutch_dishes)
        if lang == "english" and daily.english_dishes:
            return ", ".join(daily.english_dishes)
        return ", ".join(daily.all_raw_items or daily.dutch_dishes)


class HowestRestoTodaySensor(HowestRestoBaseSensor):
    """Sensor for today's lunch menu."""

    _attr_translation_key = "today_menu"
    _attr_icon = "mdi:silverware-fork-knife"

    def __init__(
        self,
        coordinator: HowestRestoCoordinator,
        entry: HowestRestoConfigEntry,
    ) -> None:
        """Initialize today sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"howest_resto_{coordinator.campus_code.lower()}_today"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return self._format_dish_state(self.coordinator.today_menu)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        attrs: dict[str, Any] = {
            ATTR_CAMPUS: self.coordinator.campus_code,
            ATTR_CAMPUS_NAME: self.coordinator.campus_name,
            ATTR_WEEK: self.coordinator.data.week
            if self.coordinator.data
            else "current",
        }
        today = self.coordinator.today_menu
        if today:
            attrs.update(
                {
                    ATTR_DATE: today.date,
                    ATTR_DAY: today.day,
                    ATTR_DISHES: today.all_raw_items or today.dutch_dishes,
                    ATTR_DUTCH_DISHES: today.dutch_dishes,
                    ATTR_ENGLISH_DISHES: today.english_dishes,
                }
            )
        if self.coordinator.data and self.coordinator.data.days:
            attrs[ATTR_DAYS] = [
                {
                    ATTR_DATE: d.date,
                    ATTR_DAY: d.day,
                    ATTR_DISHES: d.all_raw_items or d.dutch_dishes,
                    ATTR_DUTCH_DISHES: d.dutch_dishes,
                    ATTR_ENGLISH_DISHES: d.english_dishes,
                }
                for d in self.coordinator.data.days
            ]
        return attrs


class HowestRestoTomorrowSensor(HowestRestoBaseSensor):
    """Sensor for tomorrow's lunch menu."""

    _attr_translation_key = "tomorrow_menu"
    _attr_icon = "mdi:calendar-arrow-right"

    def __init__(
        self,
        coordinator: HowestRestoCoordinator,
        entry: HowestRestoConfigEntry,
    ) -> None:
        """Initialize tomorrow sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = (
            f"howest_resto_{coordinator.campus_code.lower()}_tomorrow"
        )

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return self._format_dish_state(self.coordinator.tomorrow_menu)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        attrs: dict[str, Any] = {
            ATTR_CAMPUS: self.coordinator.campus_code,
            ATTR_CAMPUS_NAME: self.coordinator.campus_name,
        }
        tomorrow = self.coordinator.tomorrow_menu
        if tomorrow:
            attrs.update(
                {
                    ATTR_DATE: tomorrow.date,
                    ATTR_DAY: tomorrow.day,
                    ATTR_DISHES: tomorrow.all_raw_items or tomorrow.dutch_dishes,
                    ATTR_DUTCH_DISHES: tomorrow.dutch_dishes,
                    ATTR_ENGLISH_DISHES: tomorrow.english_dishes,
                }
            )
        return attrs
