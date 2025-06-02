"""Authentication Service

This service handles user authentication, registration, password management,
and JWT token generation/validation.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import hashlib
import secrets

import httpx
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..models.user import User, UserRole
from ..database import get_db

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for handling user authentication and management."""
    
    def __init__(self):
        self.pwd_context = pwd_context
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = db.query(User).filter(User.email == email).first()
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        
        # Update last login
        user.update_last_login()
        db.commit()
        
        return user
    
    def create_user(self, db: Session, email: str, username: str, password: str, 
                   full_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user account."""
        try:
            # Check if user already exists
            if db.query(User).filter(User.email == email).first():
                return {"error": True, "message": "Email already registered"}
            
            if db.query(User).filter(User.username == username).first():
                return {"error": True, "message": "Username already taken"}
            
            # Validate password strength
            if len(password) < 8:
                return {"error": True, "message": "Password must be at least 8 characters"}
            
            # Create user
            hashed_password = self.get_password_hash(password)
            user = User(
                email=email,
                username=username,
                full_name=full_name,
                hashed_password=hashed_password,
                is_active=True,
                is_verified=False,  # Would be verified via email in production
                role=UserRole.USER.value
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"Created new user: {username} ({email})")
            
            return {
                "success": True,
                "user": user.to_dict(),
                "message": "User created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return {"error": True, "message": "Failed to create user"}
    
    def login_user(self, db: Session, email: str, password: str) -> Dict[str, Any]:
        """Login user and return access token."""
        try:
            user = self.authenticate_user(db, email, password)
            if not user:
                return {"error": True, "message": "Invalid email or password"}
            
            if not user.is_active:
                return {"error": True, "message": "Account is disabled"}
            
            # Create access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(
                data={"sub": user.email, "user_id": user.id},
                expires_delta=access_token_expires
            )
            
            logger.info(f"User logged in: {user.username}")
            
            return {
                "success": True,
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": user.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return {"error": True, "message": "Login failed"}
    
    def get_current_user(self, db: Session, token: str) -> Optional[User]:
        """Get current user from JWT token."""
        try:
            payload = self.verify_token(token)
            if not payload:
                return None
            
            email: str = payload.get("sub")
            if not email:
                return None
            
            user = db.query(User).filter(User.email == email).first()
            return user if user and user.is_active else None
            
        except Exception as e:
            logger.error(f"Error getting current user: {str(e)}")
            return None
    
    def update_user_profile(self, db: Session, user: User, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile information."""
        try:
            allowed_fields = ["full_name", "preferences"]
            
            for field, value in updates.items():
                if field in allowed_fields:
                    setattr(user, field, value)
            
            db.commit()
            db.refresh(user)
            
            return {
                "success": True,
                "user": user.to_dict(),
                "message": "Profile updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return {"error": True, "message": "Failed to update profile"}
    
    def change_password(self, db: Session, user: User, current_password: str, 
                       new_password: str) -> Dict[str, Any]:
        """Change user password."""
        try:
            # Verify current password
            if not self.verify_password(current_password, user.hashed_password):
                return {"error": True, "message": "Current password is incorrect"}
            
            # Validate new password
            if len(new_password) < 8:
                return {"error": True, "message": "New password must be at least 8 characters"}
            
            # Update password
            user.hashed_password = self.get_password_hash(new_password)
            db.commit()
            
            logger.info(f"Password changed for user: {user.username}")
            
            return {
                "success": True,
                "message": "Password changed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            return {"error": True, "message": "Failed to change password"}
    
    async def setup_github_integration(self, db: Session, user: User, 
                                     github_code: str) -> Dict[str, Any]:
        """Setup GitHub integration using OAuth code."""
        try:
            # Exchange code for access token
            github_token = await self._exchange_github_code(github_code)
            if not github_token:
                return {"error": True, "message": "Failed to authenticate with GitHub"}
            
            # Get GitHub user info
            github_user = await self._get_github_user(github_token)
            if not github_user:
                return {"error": True, "message": "Failed to get GitHub user information"}
            
            # Update user with GitHub info
            user.github_username = github_user.get("login")
            user.github_access_token = github_token  # Should encrypt this
            
            db.commit()
            
            logger.info(f"GitHub integration setup for user: {user.username}")
            
            return {
                "success": True,
                "github_username": user.github_username,
                "message": "GitHub integration setup successfully"
            }
            
        except Exception as e:
            logger.error(f"Error setting up GitHub integration: {str(e)}")
            return {"error": True, "message": "Failed to setup GitHub integration"}
    
    async def _exchange_github_code(self, code: str) -> Optional[str]:
        """Exchange GitHub OAuth code for access token."""
        try:
            # In a real implementation, you'd use your GitHub OAuth app credentials
            # For now, return a mock token
            logger.info("Mock GitHub OAuth code exchange")
            return f"mock_github_token_{secrets.token_hex(16)}"
            
        except Exception as e:
            logger.error(f"Error exchanging GitHub code: {str(e)}")
            return None
    
    async def _get_github_user(self, token: str) -> Optional[Dict[str, Any]]:
        """Get GitHub user information using access token."""
        try:
            # Mock GitHub user data
            return {
                "login": f"github_user_{secrets.token_hex(4)}",
                "id": 12345,
                "name": "GitHub User",
                "email": "user@github.com"
            }
            
        except Exception as e:
            logger.error(f"Error getting GitHub user: {str(e)}")
            return None