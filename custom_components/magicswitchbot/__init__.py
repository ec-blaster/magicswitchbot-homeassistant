"""
Magic Switchbot component for Home Assistant
Service definition

@author: ec-blaster
@since: March 2021
@contact: https://github.com/ec-blaster/magicswitchbot-homeassistant
"""
import asyncio
import logging
from .const import DOMAIN
from homeassistant.core import callback

from homeassistant.const import ATTR_ENTITY_ID
from custom_components.magicswitchbot.switch import MagicSwitchbotSwitch

_LOGGER = logging.getLogger(__name__)


@asyncio.coroutine
def async_setup(hass, config):
    """MagicSwitchbot platform initialization"""

    @callback
    def async_push_button(call):
        """Define a service to push a button with MagicSwitchbot"""
        
        '''We get the entity_id to push from the service parameter''' 
        entity_id = call.data.get(ATTR_ENTITY_ID)
        
        '''We look for that entity id in our known custom switches list'''
        if entity_id in hass.data[DOMAIN]:
            entity = hass.data[DOMAIN][entity_id]
        else:
            _LOGGER.error("There is no Magic Switchbot defined as '%s'", entity_id)
            return
  
        try:
            hass.loop.create_task(async_push_and_battery(entity))
        except Exception as e:
            entity._last_action = "Error"
            _LOGGER.error("Failed to execute the push command with Magic Switchbot device: %s", str(e))
        entity.async_write_ha_state()
        
        return
    
    async def async_push_and_battery(switch:MagicSwitchbotSwitch):
        _LOGGER.info("Pushing the button using MagicSwitchbot device at %s...", switch._mac)
        switch._device.push()
        switch._battery_level = switch._device.get_battery()
        '''Once pushed, the switch must get back to "Off" state'''
        switch._state = False
        switch._last_action = "Push"

    """Register our service with Home Assistant"""
    hass.services.async_register(DOMAIN, 'push', async_push_button)

    """"Return boolean to indicate that initialization was successfully"""
    return True
    
