"""Data coordinator for Midlothian Bin Collection."""
from __future__ import annotations

import logging
import re
from datetime import datetime, date

import aiohttp
from bs4 import BeautifulSoup

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, COUNCIL_URL, SCAN_INTERVAL, CONF_POSTCODE, CONF_UPRN, BIN_TYPES, BIN_KEYWORDS

_LOGGER = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.5",
}


async def async_lookup_addresses(postcode: str) -> list[dict[str, str]]:
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(COUNCIL_URL, ssl=False) as resp:
            if resp.status != 200:
                raise aiohttp.ClientError(f"HTTP {resp.status}")
            html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        form = soup.find("form")
        payload: dict[str, str] = {}
        if form:
            for inp in form.find_all("input", {"type": ["hidden", "submit"]}):
                if inp.get("name"):
                    payload[inp["name"]] = inp.get("value", "")
            action = form.get("action", COUNCIL_URL)
            if action.startswith("/"):
                action = "https://my.midlothian.gov.uk" + action
        else:
            action = COUNCIL_URL

        postcode_field = next(
            (inp.get("name") for inp in soup.find_all("input") if "postcode" in (inp.get("name") or "").lower()),
            "postcode"
        )
        payload[postcode_field] = postcode.upper().strip()

        async with session.post(action, data=payload, ssl=False) as resp:
            if resp.status != 200:
                raise aiohttp.ClientError(f"HTTP {resp.status}")
            html = await resp.text()

    return _parse_addresses(html)


def _parse_addresses(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    addresses = []
    for select in soup.find_all("select"):
        if any(k in (select.get("name") or "").lower() for k in ("uprn", "address", "property")):
            for option in select.find_all("option"):
                value = option.get("value", "").strip()
                text = option.get_text(strip=True)
                if value and value.lower() not in ("", "select", "please select"):
                    addresses.append({"uprn": value, "address": text})
            break
    if not addresses:
        for inp in soup.find_all("input", {"type": "radio"}):
            if any(k in (inp.get("name") or "").lower() for k in ("uprn", "address", "property")):
                value = inp.get("value", "").strip()
                label_tag = inp.find_next("label")
                label = label_tag.get_text(strip=True) if label_tag else value
                if value:
                    addresses.append({"uprn": value, "address": label})
    return addresses


async def async_fetch_bin_dates(postcode: str, uprn: str) -> dict[str, date | None]:
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(COUNCIL_URL, ssl=False) as resp:
            if resp.status != 200:
                raise UpdateFailed(f"HTTP {resp.status}")
            html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        form = soup.find("form")
        payload: dict[str, str] = {}
        action = COUNCIL_URL
        if form:
            for inp in form.find_all("input", {"type": ["hidden", "submit"]}):
                if inp.get("name"):
                    payload[inp["name"]] = inp.get("value", "")
            action = form.get("action", COUNCIL_URL)
            if action.startswith("/"):
                action = "https://my.midlothian.gov.uk" + action

        postcode_field = next(
            (inp.get("name") for inp in soup.find_all("input") if "postcode" in (inp.get("name") or "").lower()),
            "postcode"
        )
        payload[postcode_field] = postcode.upper().strip()

        async with session.post(action, data=payload, ssl=False) as resp:
            if resp.status != 200:
                raise UpdateFailed(f"HTTP {resp.status}")
            html = await resp.text()

        soup2 = BeautifulSoup(html, "html.parser")
        if uprn and (soup2.find("select") or soup2.find("input", {"type": "radio"})):
            form2 = soup2.find("form")
            payload2: dict[str, str] = {}
            action2 = action
            if form2:
                for inp in form2.find_all("input", {"type": ["hidden", "submit"]}):
                    if inp.get("name"):
                        payload2[inp["name"]] = inp.get("value", "")
                action2 = form2.get("action", action)
                if action2.startswith("/"):
                    action2 = "https://my.midlothian.gov.uk" + action2
            for select in soup2.find_all("select"):
                payload2[select.get("name")] = uprn
            for inp in soup2.find_all("input", {"type": "radio"}):
                if any(k in (inp.get("name") or "").lower() for k in ("uprn", "address", "property")):
                    payload2[inp.get("name")] = uprn
                    break
            async with session.post(action2, data=payload2, ssl=False) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"HTTP {resp.status}")
                html = await resp.text()

    return _parse_bin_dates(html)


def _parse_bin_dates(html: str) -> dict[str, date | None]:
    soup = BeautifulSoup(html, "html.parser")
    results: dict[str, date | None] = {bin_type: None for bin_type in BIN_TYPES}
    date_pattern = re.compile(
        r"\b(\d{1,2})[\/\-\s](\w+)[\/\-\s](\d{2,4})\b"
        r"|\b(\w+)\s+(\d{1,2}),?\s+(\d{4})\b"
        r"|\b(\d{1,2})\s+(\w+)\s+(\d{4})\b"
    )
    for block in [tag.get_text(" ", strip=True) for tag in soup.find_all(["tr", "li", "div", "p", "td", "span", "h3", "h4"])]:
        block_lower = block.lower()
        matched_type = next((bt for bt, kws in BIN_KEYWORDS.items() if any(kw in block_lower for kw in kws)), None)
        if not matched_type:
            continue
        for m in date_pattern.finditer(block):
            parsed = _try_parse_date(m.group(0))
            if parsed and (results[matched_type] is None or parsed < results[matched_type]):
                results[matched_type] = parsed
    return results


def _try_parse_date(text: str) -> date | None:
    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d %B %Y", "%d %b %Y", "%B %d, %Y", "%b %d, %Y", "%d %B %y", "%d %b %y", "%d/%m/%y"]:
        try:
            return datetime.strptime(text.strip(), fmt).date()
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
