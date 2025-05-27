"""Analytics and outcomes tools for OneSignal MCP server."""
from typing import Dict, Any, Optional, List
from ..api_client import api_client
from ..config import app_manager


async def view_outcomes(
    outcome_names: List[str],
    outcome_time_range: Optional[str] = None,
    outcome_platforms: Optional[List[str]] = None,
    outcome_attribution: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    View outcomes data for your OneSignal app.
    
    Args:
        outcome_names: List of outcome names to fetch data for
        outcome_time_range: Time range for data (e.g., "1d", "1mo")
        outcome_platforms: Filter by platforms (e.g., ["ios", "android"])
        outcome_attribution: Attribution model ("direct" or "influenced")
        **kwargs: Additional parameters
    """
    app_config = app_manager.get_current_app()
    if not app_config:
        raise ValueError("No app currently selected")
    
    params = {
        "outcome_names": outcome_names
    }
    
    if outcome_time_range:
        params["outcome_time_range"] = outcome_time_range
    if outcome_platforms:
        params["outcome_platforms"] = outcome_platforms
    if outcome_attribution:
        params["outcome_attribution"] = outcome_attribution
    
    params.update(kwargs)
    
    return await api_client.request(
        f"apps/{app_config.app_id}/outcomes",
        method="GET",
        params=params
    )


async def export_players_csv(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    segment_names: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Export player/subscription data to CSV.
    
    Args:
        start_date: Start date for export (ISO 8601 format)
        end_date: End date for export (ISO 8601 format)
        segment_names: List of segment names to export
        **kwargs: Additional export parameters
    """
    data = {}
    
    if start_date:
        data["start_date"] = start_date
    if end_date:
        data["end_date"] = end_date
    if segment_names:
        data["segment_names"] = segment_names
    
    data.update(kwargs)
    
    return await api_client.request(
        "players/csv_export",
        method="POST",
        data=data,
        use_org_key=True
    )


async def export_audience_activity_csv(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    event_types: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Export audience activity events to CSV.
    
    Args:
        start_date: Start date for export (ISO 8601 format)
        end_date: End date for export (ISO 8601 format)
        event_types: List of event types to export
        **kwargs: Additional export parameters
    """
    data = {}
    
    if start_date:
        data["start_date"] = start_date
    if end_date:
        data["end_date"] = end_date
    if event_types:
        data["event_types"] = event_types
    
    data.update(kwargs)
    
    return await api_client.request(
        "notifications/csv_export",
        method="POST",
        data=data,
        use_org_key=True
    )


def format_outcomes_response(outcomes: Dict[str, Any]) -> str:
    """Format outcomes response for display."""
    if not outcomes or "outcomes" not in outcomes:
        return "No outcomes data available."
    
    output = "Outcomes Report:\n\n"
    
    for outcome in outcomes.get("outcomes", []):
        output += f"Outcome: {outcome.get('id')}\n"
        output += f"Total Count: {outcome.get('aggregation', {}).get('count', 0)}\n"
        output += f"Total Value: {outcome.get('aggregation', {}).get('sum', 0)}\n"
        
        # Platform breakdown
        platforms = outcome.get('platforms', {})
        if platforms:
            output += "Platform Breakdown:\n"
            for platform, data in platforms.items():
                output += f"  {platform}: Count={data.get('count', 0)}, Value={data.get('sum', 0)}\n"
        
        output += "\n"
    
    return output 