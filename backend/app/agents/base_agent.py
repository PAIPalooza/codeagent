"""
Base agent class for multi-agent coordination.

This module provides the base class for all specialized agents in the
multi-agent coordination system.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for specialized code generation agents."""
    
    def __init__(self, agent_id: str, name: str):
        """
        Initialize the agent.
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable name for this agent
        """
        self.agent_id = agent_id
        self.name = name
        self.logger = logging.getLogger(f"agent.{name.lower()}")
    
    @abstractmethod
    async def run(self, task_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's task.
        
        Args:
            task_payload: Task-specific parameters and data
            
        Returns:
            Dictionary containing the task result
        """
        pass
    
    def validate_payload(self, payload: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Validate that the payload contains required fields.
        
        Args:
            payload: Payload to validate
            required_fields: List of required field names
            
        Returns:
            True if valid, False otherwise
        """
        missing_fields = [field for field in required_fields if field not in payload]
        if missing_fields:
            self.logger.error(f"Missing required fields: {missing_fields}")
            return False
        return True
    
    def log_start(self, action: str, payload: Dict[str, Any]) -> None:
        """Log the start of an agent action."""
        self.logger.info(f"Starting {action} for agent {self.name}")
        self.logger.debug(f"Payload: {payload}")
    
    def log_success(self, action: str, result: Dict[str, Any]) -> None:
        """Log successful completion of an agent action."""
        self.logger.info(f"Successfully completed {action} for agent {self.name}")
        self.logger.debug(f"Result: {result}")
    
    def log_error(self, action: str, error: str) -> None:
        """Log an error during agent execution."""
        self.logger.error(f"Error in {action} for agent {self.name}: {error}")
    
    def create_error_response(self, action: str, error: str) -> Dict[str, Any]:
        """
        Create a standardized error response.
        
        Args:
            action: The action that failed
            error: Error message
            
        Returns:
            Error response dictionary
        """
        return {
            "error": True,
            "agent": self.name,
            "action": action,
            "message": error
        }
    
    def create_success_response(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a standardized success response.
        
        Args:
            action: The completed action
            data: Result data
            
        Returns:
            Success response dictionary
        """
        return {
            "success": True,
            "agent": self.name,
            "action": action,
            **data
        }