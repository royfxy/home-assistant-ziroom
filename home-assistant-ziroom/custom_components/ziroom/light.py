"""Ziroom 灯支持"""
import logging
from typing import Any, Optional

from homeassistant.components.light import LightEntity, ColorMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ZiroomDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """从配置条目设置灯实体"""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for device in coordinator.client.devices:
        model = device.get("modelCode")
        if model in ("light03", "light04"):
            entities.append(ZiroomLight(coordinator, device))

    async_add_entities(entities)


class ZiroomLight(CoordinatorEntity, LightEntity):
    """Ziroom 灯设备"""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, coordinator: ZiroomDataUpdateCoordinator, device_info):
        super().__init__(coordinator)
        self._device = device_info
        self._dev_uuid = device_info["devUuid"]
        self._attr_unique_id = self._dev_uuid
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._dev_uuid)},
            name=f"{device_info.get('rname', '房间')} - {device_info.get('devName', '灯')}",
            manufacturer="自如",
            model=device_info.get("modelCode"),
        )
        # 判断是否支持亮度
        self._attr_supported_color_modes = {ColorMode.ONOFF}
        self._attr_color_mode = ColorMode.ONOFF
        # TODO: light04 是否支持亮度？可以后续看需求加

    @property
    def is_on(self) -> bool:
        """灯是否打开"""
        device = self.coordinator.data.get(self._dev_uuid, {})
        props = device.get("props", {})
        # 根据原项目代码，开灯是 set_on_off = 1
        on_off = props.get("set_on_off")
        return on_off == "1"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """开灯"""
        await self._set_prop("set_on_off", "1")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """关灯"""
        await self._set_prop("set_on_off", "0")
        await self.coordinator.async_request_refresh()

    async def _get_prop(self, prop: str) -> Optional[str]:
        """获取设备属性"""
        detail = await self.coordinator.client.get_device_detail(self._dev_uuid)
        self.coordinator.data[self._dev_uuid] = detail
        return detail.get("props", {}).get(prop)

    async def _set_prop(self, prop: str, value: str) -> None:
        """设置设备属性"""
        await self.coordinator.client.set_device_state(self._dev_uuid, prop, value)
