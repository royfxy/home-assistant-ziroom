"""Ziroom API Client"""
import requests
import json
from typing import List

class Device:
    """Device model"""
    def __init__(self, id: str, name: str, type: str, data: dict):
        self.id = id
        self.name = name
        self.type = type
        self.data = data

class ZiroomApi:
    """Ziroom API Client"""
    def __init__(self, token: str = None):
        self.token = token
        self.base_url = "https://if.izira.com/api"

    def login(self, username: str, password: str) -> str | None:
        """Login and get token"""
        url = f"{self.base_url}/v2/user/login"
        payload = {
            "mobile": username,
            "password": password,
        }
        response = requests.post(url, json=payload)
        data = response.json()
        if data.get("code") == 200 and data.get("data"):
            self.token = data["data"]["token"]
            return self.token
        return None

    def get_devices(self) -> List[Device]:
        """Get all devices"""
        if not self.token:
            return []
        url = f"{self.base_url}/v2/device/list"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        devices = []
        if data.get("code") == 200 and data.get("data"):
            for item in data["data"]:
                devices.append(Device(
                    id=str(item["deviceId"]),
                    name=item["deviceName"],
                    type=item["deviceType"],
                    data=item
                ))
        return devices

    def control_aircon(self, device_id: str, temperature: int, mode: int, speed: int, on: bool) -> bool:
        """Control air conditioner"""
        if not self.token:
            return False
        url = f"{self.base_url}/v2/device/aircon/control"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        payload = {
            "deviceId": device_id,
            "temperature": temperature,
            "mode": mode,
            "windSpeed": speed,
            "on": on
        }
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        return data.get("code") == 200

    def control_light(self, device_id: str, on: bool, brightness: int = None) -> bool:
        """Control light"""
        if not self.token:
            return False
        url = f"{self.base_url}/v2/device/light/control"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        payload = {
            "deviceId": device_id,
            "on": on,
        }
        if brightness is not None:
            payload["brightness"] = brightness
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        return data.get("code") == 200