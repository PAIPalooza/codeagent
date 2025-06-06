"""Base class for AINative API tool wrappers.

This module provides a base class for all AINative API tool wrappers with common
functionality for making HTTP requests, handling errors, and processing responses.
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class AINativeBaseTool(ABC):
    """Base class for Cody AI Development Platform API tool wrappers.
    
    This abstract base class handles common functionality for all AI API
    tool wrappers including authentication, error handling, and HTTP requests.
    
    Attributes:
        base_url: The base URL for the Cody AI Development Platform API.
        api_key: The API key for authentication.
        endpoint: The specific API endpoint for this tool.
    """
    
    def __init__(self, endpoint: str) -> None:
        """Initialize the AI tool with API configuration.
        
        Args:
            endpoint: The specific API endpoint for this tool.
        
        Note:
            If API credentials are missing, the tool will operate in mock mode.
        """
        self.base_url = os.environ.get("AINATIVE_BASE_URL", "https://api.ainative.studio/api/v1")
        self.api_key = os.environ.get("AINATIVE_API_KEY")
        self.mock_mode = False
        
        # Check if we need to use mock mode
        if not self.api_key or self.api_key == "your_ainative_api_key_here":
            logger.warning(f"Missing or invalid API credentials. Using mock mode for {endpoint}")
            self.mock_mode = True
            self.api_key = "mock-api-key"
        
        self.endpoint = endpoint
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests.
        
        Returns:
            Dictionary containing required HTTP headers.
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def _make_request(
        self, 
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make an HTTP request to the Cody AI Development Platform API.
        
        Args:
            payload: The request payload to send.
            
        Returns:
            Dictionary containing the API response.
            
        Raises:
            httpx.HTTPStatusError: If the HTTP request fails.
            json.JSONDecodeError: If the response is not valid JSON.
        """
        if self.mock_mode:
            logger.info(f"MOCK MODE: Simulating API call to {self.endpoint}")
            # Return a mock response for testing
            return self._generate_mock_response(payload)
        
        url = f"{self.base_url}/{self.endpoint}"
        headers = self._get_headers()
        
        logger.debug(f"Making request to: {url}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, 
                    headers=headers, 
                    json=payload, 
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            error_response = {"error": True, "message": str(e)}
            
            # Try to parse error details from response if possible
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict):
                    error_response["details"] = error_data
            except (json.JSONDecodeError, AttributeError):
                pass
                
            return error_response
            
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return {"error": True, "message": f"Request failed: {str(e)}"}
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return {"error": True, "message": "Invalid JSON in response"}
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"error": True, "message": f"Unexpected error: {str(e)}"}
        
    def _generate_mock_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a mock response for testing purposes.
        
        Args:
            payload: The request payload that would have been sent to the API.
            
        Returns:
            Dictionary containing a mock response appropriate for the tool.
        """
        # Default mock response with a successful outcome
        # This method should be overridden by specific tool implementations
        # to provide more realistic mock responses
        return {
            "success": True,
            "mock": True,
            "endpoint": self.endpoint,
            "message": "This is a mock response for testing",
            "file_path": "example.txt",
            "code": "# This is mock generated code\nprint('Hello, world!')\n",
            "received_payload": payload
        }
    
    @abstractmethod
    async def _call(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute the tool with the given parameters.
        
        Args:
            **kwargs: Tool-specific parameters.
            
        Returns:
            Dictionary containing the tool response.
        """
        pass
