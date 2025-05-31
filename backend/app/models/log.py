from sqlalchemy import Column, String, Text, ForeignKey, Enum, JSON, Integer
import enum
from .base import Base

class LogLevel(enum.Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class Log(Base):
    """Model to store system logs"""
    __tablename__ = "logs"
    
    level = Column(Enum(LogLevel), nullable=False)
    message = Column(Text, nullable=False)
    source = Column(String(100), nullable=True)  # e.g., "backend", "frontend", "worker"
    context = Column(JSON, nullable=True)  # Additional context as JSON
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    
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
