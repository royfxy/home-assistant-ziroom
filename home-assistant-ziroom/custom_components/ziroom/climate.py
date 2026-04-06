"""Ziroom 空调支持"""
import logging
from typing import Any, Optional

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    HVACAction,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ZiroomDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# 自如空调操作模式映射
AC_MODE_MAP = {
    "0": HVACMode.HEAT,    # 制热
    "1": HVACMode.COOL,    # 制冷
    "2": HVACMode.AUTO,    # 自动
    "3": HVACMode.DRY,      # 除湿
    "4": HVACMode.FAN_ONLY, # 送风
}

HVAC_MODE_TO_ZIROOM = {v: k for k, v in AC_MODE_MAP.items()}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """从配置条目设置气候实体"""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for device in coordinator.client.devices:
        if device.get("modelCode") == "conditioner02":
            entities.append(ZiroomConditioner(coordinator, device))

    async_add_entities(entities)


class ZiroomConditioner(CoordinatorEntity, ClimateEntity):
    """Ziroom 空调设备"""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: ZiroomDataUpdateCoordinator, device_info):
        super().__init__(coordinator)
        self._device = device_info
        self._dev_uuid = device_info["devUuid"]
        self._attr_unique_id = self._dev_uuid
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._dev_uuid)},
            name=f"{device_info.get('rname', '房间')} - {device_info.get('devName', '空调')}",
            manufacturer="自如",
            model=device_info.get("modelCode", "conditioner02"),
        )
        # 支持的特性
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.FAN_MODE
        )

    @property
    def extra_state_attributes(self):
        """附加属性"""
        device = self.coordinator.data.get(self._dev_uuid, {})
        return {
            "dev_uuid": self._dev_uuid,
            "model_code": self._device.get("modelCode"),
        }

    @property
    def current_temperature(self) -> Optional[float]:
        """当前室内温度"""
        device = self.coordinator.data.get(self._dev_uuid, {})
        props = device.get("props", {})
        temp = props.get("show_inside_tem")
        return float(temp) if temp else None

    @property
    def current_humidity(self) -> Optional[float]:
        """当前湿度"""
        device = self.coordinator.data.get(self._dev_uuid, {})
        props = device.get("props", {})
        hum = props.get("show_inside_hum")
        return float(hum) if hum else None

    @property
    def target_temperature(self) -> Optional[float]:
        """目标温度"""
        device = self.coordinator.data.get(self._dev_uuid, {})
        props = device.get("props", {})
        tem = props.get("set_tem")
        return float(tem) if tem else None

    @property
    def hvac_mode(self) -> HVACMode:
        """当前 HVAC 模式"""
        device = self.coordinator.data.get(self._dev_uuid, {})
        props = device.get("props", {})
        on_off = props.get("set_on_off")
        if on_off != "1":
            return HVACMode.OFF

        mode = props.get("set_mode")
        return AC_MODE_MAP.get(mode, HVACMode.AUTO)

    @property
    def hvac_modes(self):
        """支持的 HVAC 模式"""
        return [
            HVACMode.OFF,
            HVACMode.HEAT,
            HVACMode.COOL,
            HVACMode.AUTO,
            HVACMode.DRY,
            HVACMode.FAN_ONLY,
        ]

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """设置 HVAC 模式"""
        if hvac_mode == HVACMode.OFF:
            await self._set_prop("set_on_off", "0")
            return

        on = await self._get_prop("set_on_off")
        if on != "1":
            await self._set_prop("set_on_off", "1")

        if hvac_mode in HVAC_MODE_TO_ZIROOM:
            mode_code = HVAC_MODE_TO_ZIROOM[hvac_mode]
            await self._set_prop("set_mode", mode_code)
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """设置目标温度"""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is not None:
            await self._set_prop("set_tem", str(round(temp)))
        await self.coordinator.async_request_refresh()

    async def _get_prop(self, prop: str) -> Optional[str]:
        """获取设备属性"""
        detail = await self.coordinator.client.get_device_detail(self._dev_uuid)
        self.coordinator.data[self._dev_uuid] = detail
        return detail.get("props", {}).get(prop)

    async def _set_prop(self, prop: str, value: str) -> None:
        """设置设备属性"""
        # 自如 API prodOperCode 一般对应属性名称
        await self.coordinator.client.set_device_state(self._dev_uuid, prop, value)
