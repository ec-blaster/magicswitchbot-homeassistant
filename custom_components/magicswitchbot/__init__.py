"""The magicswitchbot component."""
import asyncio
import logging
from .const import DOMAIN
from homeassistant.core import callback

from homeassistant.auth.mfa_modules import _LOGGER
from homeassistant.const import ATTR_ENTITY_ID


@asyncio.coroutine
def async_setup(hass, config):
    """MagicSwitchbot initialization"""

    @callback
    def push(call):
        """Define a service to push a button with MagicSwitchbot"""
        device_id = call.data.get(ATTR_ENTITY_ID)
        _LOGGER.info('Device id to push: %s', device_id)

    # Register our service with Home Assistant.
    hass.services.async_register(DOMAIN, 'push', push)

    # Return boolean to indicate that initialization was successfully.
    return True
