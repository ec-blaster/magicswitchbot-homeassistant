from typing import Dict, Any

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
from homeassistant.const import (
  CONF_MAC,
  CONF_NAME,
  CONF_PASSWORD,
  CONF_DEVICE_ID,
  CONF_COUNT
)
from homeassistant.helpers.restore_state import RestoreEntity
from magicswitchbot import MagicSwitchbot, _LOGGER

from .const import DOMAIN
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

DEFAULT_NAME = "MagicSwitchbot"
DEFAULT_DEVICE_ID = 0
DEFAULT_RETRY_COUNT = 3

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MAC): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
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
    
    '''Get the switch config'''
    name = config.get(CONF_NAME)
    mac_addr = config[CONF_MAC]
    password = config.get(CONF_PASSWORD)
    retry_count = config.get(CONF_COUNT)
    bt_device = config.get(CONF_DEVICE_ID)
    
    '''Initialize the device'''
    device = MagicSwitchbot(mac=mac_addr, retry_count=retry_count, password=password, interface=bt_device)
    
    '''Connect asynchronously'''
    await hass.async_add_executor_job(device.connect)
    
    '''Let's auth (max time 5 seconds or will be disconnected)'''
    '''TODO: catch auth or connect exceptions'''
    await hass.async_add_executor_job(device.auth)
    # hass.async_add_job(device.connect)
    
    '''Initialize out custom switchs list if it does not exist in HA'''
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    
    '''Create our entity'''
    async_add_entities([MagicSwitchbotSwitch(device, hass, mac_addr, name)])

    
class MagicSwitchbotSwitch(SwitchEntity, RestoreEntity):
    """Custom switch for MagicSwitchbot"""

    def __init__(self, device, hass, mac, name) -> None:
        """Initialize the MagicSwitchbot."""
        self._state = None
        self._device = device
        self._hass = hass
        self._last_run_success = None
        self._name = name
        self._mac = mac

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if not state:
            return
        self._state = state.state == "on"
        self._hass.data[DOMAIN][self.entity_id] = self._device
        _LOGGER.info("Added Magic Swithbot with entity_id '%s' to the list of custom switches", self.entity_id)
        
    def turn_on(self, **kwargs) -> None:
        """Turn device on."""
        if self._device.turn_on():
            self._state = True
            self._last_run_success = True
        else:
            self._last_run_success = False

    def turn_off(self, **kwargs) -> None:
        """Turn device off."""
        if self._device.turn_off():
            self._state = False
            self._last_run_success = True
        else:
            self._last_run_success = False

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
        
    @property
    def assumed_state(self) -> bool:
        """Return true if unable to access real state of entity."""
        return True

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
        return {"last_run_success": self._last_run_success}
