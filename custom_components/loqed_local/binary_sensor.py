"""Binary sensor platform for the LOQED Local integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import LoqedLocalConfigEntry
from .const import CONF_LOCK_NAME, DOMAIN, MANUFACTURER
from .coordinator import LoqedLocalDataCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LoqedLocalConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up LOQED Local binary sensor entities."""
    coordinator = entry.runtime_data
    async_add_entities([LoqedLocalOnlineSensor(coordinator, entry)])


class LoqedLocalOnlineSensor(CoordinatorEntity[LoqedLocalDataCoordinator], BinarySensorEntity):
    """Binary sensor indicating whether the lock is online."""

    _attr_has_entity_name = True
    _attr_translation_key = "lock_online"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self,
        coordinator: LoqedLocalDataCoordinator,
        entry: LoqedLocalConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        mac = coordinator.data.bridge_mac_wifi if coordinator.data else "unknown"
        lock_name = entry.data.get(CONF_LOCK_NAME, "LOQED Lock")

        self._attr_unique_id = f"loqed_local_{mac}_online"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac)},
            name=f"{lock_name} (Local)",
            manufacturer=MANUFACTURER,
            model="Touch Smart Lock",
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the lock is online."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.lock_online
