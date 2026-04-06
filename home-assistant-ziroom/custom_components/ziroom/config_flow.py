"""Ziroom 配置流"""
import logging

import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_TOKEN, CONF_HID

from .ziroom_api import ZiroomClient, ZiroomApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_TOKEN): str,
    vol.Optional(CONF_HID): str,
})


async def validate_input(hass: HomeAssistant, data: dict) -> dict:
    """验证用户输入，测试能否成功获取设备"""
    token = data[CONF_TOKEN]
    hid = data.get(CONF_HID, "")

    client = ZiroomClient(token=token, hid=hid)

    try:
        devices = await client.get_device_list()
    except ZiroomApiError as err:
        raise CannotConnect(str(err)) from err

    return {"title": "自如", "devices": len(devices)}


class ZiroomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Ziroom 配置流"""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """用户第一步配置"""
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.ConfigEntryAuthFailed):
    """无法连接"""
