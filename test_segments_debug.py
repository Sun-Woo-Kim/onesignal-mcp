#!/usr/bin/env python3
"""Debug script to test the segments endpoint with detailed output"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
app_id = os.getenv("ONESIGNAL_MANDIBLE_APP_ID")
api_key = os.getenv("ONESIGNAL_MANDIBLE_API_KEY")

print(f"App ID: {app_id}")
print(f"API Key type: {'v2' if api_key.startswith('os_v2_') else 'v1'}")
print(f"API Key prefix: {api_key[:15]}...")

# Try different authentication methods
url = f"https://api.onesignal.com/apps/{app_id}/segments"
print(f"\nTesting URL: {url}")

# Test 1: Using 'Key' authorization for v2 API key
headers1 = {
    "Authorization": f"Key {api_key}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

print("\n1. Testing with 'Key' authorization header...")
try:
    response = requests.get(url, headers=headers1)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Using 'Basic' authorization
headers2 = {
    "Authorization": f"Basic {api_key}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

print("\n2. Testing with 'Basic' authorization header...")
try:
    response = requests.get(url, headers=headers2)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Without app_id in URL path (using query param)
url2 = "https://api.onesignal.com/segments"
params = {"app_id": app_id}

print(f"\n3. Testing with app_id as query param: {url2}")
print(f"Params: {params}")
try:
    response = requests.get(url2, headers=headers1, params=params)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}") 