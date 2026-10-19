"""Fixtures for the Howest Resto integration tests."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from howest_resto.models import DailyMenu, WeeklyMenuResponse
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.howest_resto.const import (
    CONF_CAMPUS,
    CONF_LANGUAGE,
    CONF_SCAN_INTERVAL,
    DOMAIN,
)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,
) -> Generator[None]:
    """Enable loading of the custom integration in every test."""
    yield


@pytest.fixture
def sample_weekly_menu() -> WeeklyMenuResponse:
    """Return a realistic sample weekly menu."""
    days = [
        DailyMenu(
            date="19/10/2026",
            day="Ma",
            all_raw_items=[
                "Tomatensoep / Tomato soup",
                "Vol-au-vent met frietjes / Chicken pastry with fries",
            ],
            dutch_dishes=[
                "Tomatensoep",
                "Vol-au-vent met frietjes",
            ],
            english_dishes=[
                "Tomato soup",
                "Chicken pastry with fries",
            ],
        ),
        DailyMenu(
            date="20/10/2026",
            day="Di",
            all_raw_items=[
                "Pompoensoep / Pumpkin soup",
                "Spaghetti Bolognese / Pasta Bolognese",
            ],
            dutch_dishes=[
                "Pompoensoep",
                "Spaghetti Bolognese",
            ],
            english_dishes=[
                "Pumpkin soup",
                "Pasta Bolognese",
            ],
        ),
        DailyMenu(
            date="21/10/2026",
            day="Wo",
            all_raw_items=[
                "Preisoep / Leek soup",
                "Balletjes in tomatensaus / Meatballs in tomato sauce",
            ],
            dutch_dishes=[
                "Preisoep",
                "Balletjes in tomatensaus",
            ],
            english_dishes=[
                "Leek soup",
                "Meatballs in tomato sauce",
            ],
        ),
        DailyMenu(
            date="22/10/2026",
            day="Do",
            all_raw_items=[
                "Groentesoep / Vegetable soup",
                "Kip curry met rijst / Chicken curry with rice",
            ],
            dutch_dishes=[
                "Groentesoep",
                "Kip curry met rijst",
            ],
            english_dishes=[
                "Vegetable soup",
                "Chicken curry with rice",
            ],
        ),
        DailyMenu(
            date="23/10/2026",
            day="Vr",
            all_raw_items=[
                "Vissoep / Fish soup",
                "Fish & Chips / Fish and chips",
            ],
            dutch_dishes=[
                "Vissoep",
                "Fish & Chips",
            ],
            english_dishes=[
                "Fish soup",
                "Fish and chips",
            ],
        ),
    ]
    return WeeklyMenuResponse(
        campus="GKG",
        campus_name="'t Obeetje (Graaf Karel de Goedelaan 5, Kortrijk)",
        week="current",
        days=days,
        fetched_at="2026-10-19T10:00:00+00:00",
    )


@pytest.fixture
def mock_client(sample_weekly_menu: WeeklyMenuResponse) -> Generator[AsyncMock]:
    """Patch AsyncHowestRestoClient across the integration."""
    client = AsyncMock()
    client.get_menu.return_value = sample_weekly_menu

    with (
        patch(
            "custom_components.howest_resto.AsyncHowestRestoClient",
            return_value=client,
        ),
        patch(
            "custom_components.howest_resto.config_flow.AsyncHowestRestoClient",
            return_value=client,
        ),
    ):
        yield client


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mock config entry for Howest Resto."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Howest Resto - 't Obeetje (Kortrijk)",
        data={CONF_CAMPUS: "GKG"},
        options={CONF_SCAN_INTERVAL: 60, CONF_LANGUAGE: "dutch"},
        unique_id="howest_resto_gkg",
    )
