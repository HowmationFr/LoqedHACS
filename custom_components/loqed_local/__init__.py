"""The LOQED Local integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LoqedApiClient
from .const import CONF_IP_ADDRESS, CONF_LOCAL_KEY_ID, CONF_SECRET, DOMAIN
from .coordinator import LoqedLocalDataCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.LOCK, Platform.SENSOR, Platform.BINARY_SENSOR]

type LoqedLocalConfigEntry = ConfigEntry[LoqedLocalDataCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: LoqedLocalConfigEntry) -> bool:
    """Set up LOQED Local from a config entry."""
    session = async_get_clientsession(hass)
    api = LoqedApiClient(
        session=session,
        ip_address=entry.data[CONF_IP_ADDRESS],
        local_key_id=entry.data[CONF_LOCAL_KEY_ID],
        secret=entry.data[CONF_SECRET],
    )

    coordinator = LoqedLocalDataCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: LoqedLocalConfigEntry) -> bool:
    """Unload a LOQED Local config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
