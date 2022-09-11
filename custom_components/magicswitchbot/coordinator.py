"""Provides the switchbot DataUpdateCoordinator."""
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, cast

from magicswitchbotasync import MagicSwitchbot

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth.passive_update_coordinator import (
    PassiveBluetoothDataUpdateCoordinator,
)
from homeassistant.core import HomeAssistant, callback

if TYPE_CHECKING:
    from bleak.backends.device import BLEDevice


_LOGGER = logging.getLogger(__name__)


class MagicSwitchbotDataUpdateCoordinator(PassiveBluetoothDataUpdateCoordinator):
    """Class to manage fetching MagicSwitchbot data."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        ble_device: BLEDevice,
        device: MagicSwitchbot,
    ) -> None:
        """Initialize global MagicSwitchbot data updater."""
        super().__init__(hass, logger, ble_device.address)
        self.ble_device = ble_device
        self.device = device
        self.data: dict[str, Any] = {}
        self._ready_event = asyncio.Event()

    @callback
    def _async_handle_bluetooth_event(
        self,
        service_info: bluetooth.BluetoothServiceInfo,
        change: bluetooth.BluetoothChange,
    ) -> None:
        """Handle a Bluetooth event."""
        super()._async_handle_bluetooth_event(service_info, change)
        discovery_info_bleak = cast(bluetooth.BluetoothServiceInfoBleak, service_info)
        if adv := parse_advertisement_data(
            discovery_info_bleak.device, discovery_info_bleak.advertisement
        ):
            self.data = adv.data
            if "modelName" in self.data:
                self._ready_event.set()
            _LOGGER.debug("%s: MagicSwitchbot data: %s", self.ble_device.address, self.data)
            self.device.update_from_advertisement(adv)
        self.async_update_listeners()

    async def async_wait_ready(self) -> bool:
        """Wait for the device to be ready."""
        try:
            await asyncio.wait_for(self._ready_event.wait(), timeout=55)
        except asyncio.TimeoutError:
            return False
        return True
