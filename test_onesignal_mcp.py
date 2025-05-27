#!/usr/bin/env python3
"""
Test script for OneSignal MCP Server
This script tests all the available functions in the OneSignal MCP server.

Usage:
1. Set up your environment variables in .env file:
   - ONESIGNAL_APP_ID
   - ONESIGNAL_API_KEY
   - ONESIGNAL_ORG_API_KEY

2. Run the OneSignal MCP server:
   python onesignal_server.py

3. In another terminal, run this test script:
   python test_onesignal_mcp.py
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Test configuration
TEST_CONFIG = {
    "test_email": "test@example.com",
    "test_phone": "+15551234567",  # E.164 format
    "test_external_id": "test_user_123",
    "test_player_id": None,  # Will be populated during tests
    "test_template_id": None,  # Will be populated during tests
    "test_user_id": None,  # Will be populated during tests
    "test_subscription_id": None,  # Will be populated during tests
}

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "errors": []
}

def print_test_header(test_name: str):
    """Print a formatted test header."""
    print(f"\n{'='*60}")
    print(f"Testing: {test_name}")
    print(f"{'='*60}")

def print_result(success: bool, message: str, result: Any = None):
    """Print test result with formatting."""
    if success:
        print(f"✅ {message}")
        test_results["passed"] += 1
    else:
        print(f"❌ {message}")
        test_results["failed"] += 1
        if result:
            test_results["errors"].append({
                "test": message,
                "error": result
            })
    
    if result and isinstance(result, dict):
        print(f"   Response: {json.dumps(result, indent=2)}")

async def test_app_management():
    """Test app management functions."""
    print_test_header("App Management")
    
    # Test listing apps
    print("\n1. Testing list_apps...")
    # Simulate function call - in real MCP, this would be via the MCP protocol
    # For testing, you'll need to call these through the MCP client
    print("   ⚠️  App management tests require MCP client implementation")
    test_results["skipped"] += 1

async def test_messaging():
    """Test messaging functions."""
    print_test_header("Messaging Functions")
    
    tests = [
        {
            "name": "Send Push Notification",
            "function": "send_push_notification",
            "params": {
                "title": "Test Push",
                "message": "This is a test push notification",
                "segments": ["Subscribed Users"]
            }
        },
        {
            "name": "Send Email",
            "function": "send_email",
            "params": {
                "subject": "Test Email",
                "body": "This is a test email",
                "include_emails": [TEST_CONFIG["test_email"]]
            }
        },
        {
            "name": "Send SMS",
            "function": "send_sms",
            "params": {
                "message": "Test SMS message",
                "phone_numbers": [TEST_CONFIG["test_phone"]]
            }
        },
        {
            "name": "Send Transactional Message",
            "function": "send_transactional_message",
            "params": {
                "channel": "push",
                "content": {"en": "Transactional test"},
                "recipients": {"include_external_user_ids": [TEST_CONFIG["test_external_id"]]}
            }
        }
    ]
    
    for test in tests:
        print(f"\n{test['name']}...")
        print(f"   Function: {test['function']}")
        print(f"   Params: {json.dumps(test['params'], indent=6)}")
        print("   ⚠️  Requires MCP client to execute")
        test_results["skipped"] += 1

async def test_templates():
    """Test template management functions."""
    print_test_header("Template Management")
    
    # Create template test
    print("\n1. Create Template")
    create_params = {
        "name": f"Test Template {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "title": "Test Template Title",
        "message": "Test template message content"
    }
    print(f"   Params: {json.dumps(create_params, indent=6)}")
    
    # Update template test
    print("\n2. Update Template")
    if TEST_CONFIG["test_template_id"]:
        update_params = {
            "template_id": TEST_CONFIG["test_template_id"],
            "name": "Updated Test Template",
            "title": "Updated Title"
        }
        print(f"   Params: {json.dumps(update_params, indent=6)}")
    else:
        print("   ⚠️  Skipped: No template ID available")
    
    # Delete template test
    print("\n3. Delete Template")
    print("   ⚠️  Skipped: Preserving test template")
    
    test_results["skipped"] += 3

async def test_live_activities():
    """Test iOS Live Activities functions."""
    print_test_header("iOS Live Activities")
    
    activity_tests = [
        {
            "name": "Start Live Activity",
            "params": {
                "activity_id": "test_activity_123",
                "push_token": "test_push_token",
                "subscription_id": "test_subscription",
                "activity_attributes": {"event": "Test Event"},
                "content_state": {"status": "active"}
            }
        },
        {
            "name": "Update Live Activity",
            "params": {
                "activity_id": "test_activity_123",
                "name": "test_update",
                "event": "update",
                "content_state": {"status": "updated"}
            }
        },
        {
            "name": "End Live Activity",
            "params": {
                "activity_id": "test_activity_123",
                "subscription_id": "test_subscription"
            }
        }
    ]
    
    for test in activity_tests:
        print(f"\n{test['name']}...")
        print(f"   Params: {json.dumps(test['params'], indent=6)}")
        print("   ⚠️  Requires iOS app with Live Activities support")
        test_results["skipped"] += 1

async def test_analytics():
    """Test analytics and export functions."""
    print_test_header("Analytics & Export")
    
    # View outcomes
    print("\n1. View Outcomes")
    outcomes_params = {
        "outcome_names": ["session_duration", "purchase"],
        "outcome_time_range": "1d",
        "outcome_platforms": ["ios", "android"]
    }
    print(f"   Params: {json.dumps(outcomes_params, indent=6)}")
    
    # Export functions
    export_tests = [
        {
            "name": "Export Players CSV",
            "params": {
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-12-31T23:59:59Z"
            }
        },
        {
            "name": "Export Messages CSV",
            "params": {
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-12-31T23:59:59Z"
            }
        }
    ]
    
    for test in export_tests:
        print(f"\n{test['name']}...")
        print(f"   Params: {json.dumps(test['params'], indent=6)}")
        print("   ⚠️  Requires Organization API Key")
        test_results["skipped"] += 1

async def test_user_management():
    """Test user management functions."""
    print_test_header("User Management")
    
    # Create user
    print("\n1. Create User")
    create_user_params = {
        "name": "Test User",
        "email": TEST_CONFIG["test_email"],
        "external_id": TEST_CONFIG["test_external_id"],
        "tags": {"test": "true", "created": datetime.now().isoformat()}
    }
    print(f"   Params: {json.dumps(create_user_params, indent=6)}")
    
    # Other user operations
    user_tests = [
        "View User",
        "Update User",
        "View User Identity",
        "Create/Update Alias",
        "Delete Alias"
    ]
    
    for test in user_tests:
        print(f"\n{test}")
        print(f"   ⚠️  Requires valid user_id from create_user")
        test_results["skipped"] += 1

async def test_player_management():
    """Test player/device management functions."""
    print_test_header("Player/Device Management")
    
    # Add player
    print("\n1. Add Player")
    add_player_params = {
        "device_type": 1,  # Android
        "identifier": "test_device_token",
        "language": "en",
        "tags": {"test_device": "true"}
    }
    print(f"   Params: {json.dumps(add_player_params, indent=6)}")
    
    # Other player operations
    player_tests = [
        "Edit Player",
        "Delete Player",
        "Edit Tags with External User ID"
    ]
    
    for test in player_tests:
        print(f"\n{test}")
        print(f"   ⚠️  Requires valid player_id")
        test_results["skipped"] += 1

async def test_subscription_management():
    """Test subscription management functions."""
    print_test_header("Subscription Management")
    
    subscription_tests = [
        {
            "name": "Create Subscription",
            "params": {
                "user_id": "test_user_id",
                "subscription_type": "email",
                "identifier": TEST_CONFIG["test_email"]
            }
        },
        {
            "name": "Update Subscription",
            "params": {
                "user_id": "test_user_id",
                "subscription_id": "test_subscription_id",
                "enabled": False
            }
        },
        {
            "name": "Transfer Subscription",
            "params": {
                "user_id": "test_user_id",
                "subscription_id": "test_subscription_id",
                "new_user_id": "new_test_user_id"
            }
        },
        {
            "name": "Delete Subscription",
            "params": {
                "user_id": "test_user_id",
                "subscription_id": "test_subscription_id"
            }
        }
    ]
    
    for test in subscription_tests:
        print(f"\n{test['name']}...")
        print(f"   Params: {json.dumps(test['params'], indent=6)}")
        print("   ⚠️  Requires valid user_id and subscription_id")
        test_results["skipped"] += 1

async def test_api_key_management():
    """Test API key management functions."""
    print_test_header("API Key Management")
    
    print("\n⚠️  API Key management requires Organization API Key")
    print("   and should be tested carefully to avoid breaking access")
    
    api_key_tests = [
        "View App API Keys",
        "Create App API Key",
        "Update App API Key",
        "Rotate App API Key",
        "Delete App API Key"
    ]
    
    for test in api_key_tests:
        print(f"\n{test}")
        print("   ⚠️  Skipped for safety")
        test_results["skipped"] += 1

def print_summary():
    """Print test summary."""
    print(f"\n\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Passed:  {test_results['passed']}")
    print(f"❌ Failed:  {test_results['failed']}")
    print(f"⚠️  Skipped: {test_results['skipped']}")
    
    if test_results["errors"]:
        print(f"\n\nERRORS:")
        for error in test_results["errors"]:
            print(f"\n- {error['test']}")
            print(f"  Error: {error['error']}")

async def main():
    """Run all tests."""
    print("OneSignal MCP Server Test Suite")
    print("================================")
    print("\nNOTE: This test script shows the structure of all available functions.")
    print("To actually execute these tests, you need to:")
    print("1. Run the OneSignal MCP server")
    print("2. Use an MCP client to connect and call the functions")
    print("3. Have valid OneSignal API credentials in your .env file")
    
    # Run test categories
    await test_app_management()
    await test_messaging()
    await test_templates()
    await test_live_activities()
    await test_analytics()
    await test_user_management()
    await test_player_management()
    await test_subscription_management()
    await test_api_key_management()
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    asyncio.run(main()) 