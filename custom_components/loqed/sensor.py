"""Sensor platform for the LOQED Smart Lock integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, SIGNAL_STRENGTH_DECIBELS, UnitOfElectricPotential
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import LoqedConfigEntry
from .api import LoqedStatus
from .const import CONF_LOCK_NAME, DOMAIN, MANUFACTURER
from .coordinator import LoqedDataCoordinator


@dataclass(frozen=True, kw_only=True)
class LoqedSensorEntityDescription(SensorEntityDescription):
    """Describe a LOQED sensor entity."""

    value_fn: Callable[[LoqedStatus], float | int | str | None]


SENSOR_DESCRIPTIONS: tuple[LoqedSensorEntityDescription, ...] = (
    LoqedSensorEntityDescription(
        key="battery_percentage",
        translation_key="battery_percentage",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.battery_percentage,
    ),
    LoqedSensorEntityDescription(
        key="battery_voltage",
        translation_key="battery_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        entity_registry_enabled_default=False,
        value_fn=lambda s: s.battery_voltage,
    ),
    LoqedSensorEntityDescription(
        key="wifi_strength",
        translation_key="wifi_strength",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda s: s.wifi_strength,
    ),
    LoqedSensorEntityDescription(
        key="ble_strength",
        translation_key="ble_strength",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda s: s.ble_strength,
    ),
    LoqedSensorEntityDescription(
        key="bolt_state",
        translation_key="bolt_state",
        device_class=SensorDeviceClass.ENUM,
        options=["open", "day_lock", "night_lock", "unknown"],
        value_fn=lambda s: s.bolt_state,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LoqedConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up LOQED sensor entities."""
    coordinator = entry.runtime_data
    async_add_entities(
        LoqedSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class LoqedSensor(CoordinatorEntity[LoqedDataCoordinator], SensorEntity):
    """Representation of a LOQED sensor."""

    entity_description: LoqedSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LoqedDataCoordinator,
        entry: LoqedConfigEntry,
        description: LoqedSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        mac = coordinator.data.bridge_mac_wifi if coordinator.data else "unknown"
        lock_name = entry.data.get(CONF_LOCK_NAME, "LOQED Lock")

        self._attr_unique_id = f"loqed_{mac}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac)},
            name=lock_name,
            manufacturer=MANUFACTURER,
            model="Touch Smart Lock",
        )

    @property
    def native_value(self) -> float | int | str | None:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
