#!/usr/bin/env python3
"""Test script to verify OneSignal API key validity"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
app_id = os.getenv("ONESIGNAL_MANDIBLE_APP_ID")
api_key = os.getenv("ONESIGNAL_MANDIBLE_API_KEY")

print("OneSignal API Key Validation Test")
print("=" * 50)

if not app_id or not api_key:
    print("❌ ERROR: Missing credentials!")
    print("   Make sure your .env file contains:")
    print("   ONESIGNAL_MANDIBLE_APP_ID=your_app_id")
    print("   ONESIGNAL_MANDIBLE_API_KEY=your_api_key")
    exit(1)

print(f"App ID: {app_id}")
print(f"API Key length: {len(api_key)}")
print(f"API Key prefix: {api_key[:15]}...")

# Determine API key type
is_v2_key = api_key.startswith("os_v2_")
print(f"API Key type: {'v2' if is_v2_key else 'v1'}")

# Set up headers based on key type
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

if is_v2_key:
    headers["Authorization"] = f"Key {api_key}"
    print("Using Authorization: Key <api_key>")
else:
    headers["Authorization"] = f"Basic {api_key}"
    print("Using Authorization: Basic <api_key>")

print("\n" + "=" * 50)
print("Testing API Key validity...")
print("=" * 50)

# Test 1: Get app details (requires valid API key)
print("\n1. Testing app details endpoint (requires valid app-specific API key)...")
url = f"https://api.onesignal.com/api/v1/apps/{app_id}"
params = {}  # No params needed for this endpoint

try:
    response = requests.get(url, headers=headers, params=params)
    print(f"   URL: {url}")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ SUCCESS: API key is valid!")
        data = response.json()
        print(f"   App Name: {data.get('name', 'N/A')}")
        print(f"   Created: {data.get('created_at', 'N/A')}")
    elif response.status_code == 401:
        print("   ❌ FAILED: Authentication error - API key is invalid or doesn't have permission")
        print(f"   Response: {response.text}")
    elif response.status_code == 403:
        print("   ❌ FAILED: Forbidden - API key doesn't have permission for this app")
        print(f"   Response: {response.text}")
    else:
        print(f"   ❌ FAILED: Unexpected status code")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 2: List notifications (requires valid API key with proper permissions)
print("\n2. Testing notifications endpoint...")
url = "https://api.onesignal.com/api/v1/notifications"
params = {"app_id": app_id, "limit": 1}

try:
    response = requests.get(url, headers=headers, params=params)
    print(f"   URL: {url}")
    print(f"   Params: {params}")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ SUCCESS: Can list notifications")
        data = response.json()
        print(f"   Total notifications: {data.get('total_count', 0)}")
    else:
        print(f"   ❌ FAILED: Status {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 3: Check segments endpoint (the one causing issues)
print("\n3. Testing segments endpoint (the problematic one)...")
url = f"https://api.onesignal.com/api/v1/apps/{app_id}/segments"

try:
    response = requests.get(url, headers=headers)
    print(f"   URL: {url}")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ SUCCESS: Can access segments")
        data = response.json()
        print(f"   Segments found: {len(data) if isinstance(data, list) else 'N/A'}")
    else:
        print(f"   ❌ FAILED: Status {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

print("\n" + "=" * 50)
print("Summary:")
print("=" * 50)

if api_key.startswith("os_v2_"):
    print("You're using a v2 API key (starts with 'os_v2_')")
    print("Make sure this key has the necessary permissions in OneSignal dashboard:")
    print("- View App Details")
    print("- View Notifications") 
    print("- View Segments")
    print("\nTo check/update permissions:")
    print("1. Go to OneSignal Dashboard")
    print("2. Navigate to Settings > Keys & IDs")
    print("3. Find your REST API Key")
    print("4. Check the permissions assigned to it")
else:
    print("You're using a v1 API key")
    print("Consider upgrading to a v2 API key for better security and permissions control") 