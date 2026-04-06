"""Data update coordinator for Ziroom."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Dict, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .ziroom_api import ZiroomApi, Device

_LOGGER = logging.getLogger(__name__)

class ZiroomDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Dict[str, Any]]]):
    """Data update coordinator for Ziroom."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=5),
        )
        self.api = ZiroomApi(token=entry.data["token"])
        self.entry = entry
        self._devices_raw: Dict[str, Device] = {}
        
    async def async_config_entry_first_refresh(self) -> None:
        """Perform the first refresh and log in."""
        await self.hass.async_add_executor_job(self.api.login)
        await super().async_config_entry_first_refresh()

    async def _async_update_data(self) -> dict[str, Dict[str, Any]]:
        """Update data."""
        devices = await self.hass.async_add_executor_job(self.api.get_devices)
        self._devices_raw = {device.id: device for device in devices}
        
        result: Dict[str, Dict[str, Any]] = {}
        for device in devices:
            try:
                detail = await self.hass.async_add_executor_job(
                    self.api.get_device_detail, device.id, True
                )
                result[device.id] = {
                    "device": device,
                    "detail": detail,
                    "name": device.name,
                    "type": device.type,
                }
            except Exception as e:
                _LOGGER.error(f"Failed to get detail for {device.id}: {e}")
                result[device.id] = {
                    "device": device,
                    "detail": None,
                    "name": device.name,
                    "type": device.type,
                }
        return result
    
    def get_device_prop(self, device_id: str, prop_name: str) -> Any:
        """Get device property from state map.
        
        If prop_name is a suffix (e.g., "on_off"), it will search for any key
        ending with that suffix. If prop_name is a full key, it will match exactly.
        """
        if device_id not in self.data:
            return None
        detail = self.data[device_id].get("detail")
        if not detail or "devStateMap" not in detail:
            return None
        dev_state_map = detail["devStateMap"]
        
        if prop_name in dev_state_map:
            return dev_state_map.get(prop_name)
        
        for key in dev_state_map.keys():
            if key.endswith(prop_name):
                return dev_state_map.get(key)
        
        return None