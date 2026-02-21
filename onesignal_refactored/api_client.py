"""API client for OneSignal REST API requests."""
import logging
import requests
from typing import Dict, Any, Optional
from .config import (
    ONESIGNAL_API_URL,
    app_manager,
    requires_org_api_key
)
from dataclasses import dataclass


@dataclass
class _AppConfigSnapshot:
    app_id: str
    api_key: str
    name: str = "injected-app"

logger = logging.getLogger("onesignal-mcp.api_client")


class OneSignalAPIError(Exception):
    """Custom exception for OneSignal API errors."""
    pass


class OneSignalAPIClient:
    """Client for making requests to the OneSignal API."""
    
    def __init__(self):
        self.api_url = ONESIGNAL_API_URL
        self.timeout = 30
    
    async def request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        use_org_key: Optional[bool] = None,
        app_key: Optional[str] = None,
        app_id: Optional[str] = None,
        app_api_key: Optional[str] = None,
        org_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the OneSignal API.
        
        All credentials must be injected per call:
        - app_id + app_api_key for app-level endpoints
        - org_api_key for org-level endpoints
        - app_key to reference a locally stored app config
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if use_org_key is None:
            use_org_key = requires_org_api_key(endpoint)
        
        if use_org_key:
            if not org_api_key:
                raise OneSignalAPIError(
                    "Organization API Key required. Pass org_api_key to this tool call."
                )
            headers["Authorization"] = f"Basic {org_api_key}"
        else:
            app_config = None
            if app_id and app_api_key:
                app_config = _AppConfigSnapshot(app_id, app_api_key, "Injected App")
            elif app_key:
                app_config = app_manager.get_app(app_key)
            else:
                app_config = app_manager.get_current_app()
            
            if not app_config:
                raise OneSignalAPIError(
                    "No app configuration available. "
                    "Pass app_id + app_api_key, or use add_app/switch_app first."
                )
            if not app_id:
                app_id = app_config.app_id
            
            app_api_key = app_api_key or app_config.api_key
            
            headers["Authorization"] = f"Basic {app_api_key}"
            
            if params is None:
                params = {}
            if "app_id" not in params and not endpoint.startswith("apps/"):
                params["app_id"] = app_id
            
            if data is not None and method in ["POST", "PUT", "PATCH"]:
                if "app_id" not in data and not endpoint.startswith("apps/"):
                    data["app_id"] = app_id
        
        url = f"{self.api_url}/{endpoint}"
        
        try:
            logger.debug(f"Making {method} request to {url}")
            
            response = self._make_request(method, url, headers, params, data)
            response.raise_for_status()
            
            return response.json() if response.text else {}
            
        except requests.exceptions.HTTPError as e:
            error_message = self._extract_error_message(e)
            logger.error(f"API request failed: {error_message}")
            raise OneSignalAPIError(error_message) from e
        except requests.exceptions.RequestException as e:
            error_message = f"Request failed: {str(e)}"
            logger.error(error_message)
            raise OneSignalAPIError(error_message) from e
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            logger.exception(error_message)
            raise OneSignalAPIError(error_message) from e
    
    def _make_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        params: Optional[Dict[str, Any]],
        data: Optional[Dict[str, Any]]
    ) -> requests.Response:
        method = method.upper()
        
        if method == "GET":
            return requests.get(url, headers=headers, params=params, timeout=self.timeout)
        elif method == "POST":
            return requests.post(url, headers=headers, json=data, timeout=self.timeout)
        elif method == "PUT":
            return requests.put(url, headers=headers, json=data, timeout=self.timeout)
        elif method == "DELETE":
            return requests.delete(url, headers=headers, timeout=self.timeout)
        elif method == "PATCH":
            return requests.patch(url, headers=headers, json=data, timeout=self.timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    
    def _extract_error_message(self, error: requests.exceptions.HTTPError) -> str:
        try:
            if hasattr(error, 'response') and error.response is not None:
                error_data = error.response.json()
                if isinstance(error_data, dict):
                    if 'errors' in error_data:
                        errors = error_data['errors']
                        if isinstance(errors, list) and errors:
                            return f"Error: {errors[0]}"
                        elif isinstance(errors, str):
                            return f"Error: {errors}"
                    elif 'error' in error_data:
                        return f"Error: {error_data['error']}"
                    elif 'message' in error_data:
                        return f"Error: {error_data['message']}"
                return f"Error: {error.response.reason} (Status: {error.response.status_code})"
        except Exception:
            pass
        return f"Error: {str(error)}"


api_client = OneSignalAPIClient()
