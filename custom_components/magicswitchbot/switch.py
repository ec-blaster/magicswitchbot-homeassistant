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

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
from homeassistant.const import (
  CONF_MAC,
  CONF_NAME,
  CONF_PASSWORD,
  CONF_DEVICE_ID,
  CONF_TIMEOUT,
  CONF_COUNT
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.restore_state import RestoreEntity
import voluptuous as vol

from .const import DOMAIN

from datetime import timedelta
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "MagicSwitchbot"
DEFAULT_DEVICE_ID = 0
DEFAULT_RETRY_COUNT = 3
CONNECT_TIMEOUT = 5
DISCONNECT_TIMEOUT = 30
SCAN_INTERVAL = timedelta(seconds=60)  # We'll check the battery level every minute

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MAC): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_TIMEOUT, default=CONNECT_TIMEOUT): vol.All(
            vol.Coerce(int), vol.Range(min=0)
        ),
        vol.Optional(CONF_COUNT, default=DEFAULT_RETRY_COUNT): vol.All(
            vol.Coerce(int), vol.Range(min=0)
        ),
        vol.Optional(CONF_DEVICE_ID, default=DEFAULT_DEVICE_ID): vol.All(
            vol.Coerce(int), vol.Range(min=0)
        ),
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Magic Switchbot component."""
    
    '''Get the switch config parameters'''
    name = config.get(CONF_NAME)
    mac_addr = config[CONF_MAC]
    password = config.get(CONF_PASSWORD)
    connect_timeout = config.get(CONF_TIMEOUT)
    retry_count = config.get(CONF_COUNT)
    bt_device = config.get(CONF_DEVICE_ID)
    
    '''Initialize the device'''
    device = MagicSwitchbot(mac=mac_addr,
                            retry_count=retry_count,
                            password=password,
                            interface=bt_device,
                            connect_timeout=connect_timeout,
                            disconnect_timeout=DISCONNECT_TIMEOUT)
    
    '''Initialize out custom switchs list if it does not exist in HA'''
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    
    '''Create our entity'''
    async_add_entities([MagicSwitchbotSwitch(device, hass, mac_addr, name)])

    
class MagicSwitchbotSwitch(SwitchEntity, RestoreEntity):
    """Custom switch for MagicSwitchbot"""

    def __init__(self, device:MagicSwitchbot, hass:HomeAssistant, mac:str, name:str) -> None:
        """Initialize the MagicSwitchbot."""
        self._state = None
        self._device = device
        self._hass = hass
        self._last_action = None
        self._name = name
        self._mac = mac
        self._battery_level = None

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if not state:
            return
        self._state = state.state == "on"
        self._hass.data[DOMAIN][self.entity_id] = self
        
        '''We get a first update at start'''
        self.schedule_update_ha_state()
#        await self._hass.async_add_executor_job(self.update)
        
        _LOGGER.debug("Added Magic Switchbot '%s' with %s address", self.entity_id, self._device._mac)
    
    async def async_turn_on(self, **kwargs) -> None:
        """Turn device on."""
        if self._device.turn_on():
            self._state = True
            self._last_action = "On"
            self._battery_level = self._device.get_battery()
        else:
            # self._state = None
            self._last_action = "Error"
        # self.schedule_update_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn device off."""
        if self._device.turn_off():
            self._state = False
            self._last_action = "Off"
            self._battery_level = self._device.get_battery()
        else:
            # self._state = None
            self._last_action = "Error"
        # self.schedule_update_ha_state()

    '''This block will only get called when using Config Entries'''

    @property
    def device_info(self):
        """Define a device for this switch"""
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.unique_id)
            },
            "name": self.name,
            "manufacturer": "Shenzhen Interear Intelligent Technology",
            "model": "Magic Switchbot",
            "sw_version": "2.0",
            "via_device": (DOMAIN, self.unique_id),
        }

    '''        
    async def async_update(self):
        """We get the battery level on a periodic polling basis"""
        self._battery_level = self._device.get_battery()
        if self._battery_level is not None:
            _LOGGER.debug("Battery level of %s: %d%%", self.entity_id, self._battery_level)
        else:
            _LOGGER.warn("Couldn't get battery level of %s", self.entity_id)
        self._device.disconnect()'''
        
    """@property
    def available(self) -> bool:
        return self._device._is_connected()"""
    
    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        return self._state

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return "magicswitchbot_" + self._mac.replace(":", "")

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._name

    @property
    def icon(self) -> str:
        return "mdi:toggle-switch"
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        return {
            "last_action": self._last_action,
            "battery_level": self._battery_level,
            "connected": self._device.is_connected()
        }

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        """Backwards compatibility. Will be soon deprecated"""
        return self.extra_state_attributes
