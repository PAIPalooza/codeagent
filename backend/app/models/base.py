"""Base model classes and mixins for SQLAlchemy models.

This module provides base classes and mixins for database models,
including common columns and utility methods that all models can inherit.
"""

from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from typing import Dict, Any, Optional

class BaseMixin:
    """Base model mixin that includes common columns and methods.
    
    This mixin adds standard fields (id, timestamps) and utility methods to models.
    It should be used with SQLAlchemy declarative base classes.
    
    Attributes:
        id: Primary key column.
        created_at: Timestamp when the record was created.
        updated_at: Timestamp when the record was last updated.
    """
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name automatically from class name.
        
        Returns:
            The lowercase class name as table name.
        """
        return cls.__name__.lower()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary.
        
        Returns:
            Dictionary with column names as keys and column values as values.
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
