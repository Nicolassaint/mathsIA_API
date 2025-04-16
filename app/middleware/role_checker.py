from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from typing import List, Optional

from app.core.config import settings
from app.core.security import decode_token
from app.schemas.auth import TokenPayload
from app.middleware.error_handler import AppException
from app.repositories.user_repository import UserRepository
from app.db.mongodb import get_database

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    scheme_name="JWT"
)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(lambda: UserRepository(get_database()))
):
    """
    Get the current user from a JWT token
    """
    try:
        payload = decode_token(token)
        token_data = TokenPayload(**payload)
        
        if token_data.type != "access":
            raise AppException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                error_code="invalid_token_type"
            )
    except (JWTError, ValidationError):
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            error_code="invalid_token"
        )
    
    user = await user_repo.find_by_id(token_data.sub)
    if not user:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            error_code="user_not_found"
        )
    
    if not user.get("is_active", False):
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
            error_code="inactive_user"
        )
    
    return user

def has_role(required_roles: List[str]):
    """
    Check if the current user has one of the required roles
    """
    async def _has_role(current_user = Depends(get_current_user)):
        if not current_user:
            raise AppException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                error_code="not_authenticated"
            )
        
        # Admin has access to everything
        if current_user.get("role") == "admin":
            return current_user
            
        if current_user.get("role") not in required_roles:
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted",
                error_code="insufficient_permissions"
            )
        return current_user
    
    return _has_role

# Specific role dependencies
get_admin_user = has_role(["admin"])
get_student_user = has_role(["student"]) 