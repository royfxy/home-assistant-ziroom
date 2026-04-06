"""Ziroom 数据更新协调器"""
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .ziroom_api import ZiroomClient, ZiroomApiError

_LOGGER = logging.getLogger(__name__)


class ZiroomDataUpdateCoordinator(DataUpdateCoordinator):
    """数据更新协调器，定期从 API 获取设备状态"""

    def __init__(self, hass: HomeAssistant, client: ZiroomClient, update_interval: int = 30):
        super().__init__(
            hass,
            _LOGGER,
            name="ziroom",
            update_interval=timedelta(seconds=update_interval),
        )
        self.client = client
        self.devices = []

    async def _async_update_data(self):
        """更新所有设备数据"""
        try:
            self.devices = await self.client.get_device_list()
            device_data = {}
            for device in self.devices:
                detail = await self.client.get_device_detail(device["devUuid"])
                device_data[device["devUuid"]] = detail
            return device_data
        except ZiroomApiError as err:
            raise UpdateFailed(f"更新设备状态失败: {err}") from err
