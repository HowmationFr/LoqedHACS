"""API client for the LOQED bridge local network interface."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

import aiohttp

from .const import BOLT_STATE_NUMERIC, BOLT_STATE_UNKNOWN

_LOGGER = logging.getLogger(__name__)

TIMEOUT = aiohttp.ClientTimeout(total=10)


@dataclass
class LoqedStatus:
    """Representation of the lock status."""

    battery_percentage: int
    battery_voltage: float
    bolt_state: str
    bolt_state_numeric: int
    lock_online: bool
    wifi_strength: int
    ble_strength: int
    bridge_mac_wifi: str
    bridge_mac_ble: str
    ip_address: str
    up_timestamp: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LoqedStatus:
        """Create a LoqedStatus from the /status JSON response."""
        bolt_numeric = data.get("bolt_state_numeric", 0)
        return cls(
            battery_percentage=data.get("battery_percentage", 0),
            battery_voltage=data.get("battery_voltage", 0.0),
            bolt_state=BOLT_STATE_NUMERIC.get(bolt_numeric, BOLT_STATE_UNKNOWN),
            bolt_state_numeric=bolt_numeric,
            lock_online=bool(data.get("lock_online", 0)),
            wifi_strength=data.get("wifi_strength", 0),
            ble_strength=data.get("ble_strength", 0),
            bridge_mac_wifi=data.get("bridge_mac_wifi", ""),
            bridge_mac_ble=data.get("bridge_mac_ble", ""),
            ip_address=data.get("ip_address", ""),
            up_timestamp=data.get("up_timestamp", 0),
        )


class LoqedApiClient:
    """Client for the LOQED bridge local HTTP API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        ip_address: str,
        local_key_id: int,
        secret: str,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._ip_address = ip_address
        self._local_key_id = local_key_id
        self._secret = secret
        self._base_url = f"http://{ip_address}"

    @property
    def ip_address(self) -> str:
        """Return the bridge IP address."""
        return self._ip_address

    async def async_get_status(self) -> LoqedStatus:
        """Fetch the current lock status from /status endpoint."""
        url = f"{self._base_url}/status"
        _LOGGER.debug("Fetching LOQED status from %s", url)

        try:
            async with self._session.get(url, timeout=TIMEOUT) as resp:
                resp.raise_for_status()
                data = await resp.json(content_type=None)
                _LOGGER.debug("LOQED status response: %s", data)
                return LoqedStatus.from_dict(data)
        except asyncio.TimeoutError as err:
            raise LoqedConnectionError(
                f"Timeout connecting to LOQED bridge at {self._ip_address}"
            ) from err
        except aiohttp.ClientError as err:
            raise LoqedConnectionError(
                f"Error connecting to LOQED bridge at {self._ip_address}: {err}"
            ) from err

    async def _async_send_command(self, command: str) -> bool:
        """Send a command to the lock via the local bridge API."""
        url = (
            f"{self._base_url}/state"
            f"?command={command}"
            f"&local_key_id={self._local_key_id}"
            f"&secret={self._secret}"
        )
        _LOGGER.debug("Sending LOQED command: %s", command)

        try:
            async with self._session.get(url, timeout=TIMEOUT) as resp:
                resp.raise_for_status()
                _LOGGER.debug(
                    "LOQED command %s response: %s", command, resp.status
                )
                return True
        except asyncio.TimeoutError as err:
            raise LoqedConnectionError(
                f"Timeout sending command to LOQED bridge at {self._ip_address}"
            ) from err
        except aiohttp.ClientError as err:
            raise LoqedConnectionError(
                f"Error sending command to LOQED bridge: {err}"
            ) from err

    async def async_open(self) -> bool:
        """Send OPEN command (unlatch / open the door)."""
        return await self._async_send_command("OPEN")

    async def async_day_lock(self) -> bool:
        """Send DAY_LOCK command (latch position / unlocked)."""
        return await self._async_send_command("DAY_LOCK")

    async def async_night_lock(self) -> bool:
        """Send NIGHT_LOCK command (fully locked)."""
        return await self._async_send_command("NIGHT_LOCK")


class LoqedConnectionError(Exception):
    """Error connecting to the LOQED bridge."""
