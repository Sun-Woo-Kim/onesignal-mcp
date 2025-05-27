#!/usr/bin/env python3
"""
Test script to verify the authentication fix for OneSignal MCP server
"""

import asyncio
import json
import logging
import os
from onesignal_server import (
    view_segments, 
    view_templates,
    get_current_app,
    app_configs,
    make_onesignal_request,
    logger
)

# Enable DEBUG logging
logging.basicConfig(level=logging.DEBUG)
logger.setLevel(logging.DEBUG)

async def test_direct_api_call():
    """Test direct API call to debug the issue"""
    print("\nTesting direct API call...")
    current_app = get_current_app()
    
    # Test direct segments call
    endpoint = f"apps/{current_app.app_id}/segments"
    print(f"Endpoint: {endpoint}")
    print(f"App ID: {current_app.app_id}")
    print(f"API Key length: {len(current_app.api_key)}")
    
    result = await make_onesignal_request(endpoint, method="GET", use_org_key=False)
    print(f"Direct API result: {json.dumps(result, indent=2)}")

async def test_endpoints():
    """Test the fixed endpoints"""
    print("Testing OneSignal Authentication Fix")
    print("=" * 50)
    
    # Check current app configuration
    current_app = get_current_app()
    if not current_app:
        print("❌ No app configured. Please ensure your .env file has:")
        print("   ONESIGNAL_APP_ID=your_app_id_here")
        print("   ONESIGNAL_API_KEY=your_rest_api_key_here")
        return
    
    print(f"✅ Current app: {current_app.name} (ID: {current_app.app_id})")
    print(f"   API Key: {'*' * 20}{current_app.api_key[-10:]}")
    print()
    
    # Test segments endpoint
    print("Testing view_segments()...")
    try:
        segments_result = await view_segments()
        if "Error retrieving segments:" in segments_result:
            print(f"❌ Segments test failed: {segments_result}")
        else:
            print("✅ Segments endpoint is working!")
            print(f"   Result preview: {segments_result[:200]}...")
    except Exception as e:
        print(f"❌ Segments test error: {str(e)}")
    
    print()
    
    # Test templates endpoint
    print("Testing view_templates()...")
    try:
        templates_result = await view_templates()
        if "Error retrieving templates:" in templates_result:
            print(f"❌ Templates test failed: {templates_result}")
        else:
            print("✅ Templates endpoint is working!")
            print(f"   Result preview: {templates_result[:200]}...")
    except Exception as e:
        print(f"❌ Templates test error: {str(e)}")
    
    # Test direct API call for debugging
    await test_direct_api_call()
    
    print()
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_endpoints()) 