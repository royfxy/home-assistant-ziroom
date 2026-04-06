"""Test script to simulate HA light entity creation with coordinator."""
from pathlib import Path
import sys
import os

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "custom_components" / "ziroom"))

from ziroom_api import ZiroomApi

env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

def main():
    """Main function."""
    token = os.getenv('ZIROOM_TOKEN')
    
    if not token:
        print("未找到 ZIROOM_TOKEN 环境变量")
        return
    
    api = ZiroomApi(token)
    
    try:
        api.login()
    except Exception as e:
        print(f"登录失败: {e}")
        return
    
    devices = api.get_devices()
    
    print("=" * 80)
    print("灯设备实体创建测试 (模拟 HA)")
    print("=" * 80)
    
    # Simulate coordinator data
    result = {}
    for device in devices:
        try:
            detail = api.get_device_detail(device.id, True)
            result[device.id] = {
                "device": device,
                "detail": detail,
                "name": device.name,
                "type": device.type,
            }
        except Exception as e:
            print(f"获取设备 {device.id} 失败: {e}")
            result[device.id] = {
                "device": device,
                "detail": None,
                "name": device.name,
                "type": device.type,
            }
    
    print(f"\ncoordinator.data 中有 {len(result)} 个设备")
    
    lights = []
    for device_id, data in result.items():
        if data["type"] in ["light03", "light04"]:
            lights.append((device_id, data))
    
    print(f"找到 {len(lights)} 个灯设备")
    
    for device_id, data in lights:
        name = data["name"]
        print(f"\n设备: {name} ({device_id})")
        
        if data["detail"] is None:
            print("  ✗ detail 为 None，无法创建实体")
            continue
        
        dev_state_map = data["detail"].get("devStateMap", {})
        
        has_on_off = any("on_off" in key.lower() for key in dev_state_map.keys())
        has_brightness = any("light_state" in key.lower() for key in dev_state_map.keys())
        
        if has_on_off and has_brightness:
            print(f"  ✓ 有必要属性，可以创建实体")
        else:
            print(f"  ✗ 缺少必要属性")
            print(f"    on_off: {has_on_off}")
            print(f"    light_state: {has_brightness}")

if __name__ == "__main__":
    main()
