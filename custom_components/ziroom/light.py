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
from .ziroom_api import Device

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Ziroom light from config entry."""
    coordinator: ZiroomDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device in coordinator.data.values():
        if device.type == "03" or device.type == "04":
            entities.append(ZiroomLight(device, coordinator))
    async_add_entities(entities)

class ZiroomLight(CoordinatorEntity[ZiroomDataUpdateCoordinator], LightEntity):
    """Ziroom light entity."""

    _attr_has_entity_name = True
    _attr_supported_color_modes: set[ColorMode] = {ColorMode.BRIGHTNESS}
    _attr_supported_features = LightEntityFeature(0)

    def __init__(self, device: Device, coordinator: ZiroomDataUpdateCoordinator) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self._device = device
        self._attr_unique_id = f"ziroom_{device.id}"
        self._attr_name = device.name
        if device.type == "04":
            self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        else:
            self._attr_supported_color_modes = {ColorMode.ONOFF}

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device.id)},
            name=self._device.name,
            manufacturer="自如",
            model=self._device.type,
        )

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._device.data.get("on", False)

    @property
    def brightness(self) -> int | None:
        """Return brightness 0-255."""
        brightness = self._device.data.get("brightness", 0)
        return int(brightness * 255 / 100)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on light."""
        brightness = kwargs.get("brightness")
        if brightness is not None:
            brightness_percent = int(brightness * 100 / 255)
        else:
            brightness_percent = self._device.data.get("brightness", 100)
        await self.hass.async_add_executor_job(
            self.coordinator.api.control_light,
            self._device.id,
            True,
            brightness_percent,
        )
        self._device.data["on"] = True
        if brightness_percent is not None:
            self._device.data["brightness"] = brightness_percent
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off light."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.control_light,
            self._device.id,
            False,
        )
        self._device.data["on"] = False
        await self.coordinator.async_request_refresh()