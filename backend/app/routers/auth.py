"""
Authentication router for user management and authentication endpoints.

This module provides endpoints for user registration, login, profile management,
and GitHub integration.
"""

import logging
from typing import Dict, Any, Optional
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from ..database import get_db
from ..models.user import User
from ..services.auth_service import AuthService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/auth",
    tags=["authentication"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

# Security scheme
security = HTTPBearer()

# Initialize auth service
auth_service = AuthService()


# Request models
class UserRegistrationRequest(BaseModel):
    """Request model for user registration."""
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")


class UserLoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="Password")


class ProfileUpdateRequest(BaseModel):
    """Request model for profile updates."""
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")


class PasswordChangeRequest(BaseModel):
    """Request model for password change."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class GitHubIntegrationRequest(BaseModel):
    """Request model for GitHub integration."""
    code: str = Field(..., description="GitHub OAuth authorization code")


# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    user = auth_service.get_current_user(db, token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


# Authentication endpoints
@router.post("/register")
async def register_user(
    request: UserRegistrationRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    Args:
        request: User registration data
        db: Database session
        
    Returns:
        Dictionary containing user info and success message
    """
    try:
        result = auth_service.create_user(
            db=db,
            email=request.email,
            username=request.username,
            password=request.password,
            full_name=request.full_name
        )
        
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return {
            "success": True,
            "user": result["user"],
            "message": "User registered successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in user registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login")
async def login_user(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login user and return access token.
    
    Args:
        request: User login credentials
        db: Database session
        
    Returns:
        Dictionary containing access token and user info
    """
    try:
        result = auth_service.login_user(
            db=db,
            email=request.email,
            password=request.password
        )
        
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"]
            )
        
        return {
            "access_token": result["access_token"],
            "token_type": result["token_type"],
            "expires_in": result["expires_in"],
            "user": result["user"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in user login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile information.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        User profile data
    """
    return {
        "user": current_user.to_dict(),
        "github_integrated": current_user.has_github_integration()
    }


@router.put("/me")
async def update_user_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.
    
    Args:
        request: Profile update data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Updated user profile
    """
    try:
        updates = {}
        if request.full_name is not None:
            updates["full_name"] = request.full_name
        if request.preferences is not None:
            updates["preferences"] = request.preferences
        
        result = auth_service.update_user_profile(db, current_user, updates)
        
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return {
            "success": True,
            "user": result["user"],
            "message": "Profile updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user's password.
    
    Args:
        request: Password change data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    try:
        result = auth_service.change_password(
            db=db,
            user=current_user,
            current_password=request.current_password,
            new_password=request.new_password
        )
        
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.post("/github/connect")
async def connect_github(
    request: GitHubIntegrationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Connect user's GitHub account.
    
    Args:
        request: GitHub integration data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        GitHub integration status
    """
    try:
        result = await auth_service.setup_github_integration(
            db=db,
            user=current_user,
            github_code=request.code
        )
        
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return {
            "success": True,
            "github_username": result["github_username"],
            "message": "GitHub account connected successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error connecting GitHub: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GitHub connection failed"
        )


@router.delete("/github/disconnect")
async def disconnect_github(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disconnect user's GitHub account.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Disconnection success message
    """
    try:
        current_user.github_username = None
        current_user.github_access_token = None
        db.commit()
        
        logger.info(f"GitHub disconnected for user: {current_user.username}")
        
        return {
            "success": True,
            "message": "GitHub account disconnected successfully"
        }
        
    except Exception as e:
        logger.error(f"Error disconnecting GitHub: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GitHub disconnection failed"
        )


@router.post("/logout")
async def logout_user(
    current_user: User = Depends(get_current_user)
):
    """
    Logout user (invalidate token).
    
    Note: In a stateless JWT implementation, the client should discard the token.
    In production, you might want to maintain a blacklist of revoked tokens.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Logout success message
    """
    logger.info(f"User logged out: {current_user.username}")
    
    return {
        "success": True,
        "message": "Logged out successfully"
    }


# Admin endpoints (require admin role)
@router.get("/admin/users")
async def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    List all users (admin only).
    
    Args:
        current_user: Authenticated user (must be admin)
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of users
    """
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    
    return {
        "users": [user.to_dict() for user in users],
        "total": db.query(User).count()
    }


@router.put("/admin/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user role (admin only).
    
    Args:
        user_id: ID of user to update
        role: New role for the user
        current_user: Authenticated user (must be admin)
        db: Database session
        
    Returns:
        Updated user info
    """
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate role
    valid_roles = ["user", "premium", "admin"]
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    user.role = role
    db.commit()
    
    logger.info(f"User role updated: {user.username} -> {role}")
    
    return {
        "success": True,
        "user": user.to_dict(),
        "message": f"User role updated to {role}"
    }