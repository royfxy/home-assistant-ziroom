#!/usr/bin/env python3
"""
Test script for Ziroom API Client.

Usage:
    python3 test_ziroom_api.py                    # Run basic tests
    python3 test_ziroom_api.py --integration      # Run API integration tests (uses .env)
    python3 test_ziroom_api.py --token <token>    # Or specify token directly
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

from ziroom_api import ZiroomApi, Device


def test_basic_functionality():
    """Test basic API functionality without actual network calls"""
    print("=" * 60)
    print("Running Basic Functionality Tests")
    print("=" * 60)
    
    # Test 1: Create API instance
    print("\n1. Testing API instance creation...")
    api = ZiroomApi()
    assert api is not None, "Failed to create ZiroomApi instance"
    print("   ✓ API instance created successfully")
    
    # Test 2: Check required methods exist
    print("\n2. Checking required methods...")
    required_methods = [
        'login',
        'get_devices',
        'get_hid',
        'get_device_detail',
        'set_device_state',
        'control_aircon',
        'control_light',
        '_encode_des',
        '_decode_des',
    ]
    for method in required_methods:
        assert hasattr(api, method), f"Method {method} not found"
        print(f"   ✓ {method}() exists")
    
    # Test 3: Test DES encryption/decryption
    print("\n3. Testing DES encryption/decryption...")
    test_text = '{"test": "data", "uid": 12345}'
    encrypted = api._encode_des(test_text)
    assert encrypted != test_text, "Encryption failed"
    decrypted = api._decode_des(encrypted)
    assert decrypted == test_text, f"Decryption failed: expected '{test_text}', got '{decrypted}'"
    print("   ✓ DES encryption/decryption works correctly")
    
    # Test 4: Test Device class
    print("\n4. Testing Device class...")
    device_data = {
        'devUuid': 'test-uuid-123',
        'devName': '测试空调',
        'modelCode': 'conditioner02',
        'other': 'data'
    }
    device = Device(
        id=device_data['devUuid'],
        name=device_data['devName'],
        type=device_data['modelCode'],
        data=device_data
    )
    assert device.id == 'test-uuid-123'
    assert device.name == '测试空调'
    assert device.type == 'conditioner02'
    assert device.data == device_data
    print("   ✓ Device class works correctly")
    
    print("\n" + "=" * 60)
    print("✅ All Basic Tests Passed!")
    print("=" * 60)
    return True


def test_api_with_token(token):
    """Test actual API calls with a valid token"""
    print("\n" + "=" * 60)
    print("Running API Integration Tests")
    print("=" * 60)
    
    api = ZiroomApi(token=token)
    
    # Test 1: Login
    print("\n1. Testing login...")
    try:
        result = api.login()
        assert result == token, "Login failed"
        print(f"   ✓ Login successful, uid: {api.uid}")
    except Exception as e:
        print(f"   ✗ Login failed: {e}")
        return False
    
    # Test 2: Get HID
    print("\n2. Testing get_hid()...")
    try:
        hid = api.get_hid()
        print(f"   ✓ Got HID: {hid}")
    except Exception as e:
        print(f"   ✗ Failed to get HID: {e}")
        return False
    
    # Test 3: Get devices
    print("\n3. Testing get_devices()...")
    try:
        devices = api.get_devices()
        print(f"   ✓ Found {len(devices)} device(s):")
        for i, device in enumerate(devices, 1):
            print(f"     {i}. {device.name} ({device.type}) - {device.id}")
    except Exception as e:
        print(f"   ✗ Failed to get devices: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All API Integration Tests Passed!")
    print("=" * 60)
    return True


def main():
    parser = argparse.ArgumentParser(description='Test Ziroom API Client')
    parser.add_argument('--token', type=str, help='Ziroom API token (or use ZIROOM_TOKEN in .env)')
    parser.add_argument('--integration', action='store_true', help='Run API integration tests')
    
    args = parser.parse_args()
    
    # Always run basic tests
    basic_passed = test_basic_functionality()
    
    # Run integration tests if requested
    if args.integration or args.token:
        # Get token from args or .env
        token = args.token or os.getenv('ZIROOM_TOKEN')
        
        if not token:
            print("\nError: Token not provided for integration tests!")
            print("\nPlease either:")
            print("  1. Use --token <your_token>")
            print("  2. Or use --integration and set ZIROOM_TOKEN in .env")
            print("\nYou can copy .env.example to .env and edit it.")
            sys.exit(1)
        
        print("\n" * 2)
        integration_passed = test_api_with_token(token)
        if not integration_passed:
            sys.exit(1)
    else:
        print("\n" + "💡 Tip: Use --integration or --token <your_token> to run API integration tests")
        print("       Or create a .env file with ZIROOM_TOKEN=your_token")
    
    if not basic_passed:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
