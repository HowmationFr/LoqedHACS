"""Lock platform for the LOQED Local integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.lock import LockEntity, LockEntityFeature
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import LoqedLocalConfigEntry
from .api import LoqedConnectionError
from .const import (
    BOLT_STATE_DAY_LOCK,
    BOLT_STATE_NIGHT_LOCK,
    BOLT_STATE_OPEN,
    CONF_LOCK_NAME,
    DOMAIN,
    MANUFACTURER,
)
from .coordinator import LoqedLocalDataCoordinator

COMMAND_DELAY = 3  # seconds to wait for the lock to finish moving

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
    _attr_name = None
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

        self._cancel_delayed_refresh: CALLBACK_TYPE | None = None

    @callback
    def _cancel_pending_refresh(self) -> None:
        """Cancel any pending delayed refresh."""
        if self._cancel_delayed_refresh is not None:
            self._cancel_delayed_refresh()
            self._cancel_delayed_refresh = None

    async def _send_command_with_transition(
        self, command_coro, target_state: str
    ) -> None:
        """Send a command, set transitional state, and schedule a delayed poll."""
        try:
            await command_coro()
        except LoqedConnectionError as err:
            _LOGGER.error("Failed to send LOQED command: %s", err)
            return

        # Immediately show "locking" / "unlocking" in HA
        self.coordinator.transition_target = target_state
        self.async_write_ha_state()

        # Cancel any previous pending refresh, then schedule a new one
        self._cancel_pending_refresh()

        @callback
        def _delayed_refresh(_now) -> None:
            """Poll the lock after the mechanical action completes."""
            self._cancel_delayed_refresh = None
            self.hass.async_create_task(
                self.coordinator.async_request_refresh()
            )

        self._cancel_delayed_refresh = async_call_later(
            self.hass, COMMAND_DELAY, _delayed_refresh
        )

    async def async_will_remove_from_hass(self) -> None:
        """Clean up on removal."""
        self._cancel_pending_refresh()
        await super().async_will_remove_from_hass()

    @property
    def is_locked(self) -> bool | None:
        """Return true if the lock is locked (night_lock)."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.bolt_state == BOLT_STATE_NIGHT_LOCK

    @property
    def is_locking(self) -> bool:
        """Return true if the lock is transitioning to locked."""
        return self.coordinator.transition_target == BOLT_STATE_NIGHT_LOCK

    @property
    def is_unlocking(self) -> bool:
        """Return true if the lock is transitioning to unlocked or open."""
        return self.coordinator.transition_target in (
            BOLT_STATE_DAY_LOCK,
            BOLT_STATE_OPEN,
        )

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
        attrs: dict[str, Any] = {
            "bolt_state": data.bolt_state,
            "bolt_state_numeric": data.bolt_state_numeric,
            "lock_online": data.lock_online,
        }
        if self.coordinator.transition_target:
            attrs["transition_target"] = self.coordinator.transition_target
        return attrs

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock the door (NIGHT_LOCK)."""
        await self._send_command_with_transition(
            self.coordinator.api.async_night_lock, BOLT_STATE_NIGHT_LOCK
        )

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock the door (DAY_LOCK / latch)."""
        await self._send_command_with_transition(
            self.coordinator.api.async_day_lock, BOLT_STATE_DAY_LOCK
        )

    async def async_open(self, **kwargs: Any) -> None:
        """Open the door (OPEN - full unlatch)."""
        await self._send_command_with_transition(
            self.coordinator.api.async_open, BOLT_STATE_OPEN
        )
