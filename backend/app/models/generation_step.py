from sqlalchemy import Column, String, Text, ForeignKey, Enum, JSON, Integer, DateTime
from sqlalchemy.sql import func
import enum
from .base import BaseMixin
from ..database import Base as DBBase

class StepStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class GenerationStep(DBBase, BaseMixin):
    """Model to track individual steps in the code generation process"""
    __tablename__ = "generation_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    sequence_order = Column(Integer, nullable=False)  # Order of execution
    tool_name = Column(String(100), nullable=False)  # Name of the tool to execute
    input_payload = Column(JSON, nullable=True)  # Input parameters for the tool
    status = Column(Enum(StepStatus), default=StepStatus.PENDING, nullable=False)
    details = Column(JSON, nullable=True)  # Additional details about the step
    error = Column(Text, nullable=True)  # Error message if the step failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "sequence_order": self.sequence_order,
            "tool_name": self.tool_name,
            "input_payload": self.input_payload,
            "status": self.status.value if self.status else None,
            "details": self.details,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
