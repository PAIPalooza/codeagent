"""Code Generation Create Tool for AINative API.

This module provides a wrapper for the AINative code-generation/create endpoint
that generates new code based on provided specifications.
"""

import logging
from typing import Any, Dict, List, Optional

from .base import AINativeBaseTool

# Configure logging
logger = logging.getLogger(__name__)


class CodeGenCreateTool(AINativeBaseTool):
    """Wrapper for AINative code-generation/create endpoint.
    
    This class provides methods to generate new code based on
    project specifications and requirements.
    """
    
    def __init__(self) -> None:
        """Initialize the CodeGenCreateTool with the appropriate endpoint."""
        super().__init__(endpoint="code-generation/create")
    
    async def _call(
        self,
        project_name: str,
        description: str,
        features: List[str],
        tech_stack: str,
        styling: Optional[str] = None,
        canvas_layout: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate new code based on project specifications.
        
        Args:
            project_name: Name of the project.
            description: Description of the project.
            features: List of features to implement.
            tech_stack: Technology stack to use.
            styling: Optional frontend styling framework.
            canvas_layout: Optional canvas layout for UI components.
            **kwargs: Additional parameters to pass to the API.
            
        Returns:
            Dictionary containing generated code or error information.
        """
        payload = {
            "project_name": project_name,
            "description": description,
            "features": features,
            "tech_stack": tech_stack,
            **kwargs
        }
        
        # Add optional parameters only if they have values
        if styling:
            payload["styling"] = styling
            
        if canvas_layout:
            payload["canvas_layout"] = canvas_layout
        
        logger.info(f"Creating code generation for project: {project_name}")
        logger.debug(f"CodeGenCreateTool payload: {payload}")
        
        return await self._make_request(payload)
