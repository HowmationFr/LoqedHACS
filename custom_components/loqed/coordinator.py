"""Data update coordinator for the LOQED integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import LoqedApiClient, LoqedConnectionError, LoqedStatus
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class LoqedDataCoordinator(DataUpdateCoordinator[LoqedStatus]):
    """Coordinator to poll the LOQED bridge for lock status."""

    def __init__(self, hass: HomeAssistant, api: LoqedApiClient) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> LoqedStatus:
        """Fetch the latest status from the bridge."""
        try:
            return await self.api.async_get_status()
        except LoqedConnectionError as err:
            raise UpdateFailed(f"Error communicating with LOQED bridge: {err}") from err
