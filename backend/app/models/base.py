from sqlalchemy import Column, Integer, DateTime, func, String
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime
from ..database import Base

class BaseMixin:
    """Base model mixin that includes common columns and methods."""
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
