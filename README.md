# OneSignal MCP Server

A comprehensive Model Context Protocol (MCP) server for interacting with the OneSignal API. This server provides a complete interface for managing push notifications, emails, SMS, users, devices, segments, templates, analytics, and more through OneSignal's REST API.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/weirdbrains/onesignal-mcp)
[![Tools](https://img.shields.io/badge/tools-57-green.svg)](https://github.com/weirdbrains/onesignal-mcp)

## Overview

This MCP server provides comprehensive access to the [OneSignal REST API](https://documentation.onesignal.com/reference/rest-api-overview), offering **57 tools** that cover all major OneSignal operations:

### 🚀 Key Features

- **Multi-channel Messaging**: Send push notifications, emails, SMS, and transactional messages
- **User & Device Management**: Complete CRUD operations for users, devices, and subscriptions
- **Advanced Segmentation**: Create and manage user segments with complex filters
- **Template System**: Create, update, and manage message templates
- **iOS Live Activities**: Full support for iOS Live Activities
- **Analytics & Export**: View outcomes data and export to CSV
- **Multi-App Support**: Manage multiple OneSignal applications seamlessly
- **API Key Management**: Create, update, rotate, and delete API keys
- **Organization-level Operations**: Manage apps across your entire organization

## Requirements

- Python 3.10 or higher (3.11+ recommended)
- `requests` package
- `mcp` package (requires Python 3.10+ for `match` statements and `X | Y` union types)
- `uvicorn` package
- OneSignal account with API credentials

## Installation

### Option 1: Clone from GitHub

```bash
# Clone the repository
git clone https://github.com/weirdbrains/onesignal-mcp.git
cd onesignal-mcp

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Install as a Package (Coming Soon)

```bash
pip install onesignal-mcp
```

## Configuration

1. Create a `.env` file for server settings (credentials are injected per MCP tool call):
   ```
   MCP_HOST=0.0.0.0
   PORT=8000
   LOG_LEVEL=INFO
   ```

2. All OneSignal credentials (`app_id`, `app_api_key`, `org_api_key`) are passed per MCP tool call.
   - Use `discover_apps` with `org_api_key` to find your apps.
   - Use `add_app` to register an app locally, or pass `app_id` + `app_api_key` directly to each tool.

3. Find your OneSignal credentials:
   - **App ID**: Settings > Keys & IDs > OneSignal App ID
   - **REST API Key**: Settings > Keys & IDs > REST API Key
   - **Organization API Key**: Organization Settings > API Keys

## Usage

### Running the Server (refactored auth-injected mode)

```bash
python -m onesignal_refactored
```

The server will start and register itself with the MCP system without requiring app credentials at startup.
Use `discover_apps` and pass `app_id` + `app_api_key` into the tool that needs them.

### Deployment (스크립트 전용)

```bash
# 1) 첫 배포 (처음 설치)
git clone -b master https://github.com/Sun-Woo-Kim/onesignal-mcp.git /opt/onesignal-mcp
cd /opt/onesignal-mcp
PUBLIC_HOST=3.34.235.194 bash scripts/deploy.sh

# 2) 코드 변경 후 업데이트/재배포 (원격 master 기준, 내부 pull + install + test 자동)
cd /opt/onesignal-mcp
PUBLIC_HOST=3.34.235.194 bash scripts/deploy.sh

# 3) 외부 체크만 분리해서 다시 보고 싶을 때
PUBLIC_HOST=3.34.235.194 bash scripts/test.sh

# 4) 포트만 바꾸고 배포할 때
PORT=9000 PUBLIC_HOST=3.34.235.194 bash scripts/deploy.sh

# 5) 단순 의존성 반영(설치만)
bash scripts/install.sh

# 6) 헬스체크만
bash scripts/test.sh
```

`deploy.sh`는 업데이트/재배포 기준 동작입니다.  
초기 설치는 클론 후 `deploy.sh`를 한 번 실행하면 됩니다.

## MCP usage flow (new)

1. `discover_apps(org_api_key="...")` → get all app IDs for the org.
2. `send_push_notification(..., app_id="ONE_SIGNAL_APP_ID", app_api_key="APP_REST_KEY")`
3. For org-level operations, pass only `org_api_key="..."` to that tool (when supported).

## Complete Tools Reference (57 Tools)

### 📱 App Management (5 tools)
- `list_apps` - List all configured OneSignal apps
- `add_app` - Add a new OneSignal app configuration locally
- `update_local_app_config` - Update an existing local app configuration
- `remove_app` - Remove a local OneSignal app configuration
- `switch_app` - Switch the current app to use for API requests

### 📨 Messaging (8 tools)
- `send_push_notification` - Send a push notification
- `send_email` - Send an email through OneSignal
- `send_sms` - Send an SMS/MMS through OneSignal
- `send_transactional_message` - Send immediate delivery messages
- `view_messages` - View recent messages sent
- `view_message_details` - Get detailed information about a message
- `view_message_history` - View message history/recipients
- `cancel_message` - Cancel a scheduled message

### 📱 Devices/Players (6 tools)
- `view_devices` - View devices subscribed to your app
- `view_device_details` - Get detailed information about a device
- `add_player` - Add a new player/device
- `edit_player` - Edit an existing player/device
- `delete_player` - Delete a player/device record
- `edit_tags_with_external_user_id` - Bulk edit tags by external ID

### 🎯 Segments (3 tools)
- `view_segments` - List all segments
- `create_segment` - Create a new segment
- `delete_segment` - Delete a segment

### 📄 Templates (6 tools)
- `view_templates` - List all templates
- `view_template_details` - Get template details
- `create_template` - Create a new template
- `update_template` - Update an existing template
- `delete_template` - Delete a template
- `copy_template_to_app` - Copy template to another app

### 🏢 Apps (6 tools)
- `view_app_details` - Get details about configured app
- `view_apps` - List all organization apps
- `create_app` - Create a new OneSignal application
- `update_app` - Update an existing application
- `view_app_api_keys` - View API keys for an app
- `create_app_api_key` - Create a new API key

### 🔑 API Key Management (3 tools)
- `delete_app_api_key` - Delete an API key
- `update_app_api_key` - Update an API key
- `rotate_app_api_key` - Rotate an API key

### 👤 Users (6 tools)
- `create_user` - Create a new user
- `view_user` - View user details
- `update_user` - Update user information
- `delete_user` - Delete a user
- `view_user_identity` - Get user identity information
- `view_user_identity_by_subscription` - Get identity by subscription

### 🏷️ Aliases (3 tools)
- `create_or_update_alias` - Create or update user alias
- `delete_alias` - Delete a user alias
- `create_alias_by_subscription` - Create alias by subscription ID

### 📬 Subscriptions (5 tools)
- `create_subscription` - Create a new subscription
- `update_subscription` - Update a subscription
- `delete_subscription` - Delete a subscription
- `transfer_subscription` - Transfer subscription between users
- `unsubscribe_email` - Unsubscribe using email token

### 🎯 Live Activities (3 tools)
- `start_live_activity` - Start iOS Live Activity
- `update_live_activity` - Update iOS Live Activity
- `end_live_activity` - End iOS Live Activity

### 📊 Analytics & Export (3 tools)
- `view_outcomes` - View outcomes/conversion data
- `export_players_csv` - Export player data to CSV
- `export_messages_csv` - Export messages to CSV

## Usage Examples

### Multi-Channel Messaging

```python
# Send a push notification
await send_push_notification(
    title="Hello World",
    message="This is a test notification",
    segments=["Subscribed Users"]
)

# Send an email
await send_email(
    subject="Welcome!",
    body="Thank you for joining us",
    email_body="<html><body><h1>Welcome!</h1></body></html>",
    include_emails=["user@example.com"]
)

# Send an SMS
await send_sms(
    message="Your verification code is 12345",
    phone_numbers=["+15551234567"]
)

# Send a transactional message
await send_transactional_message(
    channel="email",
    content={"subject": "Order Confirmation", "body": "Your order has been confirmed"},
    recipients={"include_external_user_ids": ["user123"]}
)
```

### User and Device Management

```python
# Create a user
user = await create_user(
    name="John Doe",
    email="john@example.com",
    external_id="user123",
    tags={"plan": "premium", "joined": "2024-01-01"}
)

# Add a device
device = await add_player(
    device_type=1,  # Android
    identifier="device_token_here",
    language="en",
    tags={"app_version": "1.0.0"}
)

# Update user tags across all devices
await edit_tags_with_external_user_id(
    external_user_id="user123",
    tags={"last_active": "2024-01-15", "purchases": "5"}
)
```

### iOS Live Activities

```python
# Start a Live Activity
await start_live_activity(
    activity_id="delivery_123",
    push_token="live_activity_push_token",
    subscription_id="user_subscription_id",
    activity_attributes={"order_number": "12345"},
    content_state={"status": "preparing", "eta": "15 mins"}
)

# Update the Live Activity
await update_live_activity(
    activity_id="delivery_123",
    name="delivery_update",
    event="update",
    content_state={"status": "on_the_way", "eta": "5 mins"}
)
```

### Analytics and Export

```python
# View conversion outcomes
outcomes = await view_outcomes(
    outcome_names=["purchase", "session_duration"],
    outcome_time_range="7d",
    outcome_platforms=["ios", "android"]
)

# Export player data
export = await export_players_csv(
    start_date="2024-01-01T00:00:00Z",
    end_date="2024-01-31T23:59:59Z",
    segment_names=["Active Users"]
)
```

## Testing

```bash
# Health check (local)
bash scripts/test.sh

# Health check (remote)
PUBLIC_HOST=3.34.235.194 bash scripts/test.sh
```

## Error Handling

The server provides consistent error handling:
- All errors are returned in a standardized format
- Detailed error messages help identify issues
- Automatic retry logic for transient failures
- Proper authentication error messages

## Rate Limiting

OneSignal enforces rate limits on API requests:
- Standard limit: 10 requests per second
- Bulk operations: May have lower limits
- The server includes guidance on handling rate limits

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [OneSignal](https://onesignal.com/) for their excellent notification service
- The MCP community for the Model Context Protocol
- All contributors to this project
