"""Ziroom (自如) API 客户端

从 homebridge-ziroom 逆向得到的加密协议和 API
"""
import base64
import json
import random
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

import des
import requests


SECRET_KEY = b"vpRZ1kmU"
IV = b"EbpU4WtY"
BASE_URL = "https://ztoread.ziroom.com/"


class ZiroomApiError(Exception):
    """Ziroom API 错误"""
    pass


class ZiroomClient:
    """自如 API 客户端"""

    def __init__(self, token: Optional[str] = None, account: Optional[str] = None, password: Optional[str] = None, hid: Optional[str] = None):
        self.token = token
        self.account = account
        self.password = password
        self.hid = hid or ""
        self.token_expired_at = float("inf")

    def _encode_des(self, plain_text: str) -> str:
        """DES-CBC 加密"""
        cipher = des.CBC.new(SECRET_KEY, des.PAD_PKCS5, IV)
        encrypted = cipher.encrypt(plain_text.encode("utf-8"))
        return encrypted.hex()

    def _decode_des(self, encrypted: str) -> str:
        """DES-CBC 解密"""
        cipher = des.CBC.new(SECRET_KEY, des.PAD_PKCS5, IV)
        decrypted = cipher.decrypt(bytes.fromhex(encrypted))
        return decrypted.decode("utf-8")

    def _get_jwt_payload(self) -> Optional[Dict[str, Any]]:
        """解析 JWT payload"""
        if not self.token or "." not in self.token:
            return None
        try:
            _, payload, _ = self.token.split(".")
            # padding
            padding = 4 - len(payload) % 4
            if padding:
                payload += "=" * padding
            payload_bytes = base64.urlsafe_b64decode(payload)
            return json.loads(payload_bytes)
        except Exception:
            return None

    @property
    def uid(self) -> Optional[str]:
        payload = self._get_jwt_payload()
        return payload.get("uid") if payload else None

    def _create_headers(self, timestamp: int) -> Dict[str, str]:
        """创建请求头"""
        return {
            "token": self.token,
            "User-Agent": "ZiroomerProject/7.14.7 (iPhone; iOS 18.5; Scale/3.00)",
            "Content-Type": "application/json",
            "appType": "1",
            "sys": "app",
            "timestamp": str(timestamp),
            "Request-Id": f"{str(uuid.uuid4())[:8]}:{int(timestamp / 1000)}",
            "Client-Type": "ios",
            "phoneName": "iPhone",
            "osType": "iOS",
            "osVersion": "18.5",
        }

    def login(self, account: str, password: str) -> bool:
        """账号密码登录获取 token
        TODO: 实现登录逻辑，原项目 login 函数只定义了接口没实现？
        原 homebridge-ziroom 中 login 从 /user/login 接口获取 token
        """
        # TODO: 需要补全登录逻辑，目前先支持 token 登录
        raise NotImplementedError("账号密码登录尚未实现，请使用 token 登录")

    async def get_hid(self) -> str:
        """获取房间 id"""
        if self.hid:
            return self.hid
        resp = await self.request("/homeapi/v10/home/queryHomeList", {
            "uid": self.uid,
        })
        if isinstance(resp, list) and len(resp) > 0:
            self.hid = resp[0].get("hid", "")
        return self.hid

    async def request(self, path: str, data: Dict[str, Any]) -> Any:
        """发送请求"""
        timestamp = int(time.time() * 1000)
        body_encrypted = self._encode_des(json.dumps(data))
        url = urljoin(BASE_URL, path)

        headers = self._create_headers(timestamp)

        resp = requests.post(url, headers=headers, data=body_encrypted)
        resp.raise_for_status()

        text = resp.text
        decrypted = self._decode_des(text)
        resp_data = json.loads(decrypted)

        if resp_data.get("code") == "200":
            return resp_data.get("data")

        if resp_data.get("code") == "40005":
            # token 过期，重新登录
            if self.account and self.password:
                for retry in range(3):
                    try:
                        self.login(self.account, self.password)
                        return await self.request(path, data)
                    except ZiroomApiError:
                        continue
            raise ZiroomApiError(f"Token 过期，重试失败: {resp_data.get('message')}")

        raise ZiroomApiError(f"[{path}] {resp_data.get('code')}: {resp_data.get('message')}")

    async def get_device_list(self) -> List[Dict[str, Any]]:
        """获取所有设备列表"""
        hid = await self.get_hid()
        resp = await self.request("/homeapi/v4/homePageDevice/queryAreaDeviceListNew", {
            "uid": self.uid,
            "hid": hid,
            "type": 0,
            "version": 25,
        })
        devices = {}
        for category in resp.get("deviceData", {}).get("deviceList", []):
            for device in category.get("deviceList", []):
                devices[device.get("devUuid")] = device
        return list(devices.values())

    async def get_device_detail(self, dev_uuid: str) -> Dict[str, Any]:
        """获取设备详情"""
        hid = await self.get_hid()
        return await self.request("/homeapi/v3/device/deviceDetailPage", {
            "uid": self.uid,
            "hid": hid,
            "version": 19,
            "devUuid": dev_uuid,
        })

    async def set_device_state(self, dev_uuid: str, prod_op_code: str, param: str) -> Any:
        """设置设备状态"""
        hid = await self.get_hid()
        return await self.request("/homeapi/v2/device/controlDeviceByOperCode", {
            "uid": self.uid,
            "hid": hid,
            "devUuid": dev_uuid,
            "prodOperCode": prod_op_code,
            "param": param,
        })
