import logging

from typing import Dict, Any
from magicswitchbotasync import MagicSwitchbot

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
  CONF_ADDRESS,
  CONF_NAME,
  STATE_ON
)

from homeassistant.helpers import entity_platform

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
            MagicSwitchbotButtonEntity(
                coordinator,
                unique_id,
                entry.data[CONF_ADDRESS],
                entry.data[CONF_NAME],
                coordinator.device
            )
        ]
    )

class MagicSwitchbotButtonEntity(MagicSwitchbotEntity, ButtonEntity):
    """MagicSwitchbot button press."""
    
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
        self._attr_unique_id = f"{unique_id}_button"
        self._device = device
        self._attr_is_on = False
        self._last_action = None
        self._battery_level = None
        self._icon = "mdi:gesture-tap-button"

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        if not (last_state := await self.async_get_last_state()):
            return
        self._attr_is_on = last_state.state == STATE_ON
        if "last_run_success" in last_state.attributes:
            self._last_run_success = last_state.attributes["last_run_success"]
            
    async def async_press(self, **kwargs: Any) -> None:
        """Press the button."""
        _LOGGER.info("Push MagicSwitchbot button on %s", self._address)

        self._last_run_success = bool(await self._device.push())
        if self._last_run_success:
            self._attr_is_on = True           
            self._last_action = "Push"
            self._battery_level = await self._device.get_battery()
        self.async_write_ha_state()
        
