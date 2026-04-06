"""Test script to check light device state."""
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
    print("灯设备状态检查")
    print("=" * 80)
    
    for device in devices:
        if device.type in ["light03", "light04"]:
            device_id = device.id
            name = device.name
            
            print(f"\n设备名称: {name}")
            print(f"设备ID: {device_id}")
            
            try:
                device_detail = api.get_device_detail(device_id)
                dev_state_map = device_detail.get("devStateMap", {})
                
                print("dev_state_map:")
                for key, value in dev_state_map.items():
                    print(f"  {key}: {value} (type: {type(value).__name__})")
            except Exception as e:
                print(f"获取设备详情失败: {e}")

if __name__ == "__main__":
    main()
