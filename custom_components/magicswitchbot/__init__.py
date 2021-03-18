"""The magicswitchbot component."""
import asyncio
import logging
from .const import DOMAIN
from homeassistant.core import callback

from homeassistant.auth.mfa_modules import _LOGGER
from homeassistant.const import ATTR_ENTITY_ID


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
            _LOGGER.info("Pushing the button using MagicSwitchbot device at %s...", entity._mac)
            hass.async_add_job(entity.push)
        except:
            _LOGGER.error("Failed to execute the psuh command with Magic Switchbot device")
        
        return

    # Register our service with Home Assistant.
    hass.services.async_register(DOMAIN, 'push', async_push_button)

    # Return boolean to indicate that initialization was successfully.
    return True
