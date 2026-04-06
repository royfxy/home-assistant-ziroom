"""Ziroom API Client"""
import requests
import json
import uuid
from typing import List, Optional, Dict, Any
from Crypto.Cipher import DES
import base64


class Device:
    """Device model"""
    def __init__(self, id: str, name: str, type: str, data: dict):
        self.id = id
        self.name = name
        self.type = type
        self.data = data


class ZiroomApi:
    """Ziroom API Client"""
    SECRET_KEY = b'vpRZ1kmU'
    IV = b'EbpU4WtY'
    
    def __init__(self, token: str = None):
        self.token = token
        self.base_url = "https://ztoread.ziroom.com"
        self.uid = None
        self.hid = None
        self._token_expired_at = float('inf')
        self._device_details_cache: Dict[str, Dict[str, Any]] = {}
    
    def _pad(self, text):
        """Pad text for DES encryption"""
        pad_length = 8 - (len(text) % 8)
        return text + chr(pad_length) * pad_length
    
    def _unpad(self, text):
        """Unpad text after DES decryption"""
        pad_length = ord(text[-1])
        return text[:-pad_length]
    
    def _encode_des(self, plain_text: str) -> str:
        """Encrypt text using DES"""
        cipher = DES.new(self.SECRET_KEY, DES.MODE_CBC, self.IV)
        padded = self._pad(plain_text)
        encrypted = cipher.encrypt(padded.encode('utf-8'))
        return encrypted.hex()
    
    def _decode_des(self, encrypted_hex: str) -> str:
        """Decrypt text using DES"""
        cipher = DES.new(self.SECRET_KEY, DES.MODE_CBC, self.IV)
        encrypted = bytes.fromhex(encrypted_hex)
        decrypted = cipher.decrypt(encrypted)
        return self._unpad(decrypted.decode('utf-8'))
    
    def _get_jwt_payload(self) -> Optional[Dict[str, Any]]:
        """Get payload from JWT token"""
        if not self.token:
            return None
        try:
            _, payload, _ = self.token.split('.')
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            payload_bytes = base64.urlsafe_b64decode(payload)
            return json.loads(payload_bytes.decode('utf-8'))
        except Exception:
            return None
    
    def login(self) -> Optional[str]:
        """
        Initialize API with token.
        
        Returns:
            The token if valid
        """
        if not self.token:
            raise Exception("Please configure token manually.")
        
        payload = self._get_jwt_payload()
        if payload:
            self.uid = payload.get('uid')
            self._token_expired_at = payload.get('exp', float('inf')) * 1000
        
        return self.token
    
    def _create_headers(self, timestamp: int) -> Dict[str, str]:
        """Create request headers"""
        return {
            'token': self.token,
            'User-Agent': 'ZiroomerProject/7.14.7 (iPhone; iOS 18.5; Scale/3.00)',
            'Content-Type': 'application/json',
            'appType': '1',
            'sys': 'app',
            'timestamp': str(timestamp),
            'Request-Id': f"{str(uuid.uuid4())[:8]}:{int(timestamp / 1000)}",
            'Client-Type': 'ios',
            'phoneName': 'iPhone',
            'osType': 'iOS',
            'osVersion': '18.5',
        }
    
    def request(self, path: str, data: Dict[str, Any]) -> Any:
        """Make an API request"""
        import time
        
        if not self.token:
            raise Exception("Not logged in")
        
        timestamp = int(time.time() * 1000)
        body = self._encode_des(json.dumps(data, ensure_ascii=False))
        url = f"{self.base_url}{path}"
        headers = self._create_headers(timestamp)
        
        response = requests.post(url, data=body, headers=headers)
        response.raise_for_status()
        
        encrypted_response = response.text
        decrypted_response = self._decode_des(encrypted_response)
        resp_data = json.loads(decrypted_response)
        
        if resp_data.get('code') == '200':
            return resp_data.get('data')
        elif resp_data.get('code') == '40005':
            raise Exception("Token expired, please re-login")
        else:
            raise Exception(f"[{path}] {resp_data.get('code')}: {resp_data.get('message')}")
    
    def get_hid(self) -> str:
        """Get home ID"""
        if self.hid:
            return self.hid
        
        if not self.uid:
            payload = self._get_jwt_payload()
            if payload:
                self.uid = payload.get('uid')
        
        resp = self.request('/homeapi/v10/home/queryHomeList', {'uid': self.uid})
        if resp and len(resp) > 0:
            self.hid = resp[0].get('hid', '')
        return self.hid
    
    def get_devices(self) -> List[Device]:
        """Get all devices"""
        if not self.token:
            return []
        
        hid = self.get_hid()
        resp = self.request('/homeapi/v4/homePageDevice/queryAreaDeviceListNew', {
            'uid': self.uid,
            'hid': hid,
            'type': 0,
            'version': 25,
        })
        
        devices = []
        if resp and 'deviceData' in resp and 'deviceList' in resp['deviceData']:
            for category in resp['deviceData']['deviceList']:
                if 'deviceList' in category:
                    for item in category['deviceList']:
                        devices.append(Device(
                            id=item.get('devUuid', ''),
                            name=item.get('devName', ''),
                            type=item.get('modelCode', ''),
                            data=item
                        ))
        return devices
    
    def get_device_detail(self, device_id: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Get device detail with caching"""
        if not force_refresh and device_id in self._device_details_cache:
            return self._device_details_cache[device_id]
        
        hid = self.get_hid()
        detail = self.request('/homeapi/v3/device/deviceDetailPage', {
            'uid': self.uid,
            'hid': hid,
            'version': 19,
            'devUuid': device_id,
        })
        
        self._device_details_cache[device_id] = detail
        return detail
    
    def set_device_state(self, device_id: str, prod_oper_code: str, param: str) -> bool:
        """Set device state"""
        hid = self.get_hid()
        try:
            self.request('/homeapi/v2/device/controlDeviceByOperCode', {
                'uid': self.uid,
                'hid': hid,
                'devUuid': device_id,
                'prodOperCode': prod_oper_code,
                'param': param,
            })
            if device_id in self._device_details_cache:
                del self._device_details_cache[device_id]
            return True
        except Exception as e:
            print(f"Set device state error: {e}")
            return False
    
    def _get_device_props(self, device_detail: Dict[str, Any], prop: str) -> Optional[Dict[str, Any]]:
        """Get device property element from device detail"""
        group_info_map = device_detail.get('groupInfoMap', {})
        group_info = group_info_map.get(prop)
        
        if not group_info:
            return None
        
        return group_info
    
    def _set_device_prop(self, device_id: str, prop: str, value: str) -> bool:
        """Set device property by prop name (like TypeScript version)"""
        try:
            device_detail = self.get_device_detail(device_id, force_refresh=True)
            group_info = self._get_device_props(device_detail, prop)
            
            if not group_info:
                print(f"Cannot find property group: {prop}")
                return False
            
            group_type = group_info.get('groupType')
            dev_element_list = group_info.get('devElementList', [])
            
            if group_type == 1:
                element = None
                for e in dev_element_list:
                    if e.get('value') == str(value):
                        element = e
                        break
                if not element:
                    print(f"Cannot find element for value: {value}")
                    return False
                return self.set_device_state(device_id, element.get('prodOperCode'), str(value))
            
            elif group_type == 2:
                if not dev_element_list:
                    print(f"No elements found for group type 2")
                    return False
                element = dev_element_list[0]
                max_value = element.get('maxValue', float('inf'))
                min_value = element.get('minValue', -float('inf'))
                num_value = float(value)
                if num_value < min_value or num_value > max_value:
                    print(f"Value out of range: {value} (min: {min_value}, max: {max_value})")
                    return False
                return self.set_device_state(device_id, element.get('prodOperCode'), str(value))
            
            else:
                print(f"Unsupported group type: {group_type}")
                return False
        
        except Exception as e:
            print(f"Set device prop error: {e}")
            return False
    
    def get_device_prop(self, device_id: str, prop: str) -> Optional[str]:
        """Get device property value"""
        try:
            device_detail = self.get_device_detail(device_id, force_refresh=False)
            dev_state_map = device_detail.get('devStateMap', {})
            return dev_state_map.get(prop)
        except Exception:
            return None
    
    def control_aircon(self, device_id: str, temperature: int = None, mode: int = None, speed: int = None, on: bool = None) -> bool:
        """Control air conditioner"""
        if on is not None:
            success = self._set_device_prop(device_id, 'set_on_off', '1' if on else '0')
            if not success:
                return False
            if not on:
                return True
        
        if temperature is not None:
            success = self._set_device_prop(device_id, 'set_tem', str(temperature))
            if not success:
                return False
        
        if mode is not None:
            success = self._set_device_prop(device_id, 'set_mode', str(mode))
            if not success:
                return False
        
        if speed is not None:
            success = self._set_device_prop(device_id, 'set_wind_speed', str(speed))
            if not success:
                return False
        
        return True
    
    def control_light(self, device_id: str, on: bool = None, brightness: int = None, color_temp: int = None) -> bool:
        """Control light
        
        Args:
            device_id: Light device ID
            on: Turn light on/off
            brightness: Brightness level (0-100)
            color_temp: Color temperature (typically 2700-6500K)
        """
        if on is not None:
            success = self._set_device_prop(device_id, 'set_on_off', '1' if on else '0')
            if not success:
                return False
            if not on:
                return True
        
        if brightness is not None:
            success = self._set_device_prop(device_id, 'set_brightness', str(brightness))
            if not success:
                return False
        
        if color_temp is not None:
            success = self._set_device_prop(device_id, 'set_color_tem', str(color_temp))
            if not success:
                return False
        
        return True
    
    def control_curtain(self, device_id: str, position: int = None, on: bool = None) -> bool:
        """Control curtain
        
        Args:
            device_id: Curtain device ID
            position: Curtain position (0-100, 0=closed, 100=open)
            on: Turn curtain on/off (True=open, False=close)
        """
        prop_name = 'FTB56PZT21ABS1.1_curtain_opening'
        
        if on is not None:
            if on:
                return self._set_device_prop(device_id, prop_name, '100')
            else:
                return self._set_device_prop(device_id, prop_name, '0')
        
        if position is not None:
            position = max(0, min(100, position))
            return self._set_device_prop(device_id, prop_name, str(position))
        
        return False
