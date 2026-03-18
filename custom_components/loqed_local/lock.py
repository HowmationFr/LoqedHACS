"""Lock platform for the LOQED Local integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.lock import LockEntity, LockEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import LoqedLocalConfigEntry
from .api import LoqedConnectionError
from .const import (
    BOLT_STATE_NIGHT_LOCK,
    CONF_LOCK_NAME,
    DOMAIN,
    MANUFACTURER,
)
from .coordinator import LoqedLocalDataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LoqedLocalConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the LOQED lock entity."""
    coordinator = entry.runtime_data
    async_add_entities([LoqedLocalLock(coordinator, entry)])


class LoqedLocalLock(CoordinatorEntity[LoqedLocalDataCoordinator], LockEntity):
    """Representation of a LOQED smart lock (local control)."""

    _attr_has_entity_name = True
    _attr_name = None  # Use device name
    _attr_supported_features = LockEntityFeature.OPEN

    def __init__(
        self,
        coordinator: LoqedLocalDataCoordinator,
        entry: LoqedLocalConfigEntry,
    ) -> None:
        """Initialize the lock entity."""
        super().__init__(coordinator)
        self._entry = entry
        lock_name = entry.data.get(CONF_LOCK_NAME, "LOQED Lock")
        mac = coordinator.data.bridge_mac_wifi if coordinator.data else "unknown"

        self._attr_unique_id = f"loqed_local_{mac}_lock"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac)},
            name=f"{lock_name} (Local)",
            manufacturer=MANUFACTURER,
            model="Touch Smart Lock",
            sw_version="1.0",
            configuration_url=f"http://{coordinator.api.ip_address}",
        )

    @property
    def is_locked(self) -> bool | None:
        """Return true if the lock is locked (night_lock)."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.bolt_state == BOLT_STATE_NIGHT_LOCK

    @property
    def is_locking(self) -> bool:
        """Return true if the lock is transitioning to locked."""
        return False

    @property
    def is_unlocking(self) -> bool:
        """Return true if the lock is transitioning to unlocked."""
        return False

    @property
    def is_jammed(self) -> bool:
        """Return true if the lock is jammed."""
        return False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return {}
        data = self.coordinator.data
        return {
            "bolt_state": data.bolt_state,
            "bolt_state_numeric": data.bolt_state_numeric,
            "lock_online": data.lock_online,
        }

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock the door (NIGHT_LOCK)."""
        try:
            await self.coordinator.api.async_night_lock()
        except LoqedConnectionError as err:
            _LOGGER.error("Failed to lock LOQED: %s", err)
            return
        await self.coordinator.async_request_refresh()

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock the door (DAY_LOCK / latch)."""
        try:
            await self.coordinator.api.async_day_lock()
        except LoqedConnectionError as err:
            _LOGGER.error("Failed to unlock LOQED: %s", err)
            return
        await self.coordinator.async_request_refresh()

    async def async_open(self, **kwargs: Any) -> None:
        """Open the door (OPEN - full unlatch)."""
        try:
            await self.coordinator.api.async_open()
        except LoqedConnectionError as err:
            _LOGGER.error("Failed to open LOQED: %s", err)
            return
        await self.coordinator.async_request_refresh()
