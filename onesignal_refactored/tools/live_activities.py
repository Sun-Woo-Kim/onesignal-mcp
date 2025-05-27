"""Live Activities management tools for OneSignal MCP server."""
from typing import Dict, Any, Optional
from ..api_client import api_client


async def start_live_activity(
    activity_id: str,
    push_token: str,
    subscription_id: str,
    activity_attributes: Dict[str, Any],
    content_state: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Start a new Live Activity for iOS.
    
    Args:
        activity_id: Unique identifier for the activity
        push_token: Push token for the Live Activity
        subscription_id: Subscription ID for the user
        activity_attributes: Static attributes for the activity
        content_state: Initial dynamic content state
        **kwargs: Additional parameters
    """
    data = {
        "activity_id": activity_id,
        "push_token": push_token,
        "subscription_id": subscription_id,
        "activity_attributes": activity_attributes,
        "content_state": content_state
    }
    
    data.update(kwargs)
    
    return await api_client.request(
        f"live_activities/{activity_id}/start",
        method="POST",
        data=data
    )


async def update_live_activity(
    activity_id: str,
    name: str,
    event: str,
    content_state: Dict[str, Any],
    dismissal_date: Optional[int] = None,
    priority: Optional[int] = None,
    sound: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Update an existing Live Activity.
    
    Args:
        activity_id: ID of the activity to update
        name: Name identifier for the update
        event: Event type ("update" or "end")
        content_state: Updated dynamic content state
        dismissal_date: Unix timestamp for automatic dismissal
        priority: Notification priority (5-10)
        sound: Sound file name for the update
        **kwargs: Additional parameters
    """
    data = {
        "name": name,
        "event": event,
        "content_state": content_state
    }
    
    if dismissal_date:
        data["dismissal_date"] = dismissal_date
    if priority:
        data["priority"] = priority
    if sound:
        data["sound"] = sound
    
    data.update(kwargs)
    
    return await api_client.request(
        f"live_activities/{activity_id}/update",
        method="POST",
        data=data
    )


async def end_live_activity(
    activity_id: str,
    subscription_id: str,
    dismissal_date: Optional[int] = None,
    priority: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    End a Live Activity.
    
    Args:
        activity_id: ID of the activity to end
        subscription_id: Subscription ID associated with the activity
        dismissal_date: Unix timestamp for dismissal
        priority: Notification priority (5-10)
        **kwargs: Additional parameters
    """
    data = {
        "subscription_id": subscription_id,
        "event": "end"
    }
    
    if dismissal_date:
        data["dismissal_date"] = dismissal_date
    if priority:
        data["priority"] = priority
    
    data.update(kwargs)
    
    return await api_client.request(
        f"live_activities/{activity_id}/end",
        method="POST",
        data=data
    )


async def get_live_activity_status(
    activity_id: str,
    subscription_id: str
) -> Dict[str, Any]:
    """
    Get the status of a Live Activity.
    
    Args:
        activity_id: ID of the activity
        subscription_id: Subscription ID associated with the activity
    """
    params = {"subscription_id": subscription_id}
    
    return await api_client.request(
        f"live_activities/{activity_id}/status",
        method="GET",
        params=params
    ) 