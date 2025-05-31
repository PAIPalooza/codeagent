"""Code Generation Refactor Tool for AINative API.

This module provides a wrapper for the AINative code-generation/refactor endpoint
that refactors existing code based on provided specifications.
"""

import logging
from typing import Any, Dict, List, Optional

from .base import AINativeBaseTool

# Configure logging
logger = logging.getLogger(__name__)


class CodeGenRefactorTool(AINativeBaseTool):
    """Wrapper for AINative code-generation/refactor endpoint.
    
    This class provides methods to refactor existing code based on
    specific requirements and instructions.
    """
    
    def __init__(self) -> None:
        """Initialize the CodeGenRefactorTool with the appropriate endpoint."""
        super().__init__(endpoint="code-generation/refactor")
    
    async def _call(
        self,
        code: str,
        instructions: str,
        file_path: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Refactor code based on provided instructions.
        
        Args:
            code: The source code to refactor.
            instructions: Detailed instructions for the refactoring.
            file_path: Optional file path to provide context.
            language: Optional programming language of the code.
            **kwargs: Additional parameters to pass to the API.
            
        Returns:
            Dictionary containing refactored code or error information.
        """
        payload = {
            "code": code,
            "instructions": instructions,
            **kwargs
        }
        
        # Add optional parameters only if they have values
        if file_path:
            payload["file_path"] = file_path
            
        if language:
            payload["language"] = language
        
        logger.info("Refactoring code")
        logger.debug(f"CodeGenRefactorTool payload length: {len(code)} chars")
        
        return await self._make_request(payload)
