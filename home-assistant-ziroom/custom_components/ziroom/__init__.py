"""Ziroom 自如智能设备 Home Assistant 集成"""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN, CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry

from .coordinator import ZiroomDataUpdateCoordinator
from .ziroom_api import ZiroomClient

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ziroom"
CONF_HID = "hid"

PLATFORMS = ["climate", "light"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """设置配置条目"""
    token = entry.data.get(CONF_TOKEN)
    hid = entry.data.get(CONF_HID)

    client = ZiroomClient(token=token, hid=hid)
    coordinator = ZiroomDataUpdateCoordinator(hass, client)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载配置条目"""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
