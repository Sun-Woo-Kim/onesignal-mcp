# Implementation Examples for Missing OneSignal API Endpoints

This document provides concrete examples of how to add the missing API endpoints to the current `onesignal_server.py` file without requiring a full refactor.

## 1. Email Sending Endpoint

Add this function after the existing `send_push_notification` function:

```python
@mcp.tool()
async def send_email(subject: str, body: str, email_body: str = None, 
                     include_emails: List[str] = None, segments: List[str] = None,
                     external_ids: List[str] = None, template_id: str = None) -> Dict[str, Any]:
    """Send an email through OneSignal.
    
    Args:
        subject: Email subject line
        body: Plain text email content  
        email_body: HTML email content (optional)
        include_emails: List of specific email addresses to target
        segments: List of segments to include
        external_ids: List of external user IDs to target
        template_id: Email template ID to use
    """
    app_config = get_current_app()
    if not app_config:
        return {"error": "No app currently selected. Use switch_app to select an app."}
    
    email_data = {
        "app_id": app_config.app_id,
        "email_subject": subject,
        "email_body": email_body or body,
        "target_channel": "email"
    }
    
    # Set targeting
    if include_emails:
        email_data["include_emails"] = include_emails
    elif external_ids:
        email_data["include_external_user_ids"] = external_ids
    elif segments:
        email_data["included_segments"] = segments
    else:
        email_data["included_segments"] = ["Subscribed Users"]
    
    if template_id:
        email_data["template_id"] = template_id
    
    result = await make_onesignal_request("notifications", method="POST", data=email_data)
    return result
```

## 2. SMS Sending Endpoint

```python
@mcp.tool()
async def send_sms(message: str, phone_numbers: List[str] = None, 
                   segments: List[str] = None, external_ids: List[str] = None,
                   media_url: str = None) -> Dict[str, Any]:
    """Send an SMS/MMS through OneSignal.
    
    Args:
        message: SMS message content
        phone_numbers: List of phone numbers in E.164 format
        segments: List of segments to include
        external_ids: List of external user IDs to target
        media_url: URL for MMS media attachment
    """
    app_config = get_current_app()
    if not app_config:
        return {"error": "No app currently selected. Use switch_app to select an app."}
    
    sms_data = {
        "app_id": app_config.app_id,
        "contents": {"en": message},
        "target_channel": "sms"
    }
    
    if phone_numbers:
        sms_data["include_phone_numbers"] = phone_numbers
    elif external_ids:
        sms_data["include_external_user_ids"] = external_ids
    elif segments:
        sms_data["included_segments"] = segments
    else:
        return {"error": "SMS requires phone_numbers, external_ids, or segments"}
    
    if media_url:
        sms_data["mms_media_url"] = media_url
    
    result = await make_onesignal_request("notifications", method="POST", data=sms_data)
    return result
```

## 3. Template Management Completions

### Update Template
```python
@mcp.tool()
async def update_template(template_id: str, name: str = None, 
                         title: str = None, message: str = None) -> Dict[str, Any]:
    """Update an existing template.
    
    Args:
        template_id: ID of the template to update
        name: New name for the template
        title: New title/heading for the template
        message: New content/message for the template
    """
    data = {}
    
    if name:
        data["name"] = name
    if title:
        data["headings"] = {"en": title}
    if message:
        data["contents"] = {"en": message}
    
    if not data:
        return {"error": "No update parameters provided"}
    
    result = await make_onesignal_request(f"templates/{template_id}", 
                                        method="PATCH", data=data)
    return result
```

### Delete Template
```python
@mcp.tool()
async def delete_template(template_id: str) -> Dict[str, Any]:
    """Delete a template from your OneSignal app.
    
    Args:
        template_id: ID of the template to delete
    """
    result = await make_onesignal_request(f"templates/{template_id}", 
                                        method="DELETE")
    if "error" not in result:
        return {"success": f"Template '{template_id}' deleted successfully"}
    return result
```

## 4. Live Activities

### Start Live Activity
```python
@mcp.tool()
async def start_live_activity(activity_id: str, push_token: str, 
                             subscription_id: str, activity_attributes: Dict[str, Any],
                             content_state: Dict[str, Any]) -> Dict[str, Any]:
    """Start a new iOS Live Activity.
    
    Args:
        activity_id: Unique identifier for the activity
        push_token: Push token for the Live Activity
        subscription_id: Subscription ID for the user
        activity_attributes: Static attributes for the activity
        content_state: Initial dynamic content state
    """
    data = {
        "activity_id": activity_id,
        "push_token": push_token,
        "subscription_id": subscription_id,
        "activity_attributes": activity_attributes,
        "content_state": content_state
    }
    
    result = await make_onesignal_request(f"live_activities/{activity_id}/start",
                                        method="POST", data=data)
    return result
```

### Update Live Activity
```python
@mcp.tool()
async def update_live_activity(activity_id: str, name: str, event: str,
                              content_state: Dict[str, Any], 
                              dismissal_date: int = None) -> Dict[str, Any]:
    """Update an existing iOS Live Activity.
    
    Args:
        activity_id: ID of the activity to update
        name: Name identifier for the update
        event: Event type ("update" or "end")
        content_state: Updated dynamic content state
        dismissal_date: Unix timestamp for automatic dismissal
    """
    data = {
        "name": name,
        "event": event,
        "content_state": content_state
    }
    
    if dismissal_date:
        data["dismissal_date"] = dismissal_date
    
    result = await make_onesignal_request(f"live_activities/{activity_id}/update",
                                        method="POST", data=data)
    return result
```

## 5. Analytics & Outcomes

### View Outcomes
```python
@mcp.tool()
async def view_outcomes(outcome_names: List[str], 
                       outcome_time_range: str = None,
                       outcome_platforms: List[str] = None) -> Dict[str, Any]:
    """View outcomes data for your OneSignal app.
    
    Args:
        outcome_names: List of outcome names to fetch data for
        outcome_time_range: Time range for data (e.g., "1d", "1mo")
        outcome_platforms: Filter by platforms (e.g., ["ios", "android"])
    """
    app_config = get_current_app()
    if not app_config:
        return {"error": "No app currently selected. Use switch_app to select an app."}
    
    params = {"outcome_names": outcome_names}
    
    if outcome_time_range:
        params["outcome_time_range"] = outcome_time_range
    if outcome_platforms:
        params["outcome_platforms"] = outcome_platforms
    
    result = await make_onesignal_request(f"apps/{app_config.app_id}/outcomes",
                                        method="GET", params=params)
    return result
```

## 6. Export Functions

### Export Players CSV
```python
@mcp.tool()
async def export_players_csv(start_date: str = None, end_date: str = None,
                            segment_names: List[str] = None) -> Dict[str, Any]:
    """Export player/subscription data to CSV.
    
    Args:
        start_date: Start date for export (ISO 8601 format)
        end_date: End date for export (ISO 8601 format)
        segment_names: List of segment names to export
    """
    data = {}
    
    if start_date:
        data["start_date"] = start_date
    if end_date:
        data["end_date"] = end_date
    if segment_names:
        data["segment_names"] = segment_names
    
    result = await make_onesignal_request("players/csv_export", 
                                        method="POST", data=data, use_org_key=True)
    return result
```

## 7. API Key Management

### Delete API Key
```python
@mcp.tool()
async def delete_app_api_key(app_id: str, key_id: str) -> Dict[str, Any]:
    """Delete an API key from a specific OneSignal app.
    
    Args:
        app_id: The ID of the app
        key_id: The ID of the API key to delete
    """
    result = await make_onesignal_request(f"apps/{app_id}/auth/tokens/{key_id}",
                                        method="DELETE", use_org_key=True)
    if "error" not in result:
        return {"success": f"API key '{key_id}' deleted successfully"}
    return result
```

### Update API Key
```python
@mcp.tool()
async def update_app_api_key(app_id: str, key_id: str, name: str = None,
                            scopes: List[str] = None) -> Dict[str, Any]:
    """Update an API key for a specific OneSignal app.
    
    Args:
        app_id: The ID of the app
        key_id: The ID of the API key to update
        name: New name for the API key
        scopes: New list of permission scopes
    """
    data = {}
    
    if name:
        data["name"] = name
    if scopes:
        data["scopes"] = scopes
    
    if not data:
        return {"error": "No update parameters provided"}
    
    result = await make_onesignal_request(f"apps/{app_id}/auth/tokens/{key_id}",
                                        method="PATCH", data=data, use_org_key=True)
    return result
```

## 8. Player/Device Management

### Add a Player
```python
@mcp.tool()
async def add_player(device_type: int, identifier: str = None,
                    language: str = None, tags: Dict[str, str] = None) -> Dict[str, Any]:
    """Add a new player/device to OneSignal.
    
    Args:
        device_type: Device type (0=iOS, 1=Android, etc.)
        identifier: Push token or player ID
        language: Language code (e.g., "en")
        tags: Dictionary of tags to assign
    """
    app_config = get_current_app()
    if not app_config:
        return {"error": "No app currently selected. Use switch_app to select an app."}
    
    data = {
        "app_id": app_config.app_id,
        "device_type": device_type
    }
    
    if identifier:
        data["identifier"] = identifier
    if language:
        data["language"] = language
    if tags:
        data["tags"] = tags
    
    result = await make_onesignal_request("players", method="POST", data=data)
    return result
```

### Edit Player
```python
@mcp.tool()
async def edit_player(player_id: str, tags: Dict[str, str] = None,
                     external_user_id: str = None, language: str = None) -> Dict[str, Any]:
    """Edit an existing player/device.
    
    Args:
        player_id: The player ID to edit
        tags: Dictionary of tags to update
        external_user_id: External user ID to assign
        language: Language code to update
    """
    app_config = get_current_app()
    if not app_config:
        return {"error": "No app currently selected. Use switch_app to select an app."}
    
    data = {"app_id": app_config.app_id}
    
    if tags:
        data["tags"] = tags
    if external_user_id:
        data["external_user_id"] = external_user_id
    if language:
        data["language"] = language
    
    if len(data) == 1:  # Only app_id
        return {"error": "No update parameters provided"}
    
    result = await make_onesignal_request(f"players/{player_id}", 
                                        method="PUT", data=data)
    return result
```

## Implementation Notes

1. **Error Handling**: All functions should return consistent error formats
2. **Authentication**: Use `use_org_key=True` for organization-level endpoints
3. **Validation**: Add input validation where necessary
4. **Documentation**: Include clear docstrings with parameter descriptions
5. **Testing**: Test each endpoint with valid OneSignal credentials

These implementations can be added directly to the existing `onesignal_server.py` file to provide immediate support for the missing API endpoints. 