"""Project model module for code generation projects.

This module defines the Project model and its related enums and relationships.
"""

from sqlalchemy import Column, String, Text, JSON, Enum, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
import enum
from typing import Dict, Any, List, Optional

from ..database import Base
from .base import BaseMixin


class ProjectStatus(enum.Enum):
    """Enum representing the possible statuses of a project."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COORDINATING = "coordinating"  # Multi-agent workflow coordination phase
    GENERATING = "generating"  # Active generation using coordination
    COMPLETED = "completed"
    SUCCESS = "success"  # Successfully completed with download ZIP available
    FAILED = "failed"


class Project(Base, BaseMixin):
    """Project model representing a code generation project.
    
    Attributes:
        id: Unique identifier for the project.
        name: Name of the project.
        description: Optional description of the project.
        status: Current status of the project (draft, in_progress, completed, failed).
        tech_stack: Technologies used in the project (e.g., "react-fastapi-postgresql").
        styling: CSS framework used (e.g., "tailwind", "bootstrap").
        canvas_layout: JSON representation of the canvas layout.
        user_id: ID of the user who owns the project.
        generation_steps: Relationship to GenerationStep models.
        logs: Relationship to Log models.
    """
    __tablename__ = "projects"
    
    # No need to redefine id, created_at, updated_at as they come from BaseMixin
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    features = Column(JSON, nullable=True)  # Store features as JSON array
    status = Column(Enum(ProjectStatus), default="draft", nullable=False)
    tech_stack = Column(String(100), nullable=True)  # e.g., "react-fastapi-postgresql"
    styling = Column(String(50), nullable=True)  # e.g., "tailwind", "bootstrap"
    canvas_layout = Column(JSON, nullable=True)  # Store the canvas layout as JSON
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    download_url = Column(String(512), nullable=True)  # URL to download the generated ZIP file
    coordination_workflow_id = Column(String(255), nullable=True, index=True)  # AINative workflow ID
    
    # Define relationships - these will be properly loaded when SQLAlchemy imports all models
    generation_steps = relationship("GenerationStep", back_populates="project", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="project", cascade="all, delete-orphan")
    user = relationship("User", back_populates="projects")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary with related models.
        
        Returns:
            Dictionary representation of the project and its related models.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "features": self.features,
            "status": self.status.value if self.status else None,
            "tech_stack": self.tech_stack,
            "styling": self.styling,
            "canvas_layout": self.canvas_layout,
            "user_id": self.user_id,
            "download_url": self.download_url,
            "coordination_workflow_id": self.coordination_workflow_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "generation_steps": [step.to_dict() for step in self.generation_steps] if self.generation_steps else [],
            "logs": [log.to_dict() for log in self.logs] if self.logs else []
        }
