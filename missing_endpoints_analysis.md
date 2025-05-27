# OneSignal MCP Server - Missing Endpoints Analysis

## High Priority Missing Endpoints

### 1. Messaging Endpoints
- **Email-specific endpoint** (`/notifications` with email channel)
  - Currently only generic push notifications are supported
- **SMS-specific endpoint** (`/notifications` with SMS channel)
  - No dedicated SMS sending functionality
- **Transactional Messages** (`/notifications` with specific flags)
  - Critical for automated/triggered messages

### 2. Live Activities (iOS)
- **Start Live Activity** (`/live_activities/{activity_id}/start`)
- **Update Live Activity** (`/live_activities/{activity_id}/update`)
- **End Live Activity** (`/live_activities/{activity_id}/end`)

### 3. Template Management
- **Update Template** (`PATCH /templates/{template_id}`)
- **Delete Template** (`DELETE /templates/{template_id}`)
- **Copy Template to Another App** (`POST /templates/{template_id}/copy`)

### 4. API Key Management
- **Delete API Key** (`DELETE /apps/{app_id}/auth/tokens/{token_id}`)
- **Update API Key** (`PATCH /apps/{app_id}/auth/tokens/{token_id}`)
- **Rotate API Key** (`POST /apps/{app_id}/auth/tokens/{token_id}/rotate`)

### 5. Analytics/Outcomes
- **View Outcomes** (`GET /apps/{app_id}/outcomes`)
  - Essential for tracking conversion metrics

### 6. Export Functionality
- **Export Subscriptions CSV** (`POST /players/csv_export`)
- **Export Audience Activity CSV** (`POST /notifications/csv_export`)

### 7. Player/Device Management (Legacy but still used)
- **Add a Player** (`POST /players`)
- **Edit Player** (`PUT /players/{player_id}`)
- **Edit Tags with External User ID** (`PUT /users/{external_user_id}`)
- **Delete Player Record** (`DELETE /players/{player_id}`)

### 8. Additional User/Subscription Endpoints
- **View User Identity by Subscription** (`GET /apps/{app_id}/subscriptions/{subscription_id}/identity`)
- **Create Alias by Subscription** (`PATCH /apps/{app_id}/subscriptions/{subscription_id}/identity`)

## Medium Priority Missing Features

### 1. In-App Messages
- No endpoints for managing in-app messages

### 2. Webhooks Management
- No endpoints for configuring webhooks

### 3. Journey/Automation APIs
- No support for automated messaging journeys

## Implementation Priority

1. **Email and SMS endpoints** - Critical for multi-channel messaging
2. **Transactional Messages** - Essential for automated notifications
3. **Template management completeness** - Update and delete operations
4. **Export functionality** - Important for data management
5. **Analytics/Outcomes** - Necessary for measuring effectiveness 