"""Template management tools for OneSignal MCP server."""
from typing import Dict, Any, Optional
from ..api_client import api_client
from ..config import app_manager


async def create_template(
    name: str,
    title: str,
    message: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new template in your OneSignal app.
    
    Args:
        name: Name of the template
        title: Title/heading of the template
        message: Content/message of the template
        **kwargs: Additional template parameters
    """
    app_config = app_manager.get_current_app()
    if not app_config:
        raise ValueError("No app currently selected")
    
    data = {
        "app_id": app_config.app_id,
        "name": name,
        "headings": {"en": title},
        "contents": {"en": message}
    }
    
    data.update(kwargs)
    
    return await api_client.request("templates", method="POST", data=data)


async def update_template(
    template_id: str,
    name: Optional[str] = None,
    title: Optional[str] = None,
    message: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Update an existing template.
    
    Args:
        template_id: ID of the template to update
        name: New name for the template
        title: New title/heading for the template
        message: New content/message for the template
        **kwargs: Additional template parameters
    """
    data = {}
    
    if name:
        data["name"] = name
    if title:
        data["headings"] = {"en": title}
    if message:
        data["contents"] = {"en": message}
    
    data.update(kwargs)
    
    if not data:
        raise ValueError("No update parameters provided")
    
    return await api_client.request(
        f"templates/{template_id}",
        method="PATCH",
        data=data
    )


async def view_templates() -> Dict[str, Any]:
    """List all templates available in your OneSignal app."""
    return await api_client.request("templates", method="GET")


async def view_template_details(template_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific template.
    
    Args:
        template_id: The ID of the template to retrieve
    """
    app_config = app_manager.get_current_app()
    if not app_config:
        raise ValueError("No app currently selected")
    
    params = {"app_id": app_config.app_id}
    return await api_client.request(
        f"templates/{template_id}",
        method="GET",
        params=params
    )


async def delete_template(template_id: str) -> Dict[str, Any]:
    """
    Delete a template from your OneSignal app.
    
    Args:
        template_id: ID of the template to delete
    """
    return await api_client.request(
        f"templates/{template_id}",
        method="DELETE"
    )


async def copy_template_to_app(
    template_id: str,
    target_app_id: str,
    new_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Copy a template to another OneSignal app.
    
    Args:
        template_id: ID of the template to copy
        target_app_id: ID of the app to copy the template to
        new_name: Optional new name for the copied template
    """
    data = {"app_id": target_app_id}
    
    if new_name:
        data["name"] = new_name
    
    return await api_client.request(
        f"templates/{template_id}/copy",
        method="POST",
        data=data
    )


def format_template_list(templates_response: Dict[str, Any]) -> str:
    """Format template list response for display."""
    templates = templates_response.get("templates", [])
    
    if not templates:
        return "No templates found."
    
    output = "Templates:\n\n"
    
    for template in templates:
        output += f"ID: {template.get('id')}\n"
        output += f"Name: {template.get('name')}\n"
        output += f"Created: {template.get('created_at')}\n"
        output += f"Updated: {template.get('updated_at')}\n\n"
    
    return output


def format_template_details(template: Dict[str, Any]) -> str:
    """Format template details for display."""
    heading = template.get("headings", {}).get("en", "No heading")
    content = template.get("contents", {}).get("en", "No content")
    
    details = [
        f"ID: {template.get('id')}",
        f"Name: {template.get('name')}",
        f"Title: {heading}",
        f"Message: {content}",
        f"Platform: {template.get('platform')}",
        f"Created: {template.get('created_at')}"
    ]
    
    return "\n".join(details) 