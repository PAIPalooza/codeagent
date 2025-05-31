from sqlalchemy import Column, String, Text, ForeignKey, Enum, JSON, Integer, DateTime
from sqlalchemy.sql import func
import enum
from .base import BaseMixin
from ..database import Base as DBBase

class LogLevel(enum.Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class Log(DBBase, BaseMixin):
    """Model to store system logs"""
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(Enum(LogLevel), nullable=False)
    message = Column(Text, nullable=False)
    source = Column(String(100), nullable=True)  # e.g., "backend", "frontend", "worker"
    context = Column(JSON, nullable=True)  # Additional context as JSON
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "level": self.level.value if self.level else None,
            "message": self.message,
            "source": self.source,
            "context": self.context,
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
