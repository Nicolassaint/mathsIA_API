from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm

from app.services.auth_service import AuthService
from app.middleware.role_checker import get_current_user
from app.schemas.auth import Token, RefreshToken, PasswordChange
from app.core.logging_config import logger

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token, summary="Authenticate and generate tokens")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends()):
    """
    Authenticate a user and generate access and refresh tokens
    
    - **username**: Username or email
    - **password**: User password
    """
    try:
        result = await auth_service.authenticate_user(form_data.username, form_data.password)
        return {
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "token_type": result["token_type"]
        }
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.post("/refresh", response_model=Token, summary="Refresh access token")
async def refresh_token(refresh_token: RefreshToken, auth_service: AuthService = Depends()):
    """
    Create new access and refresh tokens using a valid refresh token
    
    - **refresh_token**: A valid refresh token
    """
    try:
        result = await auth_service.refresh_tokens(refresh_token.refresh_token)
        return result
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.get("/me", summary="Get current user information")
async def get_me(current_user = Depends(get_current_user)):
    """
    Get information about the currently authenticated user
    
    Requires authentication
    """
    return current_user

@router.post("/change-password", summary="Change user password")
async def change_password(
    password_data: PasswordChange,
    current_user = Depends(get_current_user),
    auth_service: AuthService = Depends()
):
    """
    Change the password of the currently authenticated user
    
    - **current_password**: Current password
    - **new_password**: New password
    
    Requires authentication
    """
    try:
        await auth_service.change_password(
            str(current_user["_id"]),
            password_data.current_password,
            password_data.new_password
        )
        return {"message": "Password changed successfully"}
    except Exception as e:
        logger.error(f"Password change failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 