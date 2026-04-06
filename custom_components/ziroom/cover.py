"""Ziroom cover (curtain)"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.cover import (
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ZiroomDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Ziroom cover from config entry."""
    coordinator: ZiroomDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device_id, data in coordinator.data.items():
        if data["type"] == "curtain01":
            entities.append(ZiroomCover(device_id, data, coordinator))
    async_add_entities(entities)

class ZiroomCover(CoordinatorEntity[ZiroomDataUpdateCoordinator], CoverEntity):
    """Ziroom cover entity."""

    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.SET_POSITION
    )

    def __init__(self, device_id: str, data: dict, coordinator: ZiroomDataUpdateCoordinator) -> None:
        """Initialize the cover."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._data = data
        self._attr_unique_id = f"ziroom_{device_id}"
        self._attr_name = data["name"]
        self._attr_has_entity_name = False

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._data["name"],
            manufacturer="自如",
            model=self._data["type"],
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._device_id in self.coordinator.data

    @property
    def current_cover_position(self) -> int | None:
        """Return current position (0-100, 0=closed, 100=open)."""
        position = self.coordinator.get_device_prop(self._device_id, "curtain_opening")
        if position:
            try:
                return int(position)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def is_closed(self) -> bool | None:
        """Return if cover is closed."""
        pos = self.current_cover_position
        if pos is not None:
            return pos == 0
        return None

    @property
    def is_opening(self) -> bool | None:
        """Return if cover is opening."""
        return None

    @property
    def is_closing(self) -> bool | None:
        """Return if cover is closing."""
        return None

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.control_curtain,
            self._device_id,
            None,
            True,
        )
        await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.control_curtain,
            self._device_id,
            None,
            False,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Set the cover position."""
        position = kwargs.get("position")
        if position is not None:
            await self.hass.async_add_executor_job(
                self.coordinator.api.control_curtain,
                self._device_id,
                position,
                None,
            )
            await self.coordinator.async_request_refresh()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        _LOGGER.warning("Stop not supported for Ziroom curtains")
