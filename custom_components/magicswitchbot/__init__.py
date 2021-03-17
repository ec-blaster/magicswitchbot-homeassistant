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
        entity = None
        for switch in hass.data[DOMAIN].values():
          if switch.entity_id == entity_id:
            entity = switch
  
        if entity is None:
          _LOGGER.error("There is no Magic Switchbot defined as '%s'", entity_id)
          return
  
        try:
          _LOGGER.info("Connecting to MagicSwitchbot device...")
          auth = yield from hass.async_add_job(entity.push)
        except:
          _LOGGER.error("Failed to connect to Magic Switchbot device")
        
        return

    # Register our service with Home Assistant.
    hass.services.async_register(DOMAIN, 'push', async_push_button)

    # Return boolean to indicate that initialization was successfully.
    return True
