"""Configuration management for OneSignal MCP server."""
import logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger("onesignal-mcp.config")

ONESIGNAL_API_URL = "https://api.onesignal.com/api/v1"


@dataclass
class AppConfig:
    """Configuration for a OneSignal application."""
    app_id: str
    api_key: str
    name: str
    
    def __str__(self):
        return f"{self.name} ({self.app_id})"


class AppManager:
    """Manages OneSignal app configurations added at runtime via MCP tool calls."""
    
    def __init__(self):
        self.app_configs: Dict[str, AppConfig] = {}
        self.current_app_key: Optional[str] = None
    
    def add_app(self, key: str, app_id: str, api_key: str, name: Optional[str] = None) -> None:
        self.app_configs[key] = AppConfig(app_id, api_key, name or key)
        logger.info(f"Added app configuration '{key}' with ID: {app_id}")
    
    def update_app(self, key: str, app_id: Optional[str] = None, 
                   api_key: Optional[str] = None, name: Optional[str] = None) -> bool:
        if key not in self.app_configs:
            return False
        
        app = self.app_configs[key]
        if app_id:
            app.app_id = app_id
        if api_key:
            app.api_key = api_key
        if name:
            app.name = name
        
        logger.info(f"Updated app configuration '{key}'")
        return True
    
    def remove_app(self, key: str) -> bool:
        if key not in self.app_configs:
            return False
        
        if self.current_app_key == key:
            other_keys = [k for k in self.app_configs.keys() if k != key]
            self.current_app_key = other_keys[0] if other_keys else None
        
        del self.app_configs[key]
        logger.info(f"Removed app configuration '{key}'")
        return True
    
    def set_current_app(self, key: str) -> bool:
        if key in self.app_configs:
            self.current_app_key = key
            logger.info(f"Switched to app '{key}'")
            return True
        return False
    
    def get_current_app(self) -> Optional[AppConfig]:
        if self.current_app_key and self.current_app_key in self.app_configs:
            return self.app_configs[self.current_app_key]
        return None
    
    def get_app(self, key: str) -> Optional[AppConfig]:
        return self.app_configs.get(key)
    
    def list_apps(self) -> Dict[str, AppConfig]:
        return self.app_configs.copy()


app_manager = AppManager()


def requires_org_api_key(endpoint: str) -> bool:
    """Determine if an endpoint requires the Organization API Key."""
    org_level_endpoints = [
        "apps",
        "players/csv_export",
        "notifications/csv_export"
    ]
    
    return any(endpoint == ep or endpoint.startswith(f"{ep}/") for ep in org_level_endpoints)
