"""Data coordinator for Midlothian Bin Collection."""
from __future__ import annotations

import logging
from datetime import datetime, date

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    SCAN_INTERVAL,
    CONF_POSTCODE,
    CONF_UPRN,
    BIN_TYPES,
    API_BASE,
    AUTH_URL,
    LOOKUP_URL,
    ADDRESS_LOOKUP_ID,
    BIN_LOOKUP_ID,
    PORTAL_NAME,
    SERVICE_MAP,
)

_LOGGER = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-GB,en;q=0.5",
    "Content-Type": "application/json",
}


async def _get_session_cookies(session: aiohttp.ClientSession) -> None:
    """Authenticate and initialise session cookies."""
    async with session.get(
        AUTH_URL,
        params={"hostname": "my.midlothian.gov.uk"},
        ssl=False,
    ) as resp:
        if resp.status != 200:
            raise aiohttp.ClientError(f"Auth endpoint returned HTTP {resp.status}")

    # Visit the service page to fully initialise the session
    async with session.get(
        f"{API_BASE}/service/Bin_Collection_Dates",
        ssl=False,
    ) as resp:
        pass


async def async_lookup_addresses(postcode: str) -> list[dict[str, str]]:
    """Look up addresses by postcode via the Granicus API."""
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        await _get_session_cookies(session)

        payload = {
            "formValues": {
                "Section 1": {
                    "postcode": {"value": postcode.upper().strip()},
                },
            },
        }

        async with session.post(
            LOOKUP_URL,
            params={
                "id": ADDRESS_LOOKUP_ID,
                "repeat_against": "",
                "portal_name": PORTAL_NAME,
            },
            json=payload,
            ssl=False,
        ) as resp:
            if resp.status != 200:
                raise aiohttp.ClientError(f"Address lookup returned HTTP {resp.status}")
            data = await resp.json()

    rows = (
        data.get("integration", {})
        .get("transformed", {})
        .get("rows_data", {})
    )

    addresses = []
    for uprn, info in rows.items():
        if isinstance(info, dict):
            display = info.get("display") or info.get("address") or info.get("name", uprn)
            addresses.append({"uprn": str(uprn), "address": str(display)})
    return addresses


async def async_fetch_bin_dates(postcode: str, uprn: str) -> dict[str, date | None]:
    """Fetch bin collection dates via the Granicus API."""
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        await _get_session_cookies(session)

        # If no UPRN stored, try to look one up from postcode
        effective_uprn = uprn
        if not effective_uprn:
            addresses = await async_lookup_addresses(postcode)
            if addresses:
                effective_uprn = addresses[0]["uprn"]

        if not effective_uprn:
            _LOGGER.warning("No UPRN available for postcode %s", postcode)
            return {bt: None for bt in BIN_TYPES}

        today_str = date.today().isoformat()

        payload = {
            "formValues": {
                "Section 1": {
                    "uprn": {"value": str(effective_uprn)},
                    "fromDate": {"value": today_str},
                },
            },
        }

        async with session.post(
            LOOKUP_URL,
            params={
                "id": BIN_LOOKUP_ID,
                "repeat_against": "",
                "portal_name": PORTAL_NAME,
            },
            json=payload,
            ssl=False,
        ) as resp:
            if resp.status != 200:
                raise UpdateFailed(f"Bin lookup returned HTTP {resp.status}")
            data = await resp.json()

    rows = (
        data.get("integration", {})
        .get("transformed", {})
        .get("rows_data", {})
    )

    if not rows:
        _LOGGER.warning(
            "No bin collection data returned for UPRN %s. API response: %s",
            effective_uprn,
            data,
        )
        return {bt: None for bt in BIN_TYPES}

    return _parse_api_rows(rows)


def _parse_api_rows(rows: dict) -> dict[str, date | None]:
    """Parse the API rows_data into bin type -> next collection date."""
    results: dict[str, date | None] = {bt: None for bt in BIN_TYPES}

    for _key, row in rows.items():
        if not isinstance(row, dict):
            continue

        service = (row.get("Service") or "").lower()
        date_str = row.get("Date") or ""

        # Match service name to our bin type
        bin_type = None
        for keyword, bt in SERVICE_MAP.items():
            if keyword in service:
                bin_type = bt
                break

        if bin_type is None:
            _LOGGER.debug("Unknown service type: %s", service)
            continue

        # Parse date - format is "dd/MM/yyyy 00:00:00"
        parsed = _try_parse_date(date_str)
        if parsed and (results[bin_type] is None or parsed < results[bin_type]):
            results[bin_type] = parsed

    return results


def _try_parse_date(text: str) -> date | None:
    """Try to parse a date string from the API."""
    text = text.strip()
    for fmt in ["%d/%m/%Y %H:%M:%S", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


class MidlothianBinsCoordinator(DataUpdateCoordinator[dict[str, date | None]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self._postcode: str = entry.data[CONF_POSTCODE]
        self._uprn: str = entry.data.get(CONF_UPRN, "")

    async def _async_update_data(self) -> dict[str, date | None]:
        try:
            return await async_fetch_bin_dates(self._postcode, self._uprn)
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with Midlothian Council: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err
