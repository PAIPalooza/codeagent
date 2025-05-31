from sqlalchemy import Column, String, Text, JSON, ForeignKey, Enum, Integer, DateTime
from sqlalchemy.sql import func
import enum
from .base import Base, BaseMixin
from ..database import Base as DBBase

class ProjectStatus(enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Project(DBBase, BaseMixin):
    """Project model representing a code generation project"""
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, index=True)  # UUID as string
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False)
    tech_stack = Column(String(100), nullable=True)  # e.g., "react-fastapi-postgresql"
    styling = Column(String(50), nullable=True)  # e.g., "tailwind", "bootstrap"
    canvas_layout = Column(JSON, nullable=True)  # Store the canvas layout as JSON
    user_id = Column(String(36), nullable=True)  # Store UUID as string for SQLite compatibility
    agent_id = Column(String(36), nullable=True)  # Store agent UUID as string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value if self.status else None,
            "tech_stack": self.tech_stack,
            "styling": self.styling,
            "canvas_layout": self.canvas_layout,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
