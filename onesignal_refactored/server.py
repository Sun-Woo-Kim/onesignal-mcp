"""OneSignal MCP Server - Refactored implementation."""
import os
import logging
from mcp.server.fastmcp import FastMCP
from .config import app_manager
from .api_client import api_client, OneSignalAPIError
from .tools import (
    messages,
    templates,
    live_activities,
    analytics,
)

# Version information
__version__ = "2.0.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("onesignal-mcp")

# Get log level from environment
log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
if log_level_str not in valid_log_levels:
    logger.warning(f"Invalid LOG_LEVEL '{log_level_str}'. Using INFO instead.")
    log_level_str = "INFO"

logger.setLevel(log_level_str)

# Initialize MCP server (compatible with both old and new FastMCP signatures)
host = os.getenv("MCP_HOST", "0.0.0.0")
port = int(os.getenv("PORT", "8000"))

try:
    mcp = FastMCP(
        "onesignal-server",
        log_level=log_level_str,
        host=host,
        port=port,
    )
except TypeError:
    try:
        mcp = FastMCP("onesignal-server", host=host, port=port)
    except TypeError:
        logger.debug("FastMCP does not accept host/port/log_level args; using legacy signature.")
        try:
            mcp = FastMCP("onesignal-server", log_level=log_level_str)
        except TypeError:
            logger.debug("FastMCP does not accept log_level; using default signature.")
            mcp = FastMCP("onesignal-server")
logger.info(f"OneSignal MCP server v{__version__} initialized")


def _auth_kwargs(
    app_id: str = None,
    app_api_key: str = None,
    app_key: str = None,
    org_api_key: str = None
) -> dict:
    return {
        "app_id": app_id,
        "app_api_key": app_api_key,
        "app_key": app_key,
        "org_api_key": org_api_key,
    }


# === Configuration Resource ===


@mcp.resource("onesignal://config")
def get_onesignal_config() -> str:
    """Get information about the OneSignal configuration."""
    current_app = app_manager.get_current_app()
    app_list = "\n".join([
        f"- {key}: {app}" for key, app in app_manager.list_apps().items()
    ])
    
    return f"""
OneSignal Server Configuration:
Version: {__version__}
Current App: {current_app.name if current_app else 'None'}

Configured Local Apps:
{app_list or "No local apps configured"}

This refactored MCP server is ready for injected credentials:
- app_id + app_api_key can be passed per tool call
- or org_api_key can be passed for org-level endpoints
- list_apps/discover_apps help you find and choose the target app
"""


# === App Management Tools ===


@mcp.tool()
async def list_apps() -> str:
    """List locally configured OneSignal apps."""
    apps = app_manager.list_apps()
    if not apps:
        return "No local apps configured."
    
    current_app = app_manager.get_current_app()
    result = ["Configured OneSignal Apps:"]
    
    for key, app in apps.items():
        current_marker = " (current)" if current_app and key == app_manager.current_app_key else ""
        result.append(f"- {key}: {app.name} (App ID: {app.app_id}){current_marker}")
    
    return "\n".join(result)


@mcp.tool()
async def discover_apps(
    org_api_key: str = None,
    limit: int = 100,
    offset: int = 0
) -> str:
    """
    Discover apps from OneSignal org-level endpoint using injected org_api_key.
    """
    try:
        response = await api_client.request(
            "apps",
            method="GET",
            params={"limit": limit, "offset": offset},
            use_org_key=True,
            org_api_key=org_api_key
        )
        apps = response.get("apps") or response.get("rows") or []
        if not apps:
            return "No apps found for this organization credential."
        lines = ["Discovered Apps:"]
        for app in apps:
            app_id = app.get("id", "N/A")
            name = app.get("name", "Unnamed")
            lines.append(f"- {name} ({app_id})")
        return "\n".join(lines)
    except OneSignalAPIError as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def add_app(key: str, app_id: str, app_api_key: str, name: str = None) -> str:
    """Add a new OneSignal app configuration locally."""
    if not all([key, app_id, app_api_key]):
        return "Error: All parameters (key, app_id, app_api_key) are required."
    
    if key in app_manager.list_apps():
        return f"Error: App key '{key}' already exists."
    
    app_manager.add_app(key, app_id, app_api_key, name)
    
    if len(app_manager.list_apps()) == 1:
        app_manager.set_current_app(key)
    
    return f"Successfully added app '{key}' with name '{name or key}'."


@mcp.tool()
async def switch_app(key: str) -> str:
    """Switch the current local app to use for API requests."""
    if app_manager.set_current_app(key):
        app = app_manager.get_app(key)
        return f"Switched to app '{key}' ({app.name})."
    else:
        available = ", ".join(app_manager.list_apps().keys()) or "None"
        return f"Error: App key '{key}' not found. Available apps: {available}"


# === Messaging Tools ===


@mcp.tool()
async def send_push_notification(
    title: str,
    message: str,
    segments: list = None,
    include_player_ids: list = None,
    external_ids: list = None,
    data: dict = None,
    app_id: str = None,
    app_api_key: str = None,
    app_key: str = None
) -> dict:
    """Send a push notification through OneSignal."""
    try:
        return await messages.send_push_notification(
            title=title,
            message=message,
            segments=segments,
            include_player_ids=include_player_ids,
            external_ids=external_ids,
            data=data,
            **_auth_kwargs(app_id, app_api_key, app_key)
        )
    except OneSignalAPIError as e:
        return {"error": str(e)}


@mcp.tool()
async def send_email(
    subject: str,
    body: str,
    include_emails: list = None,
    segments: list = None,
    external_ids: list = None,
    template_id: str = None,
    app_id: str = None,
    app_api_key: str = None,
    app_key: str = None
) -> dict:
    """Send an email through OneSignal."""
    try:
        return await messages.send_email(
            subject=subject,
            body=body,
            include_emails=include_emails,
            segments=segments,
            external_ids=external_ids,
            template_id=template_id,
            **_auth_kwargs(app_id, app_api_key, app_key)
        )
    except OneSignalAPIError as e:
        return {"error": str(e)}


@mcp.tool()
async def send_sms(
    message: str,
    phone_numbers: list = None,
    segments: list = None,
    external_ids: list = None,
    media_url: str = None,
    app_id: str = None,
    app_api_key: str = None,
    app_key: str = None
) -> dict:
    """Send an SMS/MMS through OneSignal."""
    try:
        return await messages.send_sms(
            message=message,
            phone_numbers=phone_numbers,
            segments=segments,
            external_ids=external_ids,
            media_url=media_url,
            **_auth_kwargs(app_id, app_api_key, app_key)
        )
    except OneSignalAPIError as e:
        return {"error": str(e)}


@mcp.tool()
async def send_transactional_message(
    channel: str,
    content: dict,
    recipients: dict,
    template_id: str = None,
    custom_data: dict = None,
    app_id: str = None,
    app_api_key: str = None,
    app_key: str = None
) -> dict:
    """Send a transactional message (immediate delivery)."""
    try:
        return await messages.send_transactional_message(
            channel=channel,
            content=content,
            recipients=recipients,
            template_id=template_id,
            custom_data=custom_data,
            **_auth_kwargs(app_id, app_api_key, app_key)
        )
    except OneSignalAPIError as e:
        return {"error": str(e)}


@mcp.tool()
async def view_messages(
    limit: int = 20,
    offset: int = 0,
    kind: int = None,
    app_id: str = None,
    app_api_key: str = None,
    app_key: str = None
) -> dict:
    """View recent messages sent through OneSignal."""
    try:
        return await messages.view_messages(
            limit=limit,
            offset=offset,
            kind=kind,
            **_auth_kwargs(app_id, app_api_key, app_key)
        )
    except OneSignalAPIError as e:
        return {"error": str(e)}


@mcp.tool()
async def view_message_details(message_id: str) -> dict:
    """Get detailed information about a specific message."""
    try:
        return await messages.view_message_details(message_id)
    except OneSignalAPIError as e:
        return {"error": str(e)}


@mcp.tool()
async def cancel_message(message_id: str) -> dict:
    """Cancel a scheduled message."""
    try:
        return await messages.cancel_message(message_id)
    except OneSignalAPIError as e:
        return {"error": str(e)}


@mcp.tool()
async def view_message_history(
    message_id: str,
    event: str,
    app_id: str = None,
    app_api_key: str = None,
    app_key: str = None,
    recipient_email: str = None
) -> dict:
    """View message history by event."""
    try:
        return await messages.view_message_history(
            message_id=message_id,
            event=event,
            recipient_email=recipient_email,
            **_auth_kwargs(app_id, app_api_key, app_key)
        )
    except OneSignalAPIError as e:
        return {"error": str(e)}


@mcp.tool()
async def export_messages_csv(
    start_date: str = None,
    end_date: str = None,
    org_api_key: str = None
) -> dict:
    """Export messages to CSV (requires Organization API Key)."""
    try:
        return await messages.export_messages_csv(
            start_date=start_date,
            end_date=end_date,
            org_api_key=org_api_key
        )
    except OneSignalAPIError as e:
        return {"error": str(e)}


# === Template Tools ===


@mcp.tool()
async def create_template(
    name: str,
    title: str,
    message: str,
    app_id: str = None,
    app_api_key: str = None,
    app_key: str = None
) -> dict:
    """Create a new template."""
    try:
        result = await templates.create_template(
            name=name,
            title=title,
            message=message,
            **_auth_kwargs(app_id, app_api_key, app_key)
        )
        return {"success": f"Template '{name}' created with ID: {result.get('id')}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def update_template(
    template_id: str,
    name: str = None,
    title: str = None,
    message: str = None,
    app_id: str = None,
    app_api_key: str = None,
    app_key: str = None
) -> dict:
    """Update an existing template."""
    try:
        await templates.update_template(
            template_id=template_id,
            name=name,
            title=title,
            message=message,
            **_auth_kwargs(app_id, app_api_key, app_key)
        )
        return {"success": f"Template '{template_id}' updated successfully"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def view_templates(
    app_id: str = None,
    app_api_key: str = None,
    app_key: str = None
) -> str:
    """List all templates."""
    try:
        result = await templates.view_templates(
            **_auth_kwargs(app_id, app_api_key, app_key)
        )
        return templates.format_template_list(result)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def view_template_details(
    template_id: str,
    app_id: str = None,
    app_api_key: str = None,
    app_key: str = None
) -> str:
    """Get template details."""
    try:
        result = await templates.view_template_details(
            template_id=template_id,
            **_auth_kwargs(app_id, app_api_key, app_key)
        )
        return templates.format_template_details(result)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def delete_template(
    template_id: str,
    app_id: str = None,
    app_api_key: str = None,
    app_key: str = None
) -> dict:
    """Delete a template."""
    try:
        await templates.delete_template(
            template_id=template_id,
            **_auth_kwargs(app_id, app_api_key, app_key)
        )
        return {"success": f"Template '{template_id}' deleted successfully"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def copy_template_to_app(
    template_id: str,
    target_app_id: str,
    new_name: str = None,
    app_id: str = None,
    app_api_key: str = None,
    app_key: str = None
) -> dict:
    """Copy a template to another app."""
    try:
        result = await templates.copy_template_to_app(
            template_id=template_id,
            target_app_id=target_app_id,
            new_name=new_name,
            **_auth_kwargs(app_id, app_api_key, app_key)
        )
        return {"success": f"Template copied successfully. New ID: {result.get('id')}"}
    except Exception as e:
        return {"error": str(e)}


# === Live Activities Tools ===


@mcp.tool()
async def start_live_activity(
    activity_id: str,
    push_token: str,
    subscription_id: str,
    activity_attributes: dict,
    content_state: dict,
    app_id: str = None,
    app_api_key: str = None,
    app_key: str = None
) -> dict:
    """Start a new iOS Live Activity."""
    try:
        return await live_activities.start_live_activity(
            activity_id=activity_id,
            push_token=push_token,
            subscription_id=subscription_id,
            activity_attributes=activity_attributes,
            content_state=content_state,
            **_auth_kwargs(app_id, app_api_key, app_key)
        )
    except OneSignalAPIError as e:
        return {"error": str(e)}


@mcp.tool()
async def update_live_activity(
    activity_id: str,
    name: str,
    event: str,
    content_state: dict,
    dismissal_date: int = None,
    priority: int = None,
    sound: str = None,
    app_id: str = None,
    app_api_key: str = None,
    app_key: str = None
) -> dict:
    """Update an iOS Live Activity."""
    try:
        return await live_activities.update_live_activity(
            activity_id=activity_id,
            name=name,
            event=event,
            content_state=content_state,
            dismissal_date=dismissal_date,
            priority=priority,
            sound=sound,
            **_auth_kwargs(app_id, app_api_key, app_key)
        )
    except OneSignalAPIError as e:
        return {"error": str(e)}


@mcp.tool()
async def end_live_activity(
    activity_id: str,
    subscription_id: str,
    dismissal_date: int = None,
    priority: int = None,
    app_id: str = None,
    app_api_key: str = None,
    app_key: str = None
) -> dict:
    """End an iOS Live Activity."""
    try:
        return await live_activities.end_live_activity(
            activity_id=activity_id,
            subscription_id=subscription_id,
            dismissal_date=dismissal_date,
            priority=priority,
            **_auth_kwargs(app_id, app_api_key, app_key)
        )
    except OneSignalAPIError as e:
        return {"error": str(e)}


# === Analytics Tools ===


@mcp.tool()
async def view_outcomes(
    outcome_names: list,
    outcome_time_range: str = None,
    outcome_platforms: list = None,
    outcome_attribution: str = None,
    app_id: str = None,
    app_api_key: str = None,
    app_key: str = None
) -> str:
    """View outcomes data for your app."""
    try:
        result = await analytics.view_outcomes(
            outcome_names=outcome_names,
            outcome_time_range=outcome_time_range,
            outcome_platforms=outcome_platforms,
            outcome_attribution=outcome_attribution,
            app_id=app_id,
            app_api_key=app_api_key,
            app_key=app_key
        )
        return analytics.format_outcomes_response(result)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def export_players_csv(
    start_date: str = None,
    end_date: str = None,
    segment_names: list = None,
    org_api_key: str = None
) -> dict:
    """Export player data to CSV (requires Organization API Key)."""
    try:
        return await analytics.export_players_csv(
            start_date=start_date,
            end_date=end_date,
            segment_names=segment_names,
            org_api_key=org_api_key
        )
    except OneSignalAPIError as e:
        return {"error": str(e)}


@mcp.tool()
async def export_audience_activity_csv(
    start_date: str = None,
    end_date: str = None,
    event_types: list = None,
    org_api_key: str = None
) -> dict:
    """Export audience activity to CSV (requires Organization API Key)."""
    try:
        return await analytics.export_audience_activity_csv(
            start_date=start_date,
            end_date=end_date,
            event_types=event_types,
            org_api_key=org_api_key
        )
    except OneSignalAPIError as e:
        return {"error": str(e)}


# Run the server
if __name__ == "__main__":
    mcp.run()
