"""Log model module for system logging.

This module defines the Log model and its related enums and relationships.
"""

from sqlalchemy import Column, String, Text, ForeignKey, Enum, JSON, Integer, DateTime, func
from sqlalchemy.orm import relationship
import enum
from typing import Dict, Any, Optional

from ..database import Base
from .base import BaseMixin


class LogLevel(enum.Enum):
    """Enum representing the possible log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Log(Base, BaseMixin):
    """Model to store system logs.
    
    Attributes:
        id: Unique identifier for the log entry.
        level: Log level (debug, info, warning, error, critical).
        message: Log message content.
        source: Source of the log (e.g., "backend", "frontend", "worker").
        context: Additional context as JSON.
        project_id: Optional reference to a project this log is associated with.
        project: Relationship to the Project model.
    """
    __tablename__ = "logs"
    
    # No need to redefine id, created_at as they come from BaseMixin
    level = Column(Enum(LogLevel), nullable=False)
    message = Column(Text, nullable=False)
    source = Column(String(100), nullable=True)  # e.g., "backend", "frontend", "worker"
    context = Column(JSON, nullable=True)  # Additional context as JSON
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Define relationship to Project
    project = relationship("Project", back_populates="logs")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary.
        
        Returns:
            Dictionary representation of the log entry.
        """
        return {
            "id": self.id,
            "level": self.level.value if self.level else None,
            "message": self.message,
            "source": self.source,
            "context": self.context,
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
