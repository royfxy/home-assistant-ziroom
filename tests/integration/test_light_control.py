#!/usr/bin/env python3
"""
Test script for controlling Ziroom lights.

Usage:
    python3 test_light_control.py                           # List all lights (uses .env)
    python3 test_light_control.py --device <id> --off      # Control specific light (uses .env)
    python3 test_light_control.py --token <token>          # Or specify token directly
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


def list_lights(api):
    """List all available light devices"""
    print("=" * 60)
    print("Finding Light Devices")
    print("=" * 60)
    
    devices = api.get_devices()
    lights = []
    
    for device in devices:
        if device.type in ['light03', 'light04']:
            lights.append(device)
            print(f"\n  • {device.name}")
            print(f"    ID: {device.id}")
            print(f"    Type: {device.type}")
            
            brightness = api.get_device_prop(device.id, 'set_brightness')
            color_temp = api.get_device_prop(device.id, 'set_color_tem')
            on = api.get_device_prop(device.id, 'set_on_off')
            
            if on:
                print(f"    Status: {'ON' if on == '1' else 'OFF'}")
            if brightness:
                print(f"    Brightness: {brightness}%")
            if color_temp:
                print(f"    Color Temp: {color_temp}K")
    
    print(f"\nFound {len(lights)} light device(s)")
    return lights


def control_light(api, device_id, on=None, brightness=None, color_temp=None):
    """Control a specific light"""
    print(f"\nControlling light: {device_id}")
    
    if on is not None:
        print(f"  Power: {'ON' if on else 'OFF'}")
    if brightness is not None:
        print(f"  Brightness: {brightness}%")
    if color_temp is not None:
        print(f"  Color Temp: {color_temp}K")
    
    success = api.control_light(device_id, on=on, brightness=brightness, color_temp=color_temp)
    
    if success:
        print(f"  ✓ Control command sent successfully!")
    else:
        print(f"  ✗ Failed to control light")
    
    return success


def main():
    parser = argparse.ArgumentParser(description='Test Ziroom Light Control')
    parser.add_argument('--token', type=str, help='Ziroom API token (or use ZIROOM_TOKEN in .env)')
    parser.add_argument('--device', type=str, help='Specific device ID to control')
    parser.add_argument('--on', action='store_true', help='Turn light(s) on')
    parser.add_argument('--off', action='store_true', help='Turn light(s) off')
    parser.add_argument('--brightness', type=int, choices=range(0, 101), 
                        metavar='0-100', help='Brightness level (0-100)')
    parser.add_argument('--color-temp', type=int, 
                        help='Color temperature in Kelvin (e.g., 2700=warm, 4000=neutral, 6500=cool)')
    
    args = parser.parse_args()
    
    # Get token from args or .env
    token = args.token or os.getenv('ZIROOM_TOKEN')
    
    if not token:
        print("Error: Token not provided!")
        print("\nPlease either:")
        print("  1. Use --token <your_token>")
        print("  2. Or create a .env file with ZIROOM_TOKEN=your_token")
        print("\nYou can copy .env.example to .env and edit it.")
        sys.exit(1)
    
    # Initialize API
    print("Initializing Ziroom API...")
    api = ZiroomApi(token=token)
    api.login()
    print("✓ API initialized successfully")
    
    # Determine power action
    on = None
    if args.on:
        on = True
    if args.off:
        on = False
    
    # List lights if no action specified
    if args.device is None and on is None and args.brightness is None and args.color_temp is None:
        list_lights(api)
        print("\n💡 Usage examples:")
        print("   Turn off a specific light:")
        print("   python3 test_light_control.py --device <id> --off")
        print("\n   Turn on all lights with brightness and color temp:")
        print("   python3 test_light_control.py --on --brightness 80 --color-temp 4000")
        print("\n   Adjust brightness without changing power:")
        print("   python3 test_light_control.py --device <id> --brightness 50")
        print("\n   Change color temperature:")
        print("   python3 test_light_control.py --device <id> --color-temp 2700")
        return
    
    # Get lights
    lights = list_lights(api)
    
    if not lights:
        print("\n✗ No light devices found!")
        sys.exit(1)
    
    # Control specific device or all devices
    if args.device:
        # Find the specific device
        target_light = next((l for l in lights if l.id == args.device), None)
        if not target_light:
            print(f"\n✗ Device not found: {args.device}")
            print("\nAvailable devices:")
            for l in lights:
                print(f"  - {l.name}: {l.id}")
            sys.exit(1)
        
        control_light(api, args.device, on=on, brightness=args.brightness, color_temp=args.color_temp)
    else:
        # Control all lights
        print(f"\nControlling all {len(lights)} light(s)...")
        for light in lights:
            control_light(api, light.id, on=on, brightness=args.brightness, color_temp=args.color_temp)
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
