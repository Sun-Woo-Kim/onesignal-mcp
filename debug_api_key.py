#!/usr/bin/env python3
"""
Debug script to check API key format and test authentication
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the API credentials
app_id = os.getenv("ONESIGNAL_MANDIBLE_APP_ID", "")
api_key = os.getenv("ONESIGNAL_MANDIBLE_API_KEY", "")
org_key = os.getenv("ONESIGNAL_ORG_API_KEY", "")

print("API Key Debugging")
print("=" * 50)
print(f"App ID: {app_id}")
print(f"REST API Key length: {len(api_key)}")
print(f"REST API Key prefix: {api_key[:10] if api_key else 'None'}")
print(f"Org API Key length: {len(org_key)}")
print(f"Org API Key prefix: {org_key[:10] if org_key else 'None'}")

# Check for common issues
if api_key:
    if api_key.startswith('"') or api_key.endswith('"'):
        print("⚠️  WARNING: API key contains quotes")
    if ' ' in api_key:
        print("⚠️  WARNING: API key contains spaces")
    if '\n' in api_key or '\r' in api_key:
        print("⚠️  WARNING: API key contains newlines")
    if api_key.startswith('Basic '):
        print("⚠️  WARNING: API key already contains 'Basic ' prefix")

# Test segments endpoint with REST API key
print("\n1. Testing segments endpoint with REST API key...")
url = f"https://api.onesignal.com/apps/{app_id}/segments"
headers = {
    "Authorization": f"Basic {api_key}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

print(f"URL: {url}")

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Response status: {response.status_code}")
    print(f"Response: {response.text[:500] if response.text else 'Empty response'}")
    
    if response.status_code == 200:
        print("✅ Segments endpoint working with REST API key!")
    else:
        print("❌ Segments endpoint failed with REST API key")
except Exception as e:
    print(f"❌ Request failed: {str(e)}")

# Test app details endpoint with Org API key
print("\n2. Testing app details endpoint with Org API key...")
url = f"https://api.onesignal.com/apps/{app_id}"
headers = {
    "Authorization": f"Basic {org_key}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

print(f"URL: {url}")

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ App details endpoint working with Org API key!")
    else:
        print(f"❌ App details endpoint failed: {response.text[:200]}")
except Exception as e:
    print(f"❌ Request failed: {str(e)}")

# Test templates endpoint
print("\n3. Testing templates endpoint with REST API key...")
url = f"https://api.onesignal.com/apps/{app_id}/templates"
headers = {
    "Authorization": f"Basic {api_key}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

print(f"URL: {url}")

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Templates endpoint working with REST API key!")
    else:
        print(f"❌ Templates endpoint failed: {response.text[:200]}")
except Exception as e:
    print(f"❌ Request failed: {str(e)}") 