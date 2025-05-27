"""Message management tools for OneSignal MCP server."""
import json
from typing import List, Dict, Any, Optional
from ..api_client import api_client, OneSignalAPIError
from ..config import app_manager


async def send_push_notification(
    title: str,
    message: str,
    segments: Optional[List[str]] = None,
    include_player_ids: Optional[List[str]] = None,
    external_ids: Optional[List[str]] = None,
    data: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Send a push notification through OneSignal.
    
    Args:
        title: Notification title
        message: Notification message content
        segments: List of segments to include
        include_player_ids: List of specific player IDs to target
        external_ids: List of external user IDs to target
        data: Additional data to include with the notification
        **kwargs: Additional notification parameters
    """
    notification_data = {
        "contents": {"en": message},
        "headings": {"en": title},
        "target_channel": "push"
    }
    
    # Set targeting
    if not any([segments, include_player_ids, external_ids]):
        segments = ["Subscribed Users"]
    
    if segments:
        notification_data["included_segments"] = segments
    if include_player_ids:
        notification_data["include_player_ids"] = include_player_ids
    if external_ids:
        notification_data["include_external_user_ids"] = external_ids
    
    if data:
        notification_data["data"] = data
    
    # Add any additional parameters
    notification_data.update(kwargs)
    
    return await api_client.request("notifications", method="POST", data=notification_data)


async def send_email(
    subject: str,
    body: str,
    email_body: Optional[str] = None,
    segments: Optional[List[str]] = None,
    include_emails: Optional[List[str]] = None,
    external_ids: Optional[List[str]] = None,
    template_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Send an email through OneSignal.
    
    Args:
        subject: Email subject line
        body: Plain text email content
        email_body: HTML email content (optional)
        segments: List of segments to include
        include_emails: List of specific email addresses to target
        external_ids: List of external user IDs to target
        template_id: Email template ID to use
        **kwargs: Additional email parameters
    """
    email_data = {
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
    
    # Add any additional parameters
    email_data.update(kwargs)
    
    return await api_client.request("notifications", method="POST", data=email_data)


async def send_sms(
    message: str,
    phone_numbers: Optional[List[str]] = None,
    segments: Optional[List[str]] = None,
    external_ids: Optional[List[str]] = None,
    media_url: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Send an SMS through OneSignal.
    
    Args:
        message: SMS message content
        phone_numbers: List of phone numbers in E.164 format
        segments: List of segments to include
        external_ids: List of external user IDs to target
        media_url: URL for MMS media attachment
        **kwargs: Additional SMS parameters
    """
    sms_data = {
        "contents": {"en": message},
        "target_channel": "sms"
    }
    
    # Set targeting
    if phone_numbers:
        sms_data["include_phone_numbers"] = phone_numbers
    elif external_ids:
        sms_data["include_external_user_ids"] = external_ids
    elif segments:
        sms_data["included_segments"] = segments
    else:
        raise OneSignalAPIError(
            "SMS requires phone_numbers, external_ids, or segments to be specified"
        )
    
    if media_url:
        sms_data["mms_media_url"] = media_url
    
    # Add any additional parameters
    sms_data.update(kwargs)
    
    return await api_client.request("notifications", method="POST", data=sms_data)


async def send_transactional_message(
    channel: str,
    content: Dict[str, str],
    recipients: Dict[str, Any],
    template_id: Optional[str] = None,
    custom_data: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Send a transactional message (immediate delivery, no scheduling).
    
    Args:
        channel: Channel to send on ("push", "email", "sms")
        content: Message content (format depends on channel)
        recipients: Targeting information
        template_id: Template ID to use
        custom_data: Custom data to include
        **kwargs: Additional parameters
    """
    message_data = {
        "target_channel": channel,
        "is_transactional": True
    }
    
    # Set content based on channel
    if channel == "email":
        message_data["email_subject"] = content.get("subject", "")
        message_data["email_body"] = content.get("body", "")
    else:
        message_data["contents"] = content
    
    # Set recipients
    message_data.update(recipients)
    
    if template_id:
        message_data["template_id"] = template_id
    
    if custom_data:
        message_data["data"] = custom_data
    
    # Add any additional parameters
    message_data.update(kwargs)
    
    return await api_client.request("notifications", method="POST", data=message_data)


async def view_messages(
    limit: int = 20,
    offset: int = 0,
    kind: Optional[int] = None
) -> Dict[str, Any]:
    """
    View recent messages sent through OneSignal.
    
    Args:
        limit: Maximum number of messages to return (max: 50)
        offset: Result offset for pagination
        kind: Filter by message type (0=Dashboard, 1=API, 3=Automated)
    """
    params = {"limit": min(limit, 50), "offset": offset}
    if kind is not None:
        params["kind"] = kind
    
    return await api_client.request("notifications", method="GET", params=params)


async def view_message_details(message_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific message."""
    return await api_client.request(f"notifications/{message_id}", method="GET")


async def cancel_message(message_id: str) -> Dict[str, Any]:
    """Cancel a scheduled message that hasn't been delivered yet."""
    return await api_client.request(f"notifications/{message_id}", method="DELETE")


async def view_message_history(message_id: str, event: str) -> Dict[str, Any]:
    """
    View the history/recipients of a message based on events.
    
    Args:
        message_id: The ID of the message
        event: The event type to track (e.g., 'sent', 'clicked')
    """
    app_config = app_manager.get_current_app()
    if not app_config:
        raise OneSignalAPIError("No app currently selected")
    
    data = {
        "app_id": app_config.app_id,
        "events": event,
        "email": f"{app_config.name}-history@example.com"
    }
    
    return await api_client.request(
        f"notifications/{message_id}/history", 
        method="POST", 
        data=data
    )


async def export_messages_csv(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Export messages to CSV.
    
    Args:
        start_date: Start date for export (ISO 8601 format)
        end_date: End date for export (ISO 8601 format)
        **kwargs: Additional export parameters
    """
    data = {}
    if start_date:
        data["start_date"] = start_date
    if end_date:
        data["end_date"] = end_date
    
    data.update(kwargs)
    
    return await api_client.request(
        "notifications/csv_export",
        method="POST",
        data=data,
        use_org_key=True
    ) 