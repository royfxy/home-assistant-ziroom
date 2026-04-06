#!/usr/bin/env python3
"""
Test script for controlling Ziroom air conditioners.

Usage:
    python3 test_aircon_control.py                          # List all AC units
    python3 test_aircon_control.py --device <id> --off     # Turn off AC
    python3 test_aircon_control.py --device <id> --on      # Turn on AC
    python3 test_aircon_control.py --device <id> --temp 24 --mode 1 --speed 2
"""

import sys
import argparse
import os
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'custom_components' / 'ziroom'))

from dotenv import load_dotenv
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

from ziroom_api import ZiroomApi


AC_MODES = {
    0: '制热 (Heat)',
    1: '制冷 (Cool)',
    2: '自动 (Auto)',
    3: '除湿 (Dehum)',
    4: '送风 (Wind)',
}


def list_aircons(api):
    """List all available air conditioner devices"""
    print("=" * 60)
    print("Finding Air Conditioners")
    print("=" * 60)
    
    devices = api.get_devices()
    aircons = []
    
    for device in devices:
        if device.type in ['conditioner02']:
            aircons.append(device)
            print(f"\n  • {device.name}")
            print(f"    ID: {device.id}")
            print(f"    Type: {device.type}")
            
            on = api.get_device_prop(device.id, 'set_on_off')
            temp = api.get_device_prop(device.id, 'set_tem')
            mode = api.get_device_prop(device.id, 'set_mode')
            speed = api.get_device_prop(device.id, 'set_wind_speed')
            inside_temp = api.get_device_prop(device.id, 'show_inside_tem')
            inside_hum = api.get_device_prop(device.id, 'show_inside_hum')
            
            print(f"    Status: {'ON' if on == '1' else 'OFF'}")
            if inside_temp:
                print(f"    Indoor Temp: {inside_temp}°C")
            if inside_hum:
                print(f"    Indoor Humidity: {inside_hum}%")
            if temp:
                print(f"    Set Temp: {temp}°C")
            if mode and mode in AC_MODES:
                print(f"    Mode: {AC_MODES[int(mode)]}")
            if speed:
                print(f"    Wind Speed: {speed}")
    
    print(f"\nFound {len(aircons)} air conditioner(s)")
    return aircons


def control_aircon(api, device_id, on=None, temp=None, mode=None, speed=None):
    """Control an air conditioner"""
    print(f"\nControlling AC: {device_id}")
    
    if on is not None:
        print(f"  Power: {'ON' if on else 'OFF'}")
    if temp is not None:
        print(f"  Temperature: {temp}°C")
    if mode is not None:
        mode_desc = AC_MODES.get(mode, f'Unknown ({mode})')
        print(f"  Mode: {mode_desc}")
    if speed is not None:
        print(f"  Wind Speed: {speed}")
    
    success = api.control_aircon(device_id, temperature=temp, mode=mode, speed=speed, on=on)
    
    if success:
        print(f"  ✓ Control command sent successfully!")
    else:
        print(f"  ✗ Failed to control AC")
    
    return success


def main():
    parser = argparse.ArgumentParser(description='Test Ziroom Air Conditioner Control')
    parser.add_argument('--token', type=str, help='Ziroom API token (or use ZIROOM_TOKEN in .env)')
    parser.add_argument('--device', type=str, help='Specific device ID to control')
    parser.add_argument('--on', action='store_true', help='Turn AC on')
    parser.add_argument('--off', action='store_true', help='Turn AC off')
    parser.add_argument('--temp', type=int, help='Set temperature (16-30)')
    parser.add_argument('--mode', type=int, choices=[0, 1, 2, 3, 4], 
                       help='Set mode: 0=Heat, 1=Cool, 2=Auto, 3=Dehum, 4=Wind')
    parser.add_argument('--speed', type=int, help='Set wind speed (1-5)')
    
    args = parser.parse_args()
    
    # Get token from args or .env
    token = args.token or os.getenv('ZIROOM_TOKEN')
    
    if not token:
        print("Error: Token not provided!")
        print("\nPlease either:")
        print("  1. Use --token <your_token>")
        print("  2. Or create a .env file with ZIROOM_TOKEN=your_token")
        sys.exit(1)
    
    # Initialize API
    print("Initializing Ziroom API...")
    api = ZiroomApi(token=token)
    api.login()
    print("✓ API initialized successfully")
    
    # List ACs if no action specified
    if not args.device and not args.on and not args.off and args.temp is None and args.mode is None and args.speed is None:
        list_aircons(api)
        print("\n💡 Usage examples:")
        print("   Turn off AC:")
        print("   python3 test_aircon_control.py --device <id> --off")
        print("\n   Turn on AC with settings:")
        print("   python3 test_aircon_control.py --device <id> --on --temp 24 --mode 1 --speed 2")
        return
    
    # Get aircons
    aircons = list_aircons(api)
    
    if not aircons:
        print("\n✗ No air conditioners found!")
        sys.exit(1)
    
    # Determine action
    on = None
    if args.on:
        on = True
    if args.off:
        on = False
    
    # Control specific device or all devices
    if args.device:
        # Find the specific device
        target_ac = next((a for a in aircons if a.id == args.device), None)
        if not target_ac:
            print(f"\n✗ Device not found: {args.device}")
            print("\nAvailable devices:")
            for a in aircons:
                print(f"  - {a.name}: {a.id}")
            sys.exit(1)
        
        control_aircon(api, args.device, on=on, temp=args.temp, mode=args.mode, speed=args.speed)
    else:
        # Control all aircons
        if on is None and args.temp is None and args.mode is None and args.speed is None:
            print("\n✗ No action specified!")
            sys.exit(1)
        
        print(f"\nControlling all {len(aircons)} AC(s)...")
        for ac in aircons:
            control_aircon(api, ac.id, on=on, temp=args.temp, mode=args.mode, speed=args.speed)
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
