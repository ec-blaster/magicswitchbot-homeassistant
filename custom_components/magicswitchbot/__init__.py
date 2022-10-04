"""
Magic Switchbot component for Home Assistant
Service definition

@author: ec-blaster
@since: March 2021
@contact: https://github.com/ec-blaster/magicswitchbot-homeassistant
"""

import logging

from magicswitchbotasync import MagicSwitchbot

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_ADDRESS,
    CONF_MAC,
    CONF_PASSWORD,
    CONF_SENSOR_TYPE,
    CONF_NAME,
    Platform
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr

from .const import (
    CONF_RETRY_COUNT,
    DEFAULT_RETRY_COUNT,
    DOMAIN
)
from .coordinator import MagicSwitchbotDataUpdateCoordinator
from _operator import add

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MagicSwitchbot from a config entry."""
    _LOGGER.debug("Configurando MagicSwitchbot desde una entrada de configuración")
    hass.data.setdefault(DOMAIN, {})
    if CONF_ADDRESS not in entry.data and CONF_MAC in entry.data:
        # Bleak uses addresses, not mac addresses, which are are actually
        # UUIDs on some platforms (MacOS).
        mac = entry.data[CONF_MAC]
        if "-" not in mac:
            mac = dr.format_mac(mac)
            
        _LOGGER.debug("Actualizando entrada con MAC, no ADDRESS")
        hass.config_entries.async_update_entry(
            entry,
            data={**entry.data, CONF_ADDRESS: mac},
        )

    if not entry.options:
        _LOGGER.debug("Actualizando entrada sin opciones")
        hass.config_entries.async_update_entry(
            entry,
            options={CONF_RETRY_COUNT: DEFAULT_RETRY_COUNT},
        )

    '''We look for a device with the address configured using HA's bluetooth library'''
    address: str = entry.data[CONF_ADDRESS]
    
    _LOGGER.debug("Buscamos dispositivo con MAC %s...", address)
    
    ble_device = bluetooth.async_ble_device_from_address(hass, address.upper())
    if not ble_device:
        raise ConfigEntryNotReady(
            f"Could not find MagicSwitchbot with address {address}"
        )

    _LOGGER.debug("Dispositivo encontrado")
    '''We create an instance of the device'''
    device = MagicSwitchbot(device=ble_device,
        password=entry.data.get(CONF_PASSWORD),
        retry_count=entry.options[CONF_RETRY_COUNT])
    
    _LOGGER.debug("Instancia creada")
    
    coordinator = hass.data[DOMAIN][entry.entry_id] = MagicSwitchbotDataUpdateCoordinator(
        hass, _LOGGER, ble_device, device
    )
    
    _LOGGER.debug("Coordinador creado")
    
    entry.async_on_unload(coordinator.async_start())
    if not await coordinator.async_wait_ready():
        raise ConfigEntryNotReady(f"MagicSwitchbot with {address} not ready")

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    
    _LOGGER.debug("Configuración pospuesta")
    
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SWITCH, Platform.BUTTON])

    _LOGGER.debug("Proceso de inserción finalizado. Datos de la entidad: %s. Opciones: %s", entry.data, entry.options)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    _LOGGER.debug("Entidad %s actualizada", entry.entry_id)
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    
    _LOGGER.debug("Descargando entidad %s", entry.entry_id)
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, [Platform.SWITCH]
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.config_entries.async_entries(DOMAIN):
            hass.data.pop(DOMAIN)

    return unload_ok


""" CÓDIGO ANTIGUO """

'''
from custom_components.magicswitchbot.switch import MagicSwitchbotSwitch


@asyncio.coroutine
def async_setup(hass, config):
    """MagicSwitchbot platform initialization"""

    @callback
    def async_push_button(call):
        """Define a service to push a button with MagicSwitchbot"""
        
        """We get the entity_id to push from the service parameter"""
        entity_id = call.data.get(ATTR_ENTITY_ID)
        
        """We look for that entity id in our known custom switches list"""
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
        """Once pushed, the switch must get back to _Off_ state"""
        switch._state = False
        switch._last_action = "Push"

    """Register our service with Home Assistant"""
    hass.services.async_register(DOMAIN, 'push', async_push_button)

    """"Return boolean to indicate that initialization was successfully"""
    return True
    
'''
