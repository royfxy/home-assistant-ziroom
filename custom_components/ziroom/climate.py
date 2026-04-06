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

_LOGGER = logging.getLogger(__name__)

HA_HVAC_MODES = {
    0: HVACMode.HEAT,
    1: HVACMode.COOL,
    2: HVACMode.AUTO,
    3: HVACMode.DRY,
    4: HVACMode.FAN_ONLY,
}

FAN_SPEEDS = {
    0: "自动",
    1: "低",
    2: "中",
    3: "高",
}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Ziroom climate from config entry."""
    coordinator: ZiroomDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device_id, data in coordinator.data.items():
        if data["type"] == "conditioner02":
            entities.append(ZiroomClimate(device_id, data, coordinator))
    async_add_entities(entities)

class ZiroomClimate(CoordinatorEntity[ZiroomDataUpdateCoordinator], ClimateEntity):
    """Ziroom climate entity."""

    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, device_id: str, data: dict, coordinator: ZiroomDataUpdateCoordinator) -> None:
        """Initialize the climate."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._data = data
        self._attr_unique_id = f"ziroom_{device_id}"
        self._attr_name = data["name"]
        self._attr_temperature_unit = "°C"
        self._attr_min_temp = 16
        self._attr_max_temp = 30
        self._attr_target_temperature_step = 1
        self._attr_fan_modes = list(FAN_SPEEDS.values())
        self._attr_hvac_modes = [HVACMode.OFF] + list(HA_HVAC_MODES.values())
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
    def current_temperature(self) -> float | None:
        """Return current temperature."""
        temp = self.coordinator.get_device_prop(self._device_id, "conditioner_indoortemp")
        if temp:
            try:
                return float(temp)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return target temperature."""
        temp = self.coordinator.get_device_prop(self._device_id, "conditioner_temper")
        if temp:
            try:
                return float(temp)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac mode."""
        on = self.coordinator.get_device_prop(self._device_id, "conditioner_powerstate")
        if on is None or on != "1":
            return HVACMode.OFF
        mode = self.coordinator.get_device_prop(self._device_id, "conditioner_model")
        if mode:
            try:
                return HA_HVAC_MODES.get(int(mode), HVACMode.AUTO)
            except (ValueError, TypeError):
                pass
        return HVACMode.AUTO

    @property
    def fan_mode(self) -> str | None:
        """Return fan mode."""
        speed = self.coordinator.get_device_prop(self._device_id, "conditioner_windspeed")
        if speed:
            try:
                return FAN_SPEEDS.get(int(speed), "自动")
            except (ValueError, TypeError):
                pass
        return "自动"

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set target temperature."""
        temp = kwargs.get("temperature")
        if temp is not None:
            on = self.hvac_mode != HVACMode.OFF
            mode = self._get_current_mode()
            speed = self._get_current_speed()
            await self.hass.async_add_executor_job(
                self.coordinator.api.control_aircon,
                self._device_id,
                int(temp),
                mode,
                speed,
                on,
            )
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set hvac mode."""
        if hvac_mode == HVACMode.OFF:
            on = False
            mode = 1
        else:
            on = True
            mode = next((k for k, v in HA_HVAC_MODES.items() if v == hvac_mode), 1)
        
        temp = self._get_current_temp()
        speed = self._get_current_speed()
        
        await self.hass.async_add_executor_job(
            self.coordinator.api.control_aircon,
            self._device_id,
            temp,
            mode,
            speed,
            on,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set fan mode."""
        speed = next((k for k, v in FAN_SPEEDS.items() if v == fan_mode), 0)
        on = self.hvac_mode != HVACMode.OFF
        temp = self._get_current_temp()
        mode = self._get_current_mode()
        
        await self.hass.async_add_executor_job(
            self.coordinator.api.control_aircon,
            self._device_id,
            temp,
            mode,
            speed,
            on,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Turn on."""
        on = True
        mode = self._get_current_mode()
        temp = self._get_current_temp()
        speed = self._get_current_speed()
        
        await self.hass.async_add_executor_job(
            self.coordinator.api.control_aircon,
            self._device_id,
            temp,
            mode,
            speed,
            on,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn off."""
        on = False
        mode = self._get_current_mode()
        temp = self._get_current_temp()
        speed = self._get_current_speed()
        
        await self.hass.async_add_executor_job(
            self.coordinator.api.control_aircon,
            self._device_id,
            temp,
            mode,
            speed,
            on,
        )
        await self.coordinator.async_request_refresh()

    def _get_current_temp(self) -> int:
        """Get current target temp."""
        temp = self.coordinator.get_device_prop(self._device_id, "conditioner_temper")
        return int(temp) if temp else 25

    def _get_current_mode(self) -> int:
        """Get current mode."""
        mode = self.coordinator.get_device_prop(self._device_id, "conditioner_model")
        return int(mode) if mode else 1

    def _get_current_speed(self) -> int:
        """Get current speed."""
        speed = self.coordinator.get_device_prop(self._device_id, "conditioner_windspeed")
        return int(speed) if speed else 102
