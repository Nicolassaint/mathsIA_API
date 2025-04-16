from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.services.student_service import StudentService
from app.middleware.role_checker import get_student_user
from app.schemas.response import ProgressResponse
from app.core.logging_config import logger

router = APIRouter(prefix="/progress", tags=["Student - Progress"])

@router.get("/", summary="Get student's progress")
async def get_progress(
    current_user = Depends(get_student_user),
    student_service: StudentService = Depends()
):
    """
    Get the current student's progress
    
    Requires student role
    """
    try:
        return await student_service.get_student_progress(str(current_user["_id"]))
    except Exception as e:
        logger.error(f"Progress retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 