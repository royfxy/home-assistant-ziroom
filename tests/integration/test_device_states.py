"""Test script to print device states."""
from pathlib import Path
import sys
import os
import argparse

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "custom_components" / "ziroom"))

from ziroom_api import ZiroomApi

env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

def translate_curtain_state(key: str, value: str) -> str:
    """Translate curtain device state."""
    translations = {
        'FTB56PZT21ABS1.1_curtain_opening': ('窗帘开度', value),
        'bs_on_switch_change': ('开关状态', value),
    }
    return translations.get(key, (key, value))

def translate_aircon_state(key: str, value: str) -> str:
    """Translate air conditioner device state."""
    translations = {
        'conditioner_temper': ('目标温度', f"{value}°C"),
        'conditioner_powerstate': ('电源状态', '开启' if value == '1' else '关闭'),
        'conditioner_model': ('运行模式', {
            '0': '制热', '1': '制冷', '2': '自动', '3': '除湿', '4': '送风'
        }.get(value, f"未知({value})")),
        'conditioner_outdoortemp': ('室外温度', f"{value}°C"),
        'conditioner_indoortemp': ('室内温度', f"{value}°C"),
        'conditioner_direction1': ('导风状态', {
            '0': '自动', '1': '固定上', '2': '固定中', '3': '固定下', '4': '扫风'
        }.get(value, f"未知({value})")),
        'conditioner_dry': ('除湿模式', '开启' if value == '1' else '关闭'),
        'conditioner_windspeed': ('风速', {
            '102': '自动', '40': '低', '60': '中', '80': '高'
        }.get(value, f"未知({value})")),
    }
    return translations.get(key, (key, value))

def translate_light_state(key: str, value: str) -> str:
    """Translate light device state."""
    translations = {
        'ZH-D01002021_temperature': ('色温', f"{value}K"),
        'ZH-D01002021_on_off': ('电源状态', '开启' if value == '1' else '关闭'),
        'ZH-D01002021_light_state': ('亮度', f"{value}%"),
        'ZH-D02002021_temperature': ('色温', f"{value}K"),
        'ZH-D02002021_on_off': ('电源状态', '开启' if value == '1' else '关闭'),
        'ZH-D02002021_light_state': ('亮度', f"{value}%"),
        'ZH-D03022022_temperature': ('色温', f"{value}K"),
        'ZH-D03022022_on_off': ('电源状态', '开启' if value == '1' else '关闭'),
        'ZH-D03022022_light_state': ('亮度', f"{value}%"),
        'ZH-D00002021_temperature': ('色温', f"{value}K"),
        'ZH-D00002021_on_off': ('电源状态', '开启' if value == '1' else '关闭'),
        'ZH-D00002021_light_state': ('亮度', f"{value}%"),
        'ZH-D00012021_temperature': ('色温', f"{value}K"),
        'ZH-D00012021_on_off': ('电源状态', '开启' if value == '1' else '关闭'),
        'ZH-D00012021_light_state': ('亮度', f"{value}%"),
    }
    return translations.get(key, (key, value))

def translate_other_state(key: str, value: str) -> str:
    """Translate other device states."""
    translations = {
        'ZH-C0101_voice_switchstate': ('语音开关', '开启' if value == '1' else '关闭'),
        'ZH-C0101_lcd_sleep': ('LCD睡眠', value),
        'ZH-C0101_lightsensor': ('光感', value),
        'zh_c0101_switchstate2': ('开关状态2', value),
        'ZH-C0101_nearest_switchstate': ('最近开关', '开启' if value == '1' else '关闭'),
        'ZH-C0101_pir_switchstate': ('人体感应', '开启' if value == '1' else '关闭'),
        'zh_c0101_switchstate': ('开关状态', value),
        'ZH-C0101_multi_switchstate': ('多键开关', value),
        'battery_state': ('电池状态', f"{value}%"),
        'lock_state': ('锁状态', {
            '11': '反锁', '12': '关', '13': '开', '14': '童锁'
        }.get(value, f"未知({value})")),
        'yg0002_warning_state': ('告警状态', value),
        'E321V04022A_alarmed_change': ('告警状态', '触发' if value == '1' else '正常'),
        'wsdl_low_battery_change': ('低电量', '是' if value == '1' else '否'),
        'E321V04022A_batterystate_state': ('电池状态', f"{value}%"),
        'E321V04022B_gas_alarmed': ('燃气告警', '触发' if value == '1' else '正常'),
        'E321V04022B_trouble_change': ('故障状态', '有故障' if value == '1' else '正常'),
        'wsdl_smokealarm_batterystate': ('电池状态', f"{value}%"),
        'E321V040228_trouble_change': ('故障状态', '有故障' if value == '1' else '正常'),
        'E321V040228_alarmed': ('烟雾告警', '触发' if value == '1' else '正常'),
        'yg_low_battery_change': ('低电量', '是' if value == '1' else '否'),
        'max_light': ('最大亮度', value),
    }
    return translations.get(key, (key, value))

def translate_state(device_type: str, key: str, value: str) -> tuple[str, str]:
    """Translate device state based on device type."""
    if device_type == 'curtain01':
        return translate_curtain_state(key, value)
    elif device_type == 'conditioner02':
        return translate_aircon_state(key, value)
    elif device_type == 'light03':
        return translate_light_state(key, value)
    else:
        return translate_other_state(key, value)

def print_device_state(api: ZiroomApi, device_id: str):
    """Print state of a specific device."""
    try:
        device_detail = api.get_device_detail(device_id)
        dev_state_map = device_detail.get("devStateMap", {})
        
        print("设备状态:")
        for key, value in dev_state_map.items():
            readable_key, readable_value = translate_state(device_detail.get('modelCode', ''), key, value)
            print(f"  {readable_key}: {readable_value} [{value}]")
    except Exception as e:
        print(f"获取设备详情失败: {e}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='打印设备状态')
    parser.add_argument('device_id', nargs='?', help='设备ID，不提供则打印所有设备状态')
    
    args = parser.parse_args()
    
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
    
    if args.device_id:
        devices = [d for d in api.get_devices() if d.id == args.device_id]
        if not devices:
            print(f"未找到设备ID: {args.device_id}")
            return
    else:
        devices = api.get_devices()
    
    print("=" * 80)
    print("设备状态列表")
    print("=" * 80)
    
    if not devices:
        print("未找到任何设备")
        return
    
    for device in devices:
        device_id = device.id
        device_type = device.type
        name = device.name
        
        print(f"\n设备名称: {name}")
        print(f"设备ID: {device_id}")
        print(f"设备类型: {device_type}")
        
        print_device_state(api, device_id)
        
        print("-" * 80)

if __name__ == "__main__":
    main()
