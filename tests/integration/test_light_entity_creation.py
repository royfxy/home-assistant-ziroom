"""Test script to simulate HA light entity creation."""
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
    print("灯设备实体创建测试")
    print("=" * 80)
    
    lights = []
    for device in devices:
        if device.type in ["light03", "light04"]:
            lights.append(device)
    
    print(f"\n找到 {len(lights)} 个灯设备")
    
    for device in lights:
        device_id = device.id
        name = device.name
        
        print(f"\n设备: {name} ({device_id})")
        
        try:
            detail = api.get_device_detail(device_id)
            dev_state_map = detail.get("devStateMap", {})
            
            has_on_off = any("on_off" in key.lower() for key in dev_state_map.keys())
            has_brightness = any("light_state" in key.lower() for key in dev_state_map.keys())
            has_temp = any("temperature" in key.lower() for key in dev_state_map.keys())
            
            print(f"  电源状态属性: {'有' if has_on_off else '无'}")
            print(f"  亮度属性: {'有' if has_brightness else '无'}")
            print(f"  色温属性: {'有' if has_temp else '无'}")
            
            if has_on_off and has_brightness:
                color_modes = ["BRIGHTNESS"]
                if has_temp:
                    color_modes.append("COLOR_TEMP")
                print(f"  支持的颜色模式: {color_modes}")
                print(f"  ✓ 可以创建实体")
            else:
                print(f"  ✗ 缺少必要属性，无法创建实体")
        except Exception as e:
            print(f"  获取设备详情失败: {e}")

if __name__ == "__main__":
    main()
