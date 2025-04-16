from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict

from app.middleware.role_checker import get_student_user
from app.services.student_service import StudentService
from app.schemas.user import UserUpdate, UserResponse
from app.core.logging_config import logger

router = APIRouter(prefix="/profile", tags=["Student - Profile"])

@router.get("/", response_model=UserResponse, summary="Get student profile")
async def get_profile(current_user = Depends(get_student_user)):
    """
    Get the current student's profile
    
    Requires student role
    """
    return current_user

@router.put("/", response_model=UserResponse, summary="Update student profile")
async def update_profile(
    profile_data: UserUpdate,
    current_user = Depends(get_student_user),
    student_service: StudentService = Depends()
):
    """
    Update the current student's profile
    
    - **username**: New username (optional)
    - **email**: New email (optional)
    - **full_name**: New full name (optional)
    - **student_profile**: New student profile (optional)
    
    Requires student role
    """
    try:
        result = await student_service.update_student(str(current_user["_id"]), profile_data)
        return result
    except Exception as e:
        logger.error(f"Profile update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 