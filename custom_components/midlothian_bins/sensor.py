"""Sensor platform for Midlothian Bin Collection."""
from __future__ import annotations

from datetime import date

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_ADDRESS, CONF_POSTCODE, BIN_TYPES, BIN_DISPLAY_NAMES, BIN_ICONS, BIN_COLOURS
from .coordinator import MidlothianBinsCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: MidlothianBinsCoordinator = hass.data[DOMAIN][entry.entry_id]
    address = entry.data.get(CONF_ADDRESS) or entry.data.get(CONF_POSTCODE, "")
    async_add_entities(MidlothianBinSensor(coordinator, entry, bin_type, address) for bin_type in BIN_TYPES)


class MidlothianBinSensor(CoordinatorEntity[MidlothianBinsCoordinator], SensorEntity):
    def __init__(self, coordinator, entry, bin_type, address) -> None:
        super().__init__(coordinator)
        self._bin_type = bin_type
        self._bin_colour = BIN_COLOURS[bin_type]
        self._bin_display = BIN_DISPLAY_NAMES[bin_type]
        self._attr_unique_id = f"{entry.entry_id}_{bin_type}"
        self._attr_name = f"{address} {BIN_DISPLAY_NAMES[bin_type]}"
        self._attr_icon = BIN_ICONS[bin_type]

    @property
    def native_value(self) -> str | None:
        next_date = self._next_date()
        return next_date.isoformat() if next_date else None

    @property
    def extra_state_attributes(self) -> dict:
        next_date = self._next_date()
        days_until: int | None = (next_date - date.today()).days if next_date else None
        return {
            "bin_colour": self._bin_colour,
            "bin_type": self._bin_display,
            "days_until": days_until,
        }

    def _next_date(self) -> date | None:
        if self.coordinator.data is None:
            return None
        dates: list[date] = self.coordinator.data.get(self._bin_type, [])
        return dates[0] if dates else None
