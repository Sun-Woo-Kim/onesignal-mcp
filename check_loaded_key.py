#!/usr/bin/env python3
"""Check what API key is currently loaded from .env"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the current API key
api_key = os.getenv("ONESIGNAL_MANDIBLE_API_KEY")

print("Currently loaded Mandible API key:")
print(f"Length: {len(api_key) if api_key else 'None'}")
print(f"Prefix: {api_key[:20] if api_key else 'None'}...")
print(f"Suffix: ...{api_key[-10:] if api_key else 'None'}")

# Also check if we can read the .env file directly
print("\nReading .env file directly:")
try:
    with open('.env', 'r') as f:
        for line in f:
            if 'ONESIGNAL_MANDIBLE_API_KEY' in line and not line.strip().startswith('#'):
                key_from_file = line.split('=', 1)[1].strip().strip('"').strip("'")
                print(f"Length: {len(key_from_file)}")
                print(f"Prefix: {key_from_file[:20]}...")
                print(f"Suffix: ...{key_from_file[-10:]}")
                
                if api_key != key_from_file:
                    print("\n⚠️  WARNING: The loaded key differs from what's in .env!")
                    print("   You need to restart the MCP server to load the new key.")
                else:
                    print("\n✅ The loaded key matches what's in .env")
                break
except Exception as e:
    print(f"Error reading .env file: {e}") 