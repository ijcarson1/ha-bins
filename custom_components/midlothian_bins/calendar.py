"""Calendar platform for Midlothian Bin Collection."""
from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_ADDRESS,
    CONF_POSTCODE,
    BIN_TYPES,
    BIN_DISPLAY_NAMES,
    BIN_ICONS,
    BIN_COLOURS,
)
from .coordinator import MidlothianBinsCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: MidlothianBinsCoordinator = hass.data[DOMAIN][entry.entry_id]
    address = entry.data.get(CONF_ADDRESS) or entry.data.get(CONF_POSTCODE, "")
    async_add_entities(
        MidlothianBinCalendar(coordinator, entry, bin_type, address)
        for bin_type in BIN_TYPES
    )


class MidlothianBinCalendar(
    CoordinatorEntity[MidlothianBinsCoordinator], CalendarEntity
):
    """A calendar entity for a single bin type showing its next collection."""

    def __init__(
        self,
        coordinator: MidlothianBinsCoordinator,
        entry: ConfigEntry,
        bin_type: str,
        address: str,
    ) -> None:
        super().__init__(coordinator)
        self._bin_type = bin_type
        self._address = address
        self._attr_unique_id = f"{entry.entry_id}_{bin_type}_calendar"
        self._attr_name = f"{address} {BIN_DISPLAY_NAMES[bin_type]} Collection"
        self._attr_icon = BIN_ICONS[bin_type]

    def _make_event(self, collection_date: date) -> CalendarEvent:
        return CalendarEvent(
            summary=f"{BIN_DISPLAY_NAMES[self._bin_type]} bin collection",
            start=collection_date,
            end=collection_date + timedelta(days=1),
            description=f"{BIN_COLOURS[self._bin_type]} bin – {self._address}",
        )

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming calendar event for this bin."""
        if self.coordinator.data is None:
            return None
        dates: list[date] = self.coordinator.data.get(self._bin_type, [])
        return self._make_event(dates[0]) if dates else None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return all events within a date range (used by the calendar card)."""
        if self.coordinator.data is None:
            return []
        dates: list[date] = self.coordinator.data.get(self._bin_type, [])
        range_start = start_date.date()
        range_end = end_date.date()
        return [
            self._make_event(d)
            for d in dates
            if range_start <= d <= range_end
        ]
