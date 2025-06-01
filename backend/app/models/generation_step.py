"""GenerationStep model module for tracking code generation steps.

This module defines the GenerationStep model and its related enums and relationships.
"""

from sqlalchemy import Column, String, Text, ForeignKey, Enum, JSON, Integer, DateTime, func
from sqlalchemy.orm import relationship
import enum
from typing import Dict, Any, Optional

from ..database import Base
from .base import BaseMixin


class StepStatus(enum.Enum):
    """Enum representing the possible statuses of a generation step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationStep(Base, BaseMixin):
    """Model to track individual steps in the code generation process.
    
    Attributes:
        id: Unique identifier for the generation step.
        project_id: Foreign key reference to the project this step belongs to.
        step_name: Name of the generation step (e.g., "generate_models", "create_routes").
        status: Current status of the step.
        details: Additional JSON details about the step.
        error: Error message if the step failed.
        project: Relationship to the parent Project model.
    """
    __tablename__ = "generation_steps"
    
    # No need to redefine id, created_at, updated_at as they come from BaseMixin
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    step_name = Column(String(100), nullable=False)  # e.g., "generate_models", "create_routes"
    tool_name = Column(String(100), nullable=False)  # e.g., "codegen_create", "codegen_refactor"
    sequence_order = Column(Integer, nullable=False, default=0)  # Order in which steps should be executed
    status = Column(Enum(StepStatus), default=StepStatus.PENDING, nullable=False)
    input_payload = Column(JSON, nullable=True)  # Input data for the tool
    output_payload = Column(JSON, nullable=True)  # Output data from the tool
    details = Column(JSON, nullable=True)  # Additional details about the step
    error = Column(Text, nullable=True)  # Error message if the step failed
    
    # Define relationship to Project
    project = relationship("Project", back_populates="generation_steps")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary.
        
        Returns:
            Dictionary representation of the generation step.
        """
        return {
            "id": self.id,
            "project_id": self.project_id,
            "step_name": self.step_name,
            "tool_name": self.tool_name,
            "sequence_order": self.sequence_order,
            "status": self.status.value if self.status else None,
            "input_payload": self.input_payload,
            "output_payload": self.output_payload,
            "details": self.details,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
