"""Memory Store Tool for AINative API.

This module provides a wrapper for the AINative agent/memory endpoint
that stores information in the agent memory system.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from .base import AINativeBaseTool

# Configure logging
logger = logging.getLogger(__name__)


class MemoryStoreTool(AINativeBaseTool):
    """Wrapper for AINative agent/memory endpoint.
    
    This class provides methods to store and manage information
    in the AINative agent memory system.
    """
    
    def __init__(self) -> None:
        """Initialize the MemoryStoreTool with the appropriate endpoint."""
        super().__init__(endpoint="agent/memory")
    
    async def _call(
        self,
        content: str,
        title: str,
        tags: List[str],
        project_id: Optional[str] = None,
        memory_id: Optional[str] = None,
        action: str = "create",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Store or update information in the agent memory.
        
        Args:
            content: The content to store in memory.
            title: Title for the memory entry.
            tags: List of tags for categorizing the memory.
            project_id: Optional ID of the associated project.
            memory_id: Optional ID of existing memory to update.
            action: Memory action ('create', 'update', or 'delete').
            **kwargs: Additional parameters to pass to the API.
            
        Returns:
            Dictionary containing operation result or error information.
            
        Raises:
            ValueError: If invalid action type is provided.
        """
        if action not in ["create", "update", "delete"]:
            raise ValueError("Action must be one of: create, update, delete")
        
        payload = {
            "content": content,
            "title": title,
            "tags": tags,
            "action": action,
            **kwargs
        }
        
        # Add optional parameters only if they have values
        if project_id:
            payload["project_id"] = project_id
            
        if memory_id:
            payload["memory_id"] = memory_id
        
        logger.info(f"Performing memory {action} operation with title: {title}")
        
        return await self._make_request(payload)
