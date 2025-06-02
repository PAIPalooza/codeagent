"""Memory Search Tool for AINative API.

This module provides a wrapper for the AINative agent/memory/search endpoint
that searches for information in the agent memory system.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from .base import AINativeBaseTool

# Configure logging
logger = logging.getLogger(__name__)


class MemorySearchTool(AINativeBaseTool):
    """Wrapper for AINative agent/memory/search endpoint.
    
    This class provides methods to search for and retrieve information
    from the AINative agent memory system.
    """
    
    def __init__(self) -> None:
        """Initialize the MemorySearchTool with the appropriate endpoint."""
        super().__init__(endpoint="memory/search")
    
    async def _call(
        self,
        query: str,
        project_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = 10,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Search for information in the agent memory.
        
        Args:
            query: The search query string.
            project_id: Optional ID of the associated project to filter by.
            tags: Optional list of tags to filter the search results.
            limit: Optional maximum number of results to return.
            **kwargs: Additional parameters to pass to the API.
            
        Returns:
            Dictionary containing search results or error information.
        """
        payload = {
            "query": query,
            "limit": limit,
            **kwargs
        }
        
        # Add optional parameters only if they have values
        if project_id:
            payload["project_id"] = project_id
            
        if tags:
            payload["tags"] = tags
        
        logger.info(f"Searching memory with query: {query}")
        
        return await self._make_request(payload)
