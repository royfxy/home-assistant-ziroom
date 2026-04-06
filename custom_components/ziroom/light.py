"""Ziroom light"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    LightEntity,
    LightEntityFeature,
    ColorMode,
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
    """Set up Ziroom light from config entry."""
    coordinator: ZiroomDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device_id, data in coordinator.data.items():
        if data["type"] in ["light03", "light04"]:
            entities.append(ZiroomLight(device_id, data, coordinator))
    async_add_entities(entities)

class ZiroomLight(CoordinatorEntity[ZiroomDataUpdateCoordinator], LightEntity):
    """Ziroom light entity."""

    _attr_has_entity_name = True
    _attr_supported_color_modes: set[ColorMode] = {ColorMode.BRIGHTNESS, ColorMode.COLOR_TEMP}
    _attr_supported_features = LightEntityFeature(0)
    _attr_min_mireds = 153
    _attr_max_mireds = 370

    def __init__(self, device_id: str, data: dict, coordinator: ZiroomDataUpdateCoordinator) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._data = data
        self._attr_unique_id = f"ziroom_{device_id}"
        self._attr_name = data["name"]

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
    def is_on(self) -> bool:
        """Return true if light is on."""
        on = self.coordinator.get_device_prop(self._device_id, "set_on_off")
        return on == "1"

    @property
    def brightness(self) -> int | None:
        """Return brightness 0-255."""
        brightness = self.coordinator.get_device_prop(self._device_id, "set_brightness")
        if brightness:
            return int(brightness) * 255 // 100
        return None

    @property
    def color_temp(self) -> int | None:
        """Return color temperature in mireds."""
        temp_k = self.coordinator.get_device_prop(self._device_id, "set_color_tem")
        if temp_k and int(temp_k) > 0:
            return int(1000000 / int(temp_k))
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on light."""
        brightness_percent = None
        color_temp_k = None
        
        if "brightness" in kwargs:
            brightness_percent = int(kwargs["brightness"]) * 100 // 255
        
        if "color_temp" in kwargs:
            color_temp_k = int(1000000 / kwargs["color_temp"])
        
        await self.hass.async_add_executor_job(
            self.coordinator.api.control_light,
            self._device_id,
            True,
            brightness_percent,
            color_temp_k,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off light."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.control_light,
            self._device_id,
            False,
        )
        await self.coordinator.async_request_refresh()
