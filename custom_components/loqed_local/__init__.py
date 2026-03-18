"""The LOQED Local integration."""

from __future__ import annotations

import logging

from aiohttp.web import Request, Response

from homeassistant.components.webhook import (
    async_generate_id,
    async_register,
    async_unregister,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.network import get_url

from .api import LoqedApiClient
from .const import (
    CONF_IP_ADDRESS,
    CONF_LOCAL_KEY_ID,
    CONF_SECRET,
    CONF_WEBHOOK_ID,
    DOMAIN,
)
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

    # ── Register webhook ──
    webhook_id = entry.data.get(CONF_WEBHOOK_ID)
    if not webhook_id:
        webhook_id = async_generate_id()
        hass.config_entries.async_update_entry(
            entry,
            data={**entry.data, CONF_WEBHOOK_ID: webhook_id},
        )

    async_register(
        hass,
        DOMAIN,
        f"LOQED Local ({entry.title})",
        webhook_id,
        _async_handle_webhook,
        local_only=True,
    )

    # Log the webhook URL for the user
    try:
        internal_url = get_url(hass, allow_external=False, prefer_external=False)
        webhook_url = f"{internal_url}/api/webhook/{webhook_id}"
        _LOGGER.info(
            "LOQED Local webhook URL: %s — Configure this in your LOQED bridge",
            webhook_url,
        )
    except Exception:  # noqa: BLE001
        _LOGGER.info(
            "LOQED Local webhook ID: %s — URL will be http://<HA_IP>:8123/api/webhook/%s",
            webhook_id,
            webhook_id,
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: LoqedLocalConfigEntry) -> bool:
    """Unload a LOQED Local config entry."""
    webhook_id = entry.data.get(CONF_WEBHOOK_ID)
    if webhook_id:
        async_unregister(hass, webhook_id)

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_handle_webhook(
    hass: HomeAssistant, webhook_id: str, request: Request
) -> Response:
    """Handle incoming webhook from the LOQED bridge."""
    try:
        data = await request.json()
    except Exception:  # noqa: BLE001
        _LOGGER.warning("LOQED webhook received invalid JSON")
        return Response(text="Bad Request", status=400)

    _LOGGER.debug("LOQED webhook received: %s", data)

    # Find the coordinator for this webhook
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data.get(CONF_WEBHOOK_ID) == webhook_id:
            coordinator: LoqedLocalDataCoordinator = entry.runtime_data
            coordinator.handle_webhook_event(data)
            break
    else:
        _LOGGER.warning("Received webhook for unknown ID: %s", webhook_id)

    return Response(text="OK", status=200)
