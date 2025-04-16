from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import List, Optional

from app.services.student_service import StudentService
from app.middleware.role_checker import get_admin_user
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.logging_config import logger
from app.core.config import settings

router = APIRouter(prefix="/students", tags=["Admin - Students"])

@router.post("/", response_model=UserResponse, summary="Create a new student")
async def create_student(
    student_data: UserCreate,
    current_user = Depends(get_admin_user),
    student_service: StudentService = Depends()
):
    """
    Create a new student (admin only)
    
    - **username**: Student username
    - **email**: Student email
    - **password**: Student password
    - **full_name**: Student full name
    - **role**: Must be "student"
    - **student_profile**: Contains level, class_name, etc.
    
    Requires admin role
    """
    try:
        result = await student_service.create_student(student_data)
        return result
    except Exception as e:
        logger.error(f"Student creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[UserResponse], summary="Get all students")
async def get_students(
    skip: int = Query(0, ge=0, description="Skip N students"),
    limit: int = Query(100, ge=1, le=100, description="Limit to N students"),
    level: Optional[str] = Query(None, description="Filter by school level"),
    current_user = Depends(get_admin_user),
    student_service: StudentService = Depends()
):
    """
    Get a list of all students (admin only)
    
    - **skip**: Number of students to skip
    - **limit**: Maximum number of students to return
    - **level**: Filter by school level (e.g., "3e")
    
    Requires admin role
    """
    try:
        return await student_service.get_students(skip, limit, level)
    except Exception as e:
        logger.error(f"Students retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{student_id}", response_model=UserResponse, summary="Get a student by ID")
async def get_student(
    student_id: str = Path(..., description="Student ID"),
    current_user = Depends(get_admin_user),
    student_service: StudentService = Depends()
):
    """
    Get a student by ID (admin only)
    
    - **student_id**: ID of the student to retrieve
    
    Requires admin role
    """
    try:
        return await student_service.get_student(student_id)
    except Exception as e:
        logger.error(f"Student retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{student_id}", response_model=UserResponse, summary="Update a student")
async def update_student(
    student_data: UserUpdate,
    student_id: str = Path(..., description="Student ID"),
    current_user = Depends(get_admin_user),
    student_service: StudentService = Depends()
):
    """
    Update a student (admin only)
    
    - **student_id**: ID of the student to update
    - **student_data**: Updated student data
    
    Requires admin role
    """
    try:
        return await student_service.update_student(student_id, student_data)
    except Exception as e:
        logger.error(f"Student update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{student_id}", summary="Delete a student")
async def delete_student(
    student_id: str = Path(..., description="Student ID"),
    current_user = Depends(get_admin_user),
    student_service: StudentService = Depends()
):
    """
    Delete a student (admin only)
    
    - **student_id**: ID of the student to delete
    
    Requires admin role
    """
    try:
        await student_service.delete_student(student_id)
        return {"message": "Student deleted successfully"}
    except Exception as e:
        logger.error(f"Student deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{student_id}/progress", summary="Get a student's progress")
async def get_student_progress(
    student_id: str = Path(..., description="Student ID"),
    current_user = Depends(get_admin_user),
    student_service: StudentService = Depends()
):
    """
    Get a student's progress (admin only)
    
    - **student_id**: ID of the student
    
    Requires admin role
    """
    try:
        return await student_service.get_student_progress(student_id)
    except Exception as e:
        logger.error(f"Student progress retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 