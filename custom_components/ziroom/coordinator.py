"""Data update coordinator for Ziroom."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .ziroom_api import ZiroomApi, Device

_LOGGER = logging.getLogger(__name__)

class ZiroomDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Device]]):
    """Data update coordinator for Ziroom."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.api = ZiroomApi(entry.data["token"])
        self.entry = entry

    async def _async_update_data(self) -> dict[str, Device]:
        """Update data."""
        devices = await self.hass.async_add_executor_job(self.api.get_devices)
        return {device.id: device for device in devices}