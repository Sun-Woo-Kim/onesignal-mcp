"""Configuration management for OneSignal MCP server."""
import os
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logger
logger = logging.getLogger("onesignal-mcp.config")

# API Configuration
ONESIGNAL_API_URL = "https://api.onesignal.com/api/v1"
ONESIGNAL_ORG_API_KEY = os.getenv("ONESIGNAL_ORG_API_KEY", "")


@dataclass
class AppConfig:
    """Configuration for a OneSignal application."""
    app_id: str
    api_key: str
    name: str
    
    def __str__(self):
        return f"{self.name} ({self.app_id})"


class AppManager:
    """Manages OneSignal app configurations."""
    
    def __init__(self):
        self.app_configs: Dict[str, AppConfig] = {}
        self.current_app_key: Optional[str] = None
        self._load_from_environment()
    
    def _load_from_environment(self):
        """
        Load legacy fallback app configuration from environment variables.
        Keep only generic defaults for backwards compatibility; prefer caller-injected credentials.
        """
        default_app_id = os.getenv("ONESIGNAL_APP_ID", "").strip()
        default_api_key = os.getenv("ONESIGNAL_API_KEY", "").strip()
        if default_app_id and default_api_key:
            self.add_app("default", default_app_id, default_api_key, "Default App")
            self.current_app_key = "default"
            logger.info("Legacy default app configured from ONESIGNAL_APP_ID/ONESIGNAL_API_KEY")
        else:
            logger.debug("No legacy app configuration found. App credentials should be injected per request.")
    
    def add_app(self, key: str, app_id: str, api_key: str, name: Optional[str] = None) -> None:
        """Add a new app configuration."""
        self.app_configs[key] = AppConfig(app_id, api_key, name or key)
        logger.info(f"Added app configuration '{key}' with ID: {app_id}")
    
    def update_app(self, key: str, app_id: Optional[str] = None, 
                   api_key: Optional[str] = None, name: Optional[str] = None) -> bool:
        """Update an existing app configuration."""
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
        """Remove an app configuration."""
        if key not in self.app_configs:
            return False
        
        if self.current_app_key == key:
            # Switch to another app if available
            other_keys = [k for k in self.app_configs.keys() if k != key]
            self.current_app_key = other_keys[0] if other_keys else None
        
        del self.app_configs[key]
        logger.info(f"Removed app configuration '{key}'")
        return True
    
    def set_current_app(self, key: str) -> bool:
        """Set the current app to use for API requests."""
        if key in self.app_configs:
            self.current_app_key = key
            logger.info(f"Switched to app '{key}'")
            return True
        return False
    
    def get_current_app(self) -> Optional[AppConfig]:
        """Get the current app configuration."""
        if self.current_app_key and self.current_app_key in self.app_configs:
            return self.app_configs[self.current_app_key]
        return None
    
    def get_app(self, key: str) -> Optional[AppConfig]:
        """Get a specific app configuration."""
        return self.app_configs.get(key)
    
    def list_apps(self) -> Dict[str, AppConfig]:
        """Get all app configurations."""
        return self.app_configs.copy()


# Global app manager instance
app_manager = AppManager()


def requires_org_api_key(endpoint: str) -> bool:
    """Determine if an endpoint requires the Organization API Key."""
    org_level_endpoints = [
        "apps",                    # Managing apps
        "players/csv_export",      # Export users
        "notifications/csv_export" # Export notifications
    ]
    
    return any(endpoint == ep or endpoint.startswith(f"{ep}/") for ep in org_level_endpoints) 
