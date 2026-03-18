"""Config flow for the LOQED Local integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LoqedApiClient, LoqedConnectionError
from .const import (
    CONF_IP_ADDRESS,
    CONF_LOCAL_KEY_ID,
    CONF_LOCK_NAME,
    CONF_SECRET,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_LOCK_NAME, default="Porte d'entrée"): str,
        vol.Required(CONF_IP_ADDRESS): str,
        vol.Required(CONF_LOCAL_KEY_ID): vol.Coerce(int),
        vol.Required(CONF_SECRET): str,
    }
)


class LoqedLocalConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LOQED Local."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            ip_address = user_input[CONF_IP_ADDRESS].strip()
            local_key_id = user_input[CONF_LOCAL_KEY_ID]
            secret = user_input[CONF_SECRET].strip()
            lock_name = user_input[CONF_LOCK_NAME].strip()

            # Deduplicate by IP + key ID
            unique_id = f"loqed_local_{ip_address}_{local_key_id}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            # Test connection
            session = async_get_clientsession(self.hass)
            api = LoqedApiClient(session, ip_address, local_key_id, secret)

            try:
                status = await api.async_get_status()
            except LoqedConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during LOQED Local setup")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"{lock_name} (Local)",
                    data={
                        CONF_IP_ADDRESS: ip_address,
                        CONF_LOCAL_KEY_ID: local_key_id,
                        CONF_SECRET: secret,
                        CONF_LOCK_NAME: lock_name,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
