"""API client for OneSignal REST API requests."""
import logging
import requests
from typing import Dict, Any, Optional
from .config import (
    ONESIGNAL_API_URL, 
    ONESIGNAL_ORG_API_KEY,
    app_manager,
    requires_org_api_key
)

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
        app_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the OneSignal API with proper authentication.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            data: Request body for POST/PUT/PATCH requests
            params: Query parameters for GET requests
            use_org_key: Whether to use the organization API key
            app_key: The key of the app configuration to use
            
        Returns:
            API response as dictionary
            
        Raises:
            OneSignalAPIError: If the API request fails
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # Determine authentication method
        if use_org_key is None:
            use_org_key = requires_org_api_key(endpoint)
        
        # Set authentication header
        if use_org_key:
            if not ONESIGNAL_ORG_API_KEY:
                raise OneSignalAPIError(
                    "Organization API Key not configured. "
                    "Set the ONESIGNAL_ORG_API_KEY environment variable."
                )
            headers["Authorization"] = f"Basic {ONESIGNAL_ORG_API_KEY}"
        else:
            # Get app configuration
            app_config = None
            if app_key:
                app_config = app_manager.get_app(app_key)
            else:
                app_config = app_manager.get_current_app()
            
            if not app_config:
                raise OneSignalAPIError(
                    "No app configuration available. "
                    "Use set_current_app or specify app_key."
                )
            
            headers["Authorization"] = f"Basic {app_config.api_key}"
            
            # Add app_id to params/data if needed
            if params is None:
                params = {}
            if "app_id" not in params and not endpoint.startswith("apps/"):
                params["app_id"] = app_config.app_id
            
            if data is not None and method in ["POST", "PUT", "PATCH"]:
                if "app_id" not in data and not endpoint.startswith("apps/"):
                    data["app_id"] = app_config.app_id
        
        url = f"{self.api_url}/{endpoint}"
        
        try:
            logger.debug(f"Making {method} request to {url}")
            logger.debug(f"Using {'Organization API Key' if use_org_key else 'App REST API Key'}")
            
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
        """Make the actual HTTP request."""
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
        """Extract a meaningful error message from the HTTP error."""
        try:
            if hasattr(error, 'response') and error.response is not None:
                error_data = error.response.json()
                if isinstance(error_data, dict):
                    # Try different error message formats
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


# Global API client instance
api_client = OneSignalAPIClient() 