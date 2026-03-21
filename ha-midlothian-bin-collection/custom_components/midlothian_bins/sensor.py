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
        self._attr_unique_id = f"{entry.entry_id}_{bin_type}"
        self._attr_name = f"{address} {BIN_DISPLAY_NAMES[bin_type]}"
        self._attr_icon = BIN_ICONS[bin_type]
        self._attr_extra_state_attributes = {
            "bin_colour": BIN_COLOURS[bin_type],
            "bin_type": BIN_DISPLAY_NAMES[bin_type],
        }

    @property
    def native_value(self) -> str | None:
        if self.coordinator.data is None:
            return None
        collection_date: date | None = self.coordinator.data.get(self._bin_type)
        return collection_date.isoformat() if collection_date else None
