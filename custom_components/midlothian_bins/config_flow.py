"""Config flow for Midlothian Bin Collection."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_POSTCODE, CONF_UPRN, CONF_ADDRESS
from .coordinator import async_lookup_addresses

_LOGGER = logging.getLogger(__name__)


class MidlothianBinsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._postcode: str = ""
        self._addresses: list[dict[str, str]] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            postcode = user_input[CONF_POSTCODE].upper().strip()
            try:
                addresses = await async_lookup_addresses(postcode)
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error looking up postcode %s", postcode)
                errors["base"] = "unknown"
            else:
                if not addresses:
                    await self.async_set_unique_id(postcode)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=postcode,
                        data={CONF_POSTCODE: postcode, CONF_UPRN: "", CONF_ADDRESS: ""},
                    )

                if len(addresses) == 1:
                    addr = addresses[0]
                    await self.async_set_unique_id(addr["uprn"] or postcode)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=addr["address"] or postcode,
                        data={CONF_POSTCODE: postcode, CONF_UPRN: addr["uprn"], CONF_ADDRESS: addr["address"]},
                    )

                self._postcode = postcode
                self._addresses = addresses
                return await self.async_step_select_address()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_POSTCODE): str}),
            errors=errors,
        )

    async def async_step_select_address(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            uprn = user_input[CONF_UPRN]
            address = next((a["address"] for a in self._addresses if a["uprn"] == uprn), uprn)
            await self.async_set_unique_id(uprn)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=address,
                data={CONF_POSTCODE: self._postcode, CONF_UPRN: uprn, CONF_ADDRESS: address},
            )

        address_options = {a["uprn"]: a["address"] for a in self._addresses}
        return self.async_show_form(
            step_id="select_address",
            data_schema=vol.Schema({vol.Required(CONF_UPRN): vol.In(address_options)}),
            errors=errors,
        )
