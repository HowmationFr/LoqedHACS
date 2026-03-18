"""Data update coordinator for the LOQED Local integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import LoqedApiClient, LoqedConnectionError, LoqedStatus
from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    EVENT_PREFIX_GO_TO_STATE,
    EVENT_PREFIX_STATE_CHANGED,
    GO_TO_STATE_MAP,
    REQUESTED_STATE_MAP,
)

_LOGGER = logging.getLogger(__name__)


class LoqedLocalDataCoordinator(DataUpdateCoordinator[LoqedStatus]):
    """Coordinator with webhook push + polling fallback."""

    def __init__(self, hass: HomeAssistant, api: LoqedApiClient) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api
        # Transition tracking for is_locking / is_unlocking
        self.transition_target: str | None = None  # "night_lock", "day_lock", "open"

    async def _async_update_data(self) -> LoqedStatus:
        """Poll /status as fallback."""
        try:
            status = await self.api.async_get_status()
            # Clear transition on poll (we have the real state now)
            self.transition_target = None
            return status
        except LoqedConnectionError as err:
            raise UpdateFailed(f"Error communicating with LOQED bridge: {err}") from err

    def handle_webhook_event(self, data: dict) -> None:
        """Process an incoming webhook event from the bridge.

        Two types of events:
        - GO_TO_STATE_*: lock is transitioning → set transition_target
        - STATE_CHANGED_*: lock reached final state → update bolt_state, clear transition
        """
        event_type: str = data.get("event_type", "")
        _LOGGER.debug("Webhook event: %s → %s", event_type, data)

        if event_type.startswith(EVENT_PREFIX_GO_TO_STATE):
            # Transitioning — set the target state
            go_to = data.get("go_to_state", "")
            target = GO_TO_STATE_MAP.get(go_to)
            if target:
                self.transition_target = target
                _LOGGER.debug("Lock transitioning to: %s", target)
                self.async_set_updated_data(self.data)

        elif event_type.startswith(EVENT_PREFIX_STATE_CHANGED):
            # Final state reached — update the actual bolt state
            requested_state = data.get("requested_state", "")
            requested_numeric = data.get("requested_state_numeric")
            new_bolt_state = REQUESTED_STATE_MAP.get(requested_state)

            if new_bolt_state and self.data:
                self.transition_target = None
                # Create updated status with new bolt state
                updated = LoqedStatus(
                    battery_percentage=self.data.battery_percentage,
                    battery_voltage=self.data.battery_voltage,
                    bolt_state=new_bolt_state,
                    bolt_state_numeric=requested_numeric if requested_numeric is not None else self.data.bolt_state_numeric,
                    lock_online=True,  # If we get a webhook, it's online
                    wifi_strength=self.data.wifi_strength,
                    ble_strength=self.data.ble_strength,
                    bridge_mac_wifi=data.get("mac_wifi", self.data.bridge_mac_wifi),
                    bridge_mac_ble=data.get("mac_ble", self.data.bridge_mac_ble),
                    ip_address=self.data.ip_address,
                    up_timestamp=self.data.up_timestamp,
                )
                _LOGGER.debug("Lock state changed to: %s", new_bolt_state)
                self.async_set_updated_data(updated)
        else:
            _LOGGER.debug("Unknown webhook event type: %s", event_type)
