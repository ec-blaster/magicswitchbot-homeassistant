"""
Magic Switchbot component for Home Assistant
Switch entity definition

@author: ec-blaster
@since: March 2021
@contact: https://github.com/ec-blaster/magicswitchbot-homeassistant
"""
import logging
from typing import Dict, Any

from magicswitchbot import MagicSwitchbot

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
  CONF_ADDRESS,
  CONF_NAME,
  STATE_ON
)

from homeassistant.helpers import entity_platform
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN
from .coordinator import MagicSwitchbotDataUpdateCoordinator
from .entity import MagicSwitchbotEntity

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: entity_platform.AddEntitiesCallback,
) -> None:
    """Set up MagicSwitchbot based on a config entry."""
    coordinator: MagicSwitchbotDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    unique_id = entry.unique_id
    assert unique_id is not None
    async_add_entities(
        [
            MagicSwitchbotSwitchEntity(
                coordinator,
                unique_id,
                entry.data[CONF_ADDRESS],
                entry.data[CONF_NAME],
                coordinator.device
            )
        ]
    )
    
    
class MagicSwitchbotSwitchEntity(MagicSwitchbotEntity, SwitchEntity, RestoreEntity):
    """Representation of a MagicSwitchbot switch functionality."""

    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(
        self,
        coordinator: MagicSwitchbotDataUpdateCoordinator,
        unique_id: str,
        address: str,
        name: str,
        device: MagicSwitchbot
        
    ) -> None:
        """Initialize the MagicSwitchbot."""
        super().__init__(coordinator, unique_id, address, name)
        self._attr_unique_id = unique_id
        self._device = device
        self._attr_is_on = False
        self._last_action = None
        self._battery_level = None
        self._icon = "mdi:light-switch"

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        if not (last_state := await self.async_get_last_state()):
            return
        self._attr_is_on = last_state.state == STATE_ON
        if "last_run_success" in last_state.attributes:
            self._last_run_success = last_state.attributes["last_run_success"]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn device on."""
        _LOGGER.info("Turn MagicSwitchbot bot on %s", self._address)

        self._last_run_success = bool(await self._device.turn_on())
        if self._last_run_success:
            self._attr_is_on = True           
            self._last_action = "On"
            self._battery_level = await self._device.get_battery()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn device off."""
        _LOGGER.info("Turn MagicSwitchbot bot off %s", self._address)

        self._last_run_success = bool(await self._device.turn_off())
        if self._last_run_success:
            self._attr_is_on = False
            self._last_action = "Off"
            self._battery_level = await self._device.get_battery()
        self.async_write_ha_state()

    @property
    def assumed_state(self) -> bool:
        """Returns the last known state if unable to access real state of entity."""
        if not "isOn" in self.data["data"]:
            return self._last_action == "On"
        return self.data["data"]["isOn"]

    @property
    def is_on(self) -> bool | None:
        """Return true if device is on."""
        if not "isOn" in self.data["data"]:
            return self._attr_is_on
        else:
            return self.data["data"]["isOn"]

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        return {
            "last_action": self._last_action,
            "battery_level": self._battery_level
        }
