"""Ziroom sensor entities."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ZiroomDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Ziroom sensors from config entry."""
    coordinator: ZiroomDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device_id, data in coordinator.data.items():
        if data["type"] == "conditioner02":
            entities.append(ZiroomTemperatureSensor(device_id, data, coordinator, "conditioner_indoortemp", "室内温度"))
            entities.append(ZiroomTemperatureSensor(device_id, data, coordinator, "conditioner_outdoortemp", "室外温度"))
    async_add_entities(entities)


class ZiroomTemperatureSensor(CoordinatorEntity[ZiroomDataUpdateCoordinator], SensorEntity):
    """Ziroom temperature sensor entity."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, device_id: str, data: dict, coordinator: ZiroomDataUpdateCoordinator, prop_name: str, name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._data = data
        self._prop_name = prop_name
        self._attr_unique_id = f"ziroom_{device_id}_{prop_name}"
        self._attr_name = f"{data['name']} {name}"
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
    def native_value(self) -> float | None:
        """Return the current value."""
        temp = self.coordinator.get_device_prop(self._device_id, self._prop_name)
        if temp:
            try:
                return float(temp)
            except (ValueError, TypeError):
                pass
        return None
