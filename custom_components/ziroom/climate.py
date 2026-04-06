"""Ziroom climate (air conditioner)"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ZiroomDataUpdateCoordinator
from .ziroom_api import Device

_LOGGER = logging.getLogger(__name__)

HA_HVAC_MODES = {
    0: HVACMode.OFF,
    1: HVACMode.COOL,
    2: HVACMode.HEAT,
    3: HVACMode.FAN_ONLY,
    4: HVACMode.DRY,
    5: HVACMode.AUTO,
}

FAN_SPEEDS = {
    1: "低",
    2: "中",
    3: "高",
    0: "自动",
}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Ziroom climate from config entry."""
    coordinator: ZiroomDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device in coordinator.data.values():
        if device.type == "02":
            entities.append(ZiroomClimate(device, coordinator))
    async_add_entities(entities)

class ZiroomClimate(CoordinatorEntity[ZiroomDataUpdateCoordinator], ClimateEntity):
    """Ziroom climate entity."""

    _attr_has_entity_name = True
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, device: Device, coordinator: ZiroomDataUpdateCoordinator) -> None:
        """Initialize the climate."""
        super().__init__(coordinator)
        self._device = device
        self._attr_unique_id = f"ziroom_{device.id}"
        self._attr_name = device.name
        self._attr_temperature_unit = "°C"
        self._attr_min_temp = 16
        self._attr_max_temp = 30
        self._attr_target_temperature_step = 1
        self._attr_fan_modes = list(FAN_SPEEDS.values())

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
    def current_temperature(self) -> float | None:
        """Return current temperature."""
        return self._device.data.get("currentTemperature")

    @property
    def target_temperature(self) -> float | None:
        """Return target temperature."""
        return self._device.data.get("targetTemperature")

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac mode."""
        if not self._device.data.get("on"):
            return HVACMode.OFF
        mode = self._device.data.get("mode", 0)
        return HA_HVAC_MODES.get(mode, HVACMode.OFF)

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return all hvac modes."""
        return list(HA_HVAC_MODES.values())

    @property
    def fan_mode(self) -> str | None:
        """Return fan mode."""
        speed = self._device.data.get("windSpeed", 0)
        return FAN_SPEEDS.get(speed, "自动")

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set target temperature."""
        temp = kwargs.get("temperature")
        if temp is not None:
            await self.hass.async_add_executor_job(
                self.coordinator.api.control_aircon,
                self._device.id,
                int(temp),
                self._device.data.get("mode", 1),
                self._device.data.get("windSpeed", 1),
                self._device.data.get("on", True),
            )
            self._device.data["targetTemperature"] = int(temp)
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set hvac mode."""
        if hvac_mode == HVACMode.OFF:
            on = False
        else:
            on = True
        mode = next(k for k, v in HA_HVAC_MODES.items() if v == hvac_mode)
        await self.hass.async_add_executor_job(
            self.coordinator.api.control_aircon,
            self._device.id,
            self._device.data.get("targetTemperature", 25),
            mode,
            self._device.data.get("windSpeed", 1),
            on,
        )
        self._device.data["on"] = on
        self._device.data["mode"] = mode
        await self.coordinator.async_request_refresh()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set fan mode."""
        speed = next(k for k, v in FAN_SPEEDS.items() if v == fan_mode)
        await self.hass.async_add_executor_job(
            self.coordinator.api.control_aircon,
            self._device.id,
            self._device.data.get("targetTemperature", 25),
            self._device.data.get("mode", 1),
            speed,
            self._device.data.get("on", True),
        )
        self._device.data["windSpeed"] = speed
        await self.coordinator.async_request_refresh()