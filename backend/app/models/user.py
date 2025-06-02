"""User model module for authentication and user management.

This module defines the User model and related functionality for user authentication,
profile management, and GitHub integration.
"""

from sqlalchemy import Column, String, Boolean, DateTime, JSON, func
from sqlalchemy.orm import relationship
import enum
from typing import Dict, Any, Optional
from datetime import datetime

from ..database import Base
from .base import BaseMixin


class UserRole(enum.Enum):
    """Enum representing user roles."""
    USER = "user"
    ADMIN = "admin"
    PREMIUM = "premium"


class User(Base, BaseMixin):
    """User model for authentication and profile management.
    
    Attributes:
        id: Unique identifier for the user.
        email: User's email address (unique).
        username: User's username (unique).
        full_name: User's full name.
        hashed_password: Encrypted password.
        is_active: Whether the user account is active.
        is_verified: Whether the user's email is verified.
        role: User's role (user, admin, premium).
        github_username: GitHub username for integration.
        github_access_token: Encrypted GitHub access token.
        preferences: User preferences as JSON.
        last_login: Timestamp of last login.
        projects: Relationship to user's projects.
    """
    __tablename__ = "users"
    
    # Basic user information
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    role = Column(String(20), default=UserRole.USER.value, nullable=False)
    
    # GitHub integration
    github_username = Column(String(100), nullable=True, index=True)
    github_access_token = Column(String(255), nullable=True)  # Should be encrypted
    
    # User preferences and metadata
    preferences = Column(JSON, nullable=True)  # Store user preferences as JSON
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert user model to dictionary.
        
        Args:
            include_sensitive: Whether to include sensitive information
            
        Returns:
            Dictionary representation of the user.
        """
        result = {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "role": self.role,
            "github_username": self.github_username,
            "preferences": self.preferences or {},
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_sensitive:
            result["hashed_password"] = self.hashed_password
            result["github_access_token"] = self.github_access_token
            
        return result
    
    def update_last_login(self) -> None:
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
    
    def has_github_integration(self) -> bool:
        """Check if user has GitHub integration configured."""
        return bool(self.github_username and self.github_access_token)
    
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN.value
    
    def is_premium(self) -> bool:
        """Check if user has premium role."""
        return self.role in [UserRole.PREMIUM.value, UserRole.ADMIN.value]