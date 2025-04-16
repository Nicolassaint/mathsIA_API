from typing import Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends

from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.config import settings
from app.repositories.user_repository import UserRepository
from app.db.mongodb import get_database
from app.core.logging_config import logger
from app.middleware.error_handler import AppException

class AuthService:
    """Service for handling authentication logic"""
    
    def __init__(self, user_repository: UserRepository = Depends(lambda: UserRepository(get_database()))):
        self.user_repository = user_repository
    
    async def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user with username and password
        """
        # Find the user by username
        user = await self.user_repository.find_by_username(username)
        
        if not user:
            # If not found by username, try email
            user = await self.user_repository.find_by_email(username)
            
        if not user:
            logger.warning(f"Authentication failed: User not found - {username}")
            raise AppException(
                status_code=401,
                detail="Incorrect username or password",
                error_code="invalid_credentials"
            )
        
        # Check password
        if not verify_password(password, user["hashed_password"]):
            logger.warning(f"Authentication failed: Invalid password for user {username}")
            raise AppException(
                status_code=401,
                detail="Incorrect username or password",
                error_code="invalid_credentials"
            )
        
        # Check if user is active
        if not user.get("is_active", False):
            logger.warning(f"Authentication failed: Inactive user {username}")
            raise AppException(
                status_code=400,
                detail="Inactive user",
                error_code="inactive_user"
            )
        
        # Update last login
        await self.user_repository.update_last_login(user["_id"])
        
        # Create tokens
        access_token = create_access_token(subject=str(user["_id"]))
        refresh_token = create_refresh_token(subject=str(user["_id"]))
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }
    
    async def refresh_tokens(self, refresh_token: str) -> Dict[str, str]:
        """
        Create new access and refresh tokens using a valid refresh token
        """
        try:
            # Decode and validate the refresh token
            payload = jwt.decode(
                refresh_token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            
            # Check token type
            if payload.get("type") != "refresh":
                logger.warning("Token refresh failed: Invalid token type")
                raise AppException(
                    status_code=401,
                    detail="Invalid token type",
                    error_code="invalid_token_type"
                )
            
            # Get user ID from token
            user_id = payload.get("sub")
            if not user_id:
                logger.warning("Token refresh failed: Missing user ID in token")
                raise AppException(
                    status_code=401,
                    detail="Invalid token",
                    error_code="invalid_token"
                )
            
            # Find the user
            user = await self.user_repository.find_by_id(user_id)
            if not user:
                logger.warning(f"Token refresh failed: User not found - {user_id}")
                raise AppException(
                    status_code=401,
                    detail="Invalid token",
                    error_code="invalid_token"
                )
            
            # Check if user is active
            if not user.get("is_active", False):
                logger.warning(f"Token refresh failed: Inactive user {user_id}")
                raise AppException(
                    status_code=400,
                    detail="Inactive user",
                    error_code="inactive_user"
                )
            
            # Create new tokens
            new_access_token = create_access_token(subject=str(user["_id"]))
            new_refresh_token = create_refresh_token(subject=str(user["_id"]))
            
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer"
            }
            
        except JWTError as e:
            logger.warning(f"Token refresh failed: JWT error - {str(e)}")
            raise AppException(
                status_code=401,
                detail="Invalid token",
                error_code="invalid_token"
            )
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Change a user's password
        """
        # Find the user
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            logger.warning(f"Password change failed: User not found - {user_id}")
            raise AppException(
                status_code=404,
                detail="User not found",
                error_code="user_not_found"
            )
        
        # Verify current password
        if not verify_password(current_password, user["hashed_password"]):
            logger.warning(f"Password change failed: Invalid current password for user {user_id}")
            raise AppException(
                status_code=400,
                detail="Current password is incorrect",
                error_code="invalid_password"
            )
        
        # Update password
        user = await self.user_repository.update_password(user_id, new_password)
        if not user:
            logger.error(f"Password change failed: Update failed for user {user_id}")
            raise AppException(
                status_code=500,
                detail="Failed to update password",
                error_code="update_failed"
            )
        
        return True 