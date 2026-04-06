#!/usr/bin/env python3
"""
Test script for controlling Ziroom curtains.

Usage:
    python3 test_curtain_control.py                          # List all curtains
    python3 test_curtain_control.py --device <id> --close   # Close curtain
    python3 test_curtain_control.py --device <id> --open    # Open curtain
    python3 test_curtain_control.py --device <id> --position 50  # Set to 50%
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


def list_curtains(api):
    """List all available curtain devices"""
    print("=" * 60)
    print("Finding Curtains")
    print("=" * 60)
    
    devices = api.get_devices()
    curtains = []
    
    for device in devices:
        if device.type in ['curtain01']:
            curtains.append(device)
            print(f"\n  • {device.name}")
            print(f"    ID: {device.id}")
            print(f"    Type: {device.type}")
            
            opening = api.get_device_prop(device.id, 'curtain_opening')
            if opening:
                print(f"    Position: {opening}%")
    
    print(f"\nFound {len(curtains)} curtain(s)")
    return curtains


def control_curtain(api, device_id, open_curtain=None, close_curtain=None, position=None):
    """Control a curtain"""
    print(f"\nControlling curtain: {device_id}")
    
    if close_curtain:
        print(f"  Action: Close (0%)")
        success = api.control_curtain(device_id, on=False)
    elif open_curtain:
        print(f"  Action: Open (100%)")
        success = api.control_curtain(device_id, on=True)
    elif position is not None:
        print(f"  Action: Set to {position}%")
        success = api.control_curtain(device_id, position=position)
    else:
        print("  No action specified")
        return False
    
    if success:
        print(f"  ✓ Control command sent successfully!")
    else:
        print(f"  ✗ Failed to control curtain")
    
    return success


def main():
    parser = argparse.ArgumentParser(description='Test Ziroom Curtain Control')
    parser.add_argument('--token', type=str, help='Ziroom API token (or use ZIROOM_TOKEN in .env)')
    parser.add_argument('--device', type=str, help='Specific device ID to control')
    parser.add_argument('--open', action='store_true', help='Open curtain (100%%)')
    parser.add_argument('--close', action='store_true', help='Close curtain (0%%)')
    parser.add_argument('--position', type=int, choices=range(0, 101), 
                       metavar='0-100', help='Set curtain position (0-100)')
    
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
    
    # List curtains if no action specified
    if not args.device and not args.open and not args.close and args.position is None:
        list_curtains(api)
        print("\n💡 Usage examples:")
        print("   Close curtain:")
        print("   python3 test_curtain_control.py --device <id> --close")
        print("\n   Open curtain:")
        print("   python3 test_curtain_control.py --device <id> --open")
        print("\n   Set to 50%:")
        print("   python3 test_curtain_control.py --device <id> --position 50")
        return
    
    # Get curtains
    curtains = list_curtains(api)
    
    if not curtains:
        print("\n✗ No curtains found!")
        sys.exit(1)
    
    # Control specific device or all devices
    if args.device:
        # Find the specific device
        target_curtain = next((c for c in curtains if c.id == args.device), None)
        if not target_curtain:
            print(f"\n✗ Device not found: {args.device}")
            print("\nAvailable devices:")
            for c in curtains:
                print(f"  - {c.name}: {c.id}")
            sys.exit(1)
        
        control_curtain(api, args.device, open_curtain=args.open, close_curtain=args.close, position=args.position)
    else:
        # Control all curtains
        if not args.open and not args.close and args.position is None:
            print("\n✗ No action specified!")
            sys.exit(1)
        
        print(f"\nControlling all {len(curtains)} curtain(s)...")
        for curtain in curtains:
            control_curtain(api, curtain.id, open_curtain=args.open, close_curtain=args.close, position=args.position)
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
