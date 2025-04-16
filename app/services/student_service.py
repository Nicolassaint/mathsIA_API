from typing import Dict, List, Optional, Any
from fastapi import Depends, Query
from bson import ObjectId

from app.repositories.user_repository import UserRepository
from app.repositories.memocard_repository import MemocardRepository
from app.repositories.response_repository import ResponseRepository
from app.db.mongodb import get_database
from app.core.logging_config import logger
from app.middleware.error_handler import AppException
from app.schemas.user import UserCreate, UserUpdate
from app.core.config import settings

class StudentService:
    """Service for handling student-related operations"""
    
    def __init__(
        self, 
        user_repository: UserRepository = Depends(lambda: UserRepository(get_database())),
        memocard_repository: MemocardRepository = Depends(lambda: MemocardRepository(get_database())),
        response_repository: ResponseRepository = Depends(lambda: ResponseRepository(get_database()))
    ):
        self.user_repository = user_repository
        self.memocard_repository = memocard_repository
        self.response_repository = response_repository
    
    async def create_student(self, student_data: UserCreate) -> Dict[str, Any]:
        """
        Create a new student
        """
        # Verify role is student
        if student_data.role != "student":
            logger.warning(f"Student creation failed: Invalid role - {student_data.role}")
            raise AppException(
                status_code=400,
                detail="Role must be 'student'",
                error_code="invalid_role"
            )
        
        # Verify student profile has a valid level
        if not student_data.student_profile or student_data.student_profile.level not in settings.SCHOOL_LEVELS:
            logger.warning(f"Student creation failed: Invalid level")
            raise AppException(
                status_code=400,
                detail=f"Student profile must have a valid level: {settings.SCHOOL_LEVELS}",
                error_code="invalid_level"
            )
        
        # Check if username already exists
        existing_user = await self.user_repository.find_by_username(student_data.username)
        if existing_user:
            logger.warning(f"Student creation failed: Username already exists - {student_data.username}")
            raise AppException(
                status_code=409,
                detail="Username already exists",
                error_code="username_exists"
            )
        
        # Check if email already exists
        existing_user = await self.user_repository.find_by_email(student_data.email)
        if existing_user:
            logger.warning(f"Student creation failed: Email already exists - {student_data.email}")
            raise AppException(
                status_code=409,
                detail="Email already exists",
                error_code="email_exists"
            )
        
        # Convert Pydantic model to dict
        student_dict = student_data.dict()
        
        # Create student
        student = await self.user_repository.create_user(student_dict)
        
        return student
    
    async def update_student(self, student_id: str, student_data: UserUpdate) -> Dict[str, Any]:
        """
        Update a student
        """
        # Find the student
        student = await self.user_repository.find_by_id(student_id)
        if not student:
            logger.warning(f"Student update failed: Student not found - {student_id}")
            raise AppException(
                status_code=404,
                detail="Student not found",
                error_code="student_not_found"
            )
        
        # Verify it's a student
        if student.get("role") != "student":
            logger.warning(f"Student update failed: Not a student - {student_id}")
            raise AppException(
                status_code=400,
                detail="User is not a student",
                error_code="not_a_student"
            )
        
        # Check if updating username and it already exists
        if student_data.username and student_data.username != student.get("username"):
            existing_user = await self.user_repository.find_by_username(student_data.username)
            if existing_user:
                logger.warning(f"Student update failed: Username already exists - {student_data.username}")
                raise AppException(
                    status_code=409,
                    detail="Username already exists",
                    error_code="username_exists"
                )
        
        # Check if updating email and it already exists
        if student_data.email and student_data.email != student.get("email"):
            existing_user = await self.user_repository.find_by_email(student_data.email)
            if existing_user:
                logger.warning(f"Student update failed: Email already exists - {student_data.email}")
                raise AppException(
                    status_code=409,
                    detail="Email already exists",
                    error_code="email_exists"
                )
        
        # Convert Pydantic model to dict, removing None values
        update_data = {k: v for k, v in student_data.dict().items() if v is not None}
        
        # Update student
        updated_student = await self.user_repository.update_user(student_id, update_data)
        if not updated_student:
            logger.error(f"Student update failed: Update operation failed for student {student_id}")
            raise AppException(
                status_code=500,
                detail="Failed to update student",
                error_code="update_failed"
            )
        
        return updated_student
    
    async def get_student(self, student_id: str) -> Dict[str, Any]:
        """
        Get a student by ID
        """
        # Find the student
        student = await self.user_repository.find_by_id(student_id)
        if not student:
            logger.warning(f"Student retrieval failed: Student not found - {student_id}")
            raise AppException(
                status_code=404,
                detail="Student not found",
                error_code="student_not_found"
            )
        
        # Verify it's a student
        if student.get("role") != "student":
            logger.warning(f"Student retrieval failed: Not a student - {student_id}")
            raise AppException(
                status_code=400,
                detail="User is not a student",
                error_code="not_a_student"
            )
        
        return student
    
    async def delete_student(self, student_id: str) -> bool:
        """
        Delete a student
        """
        # Find the student
        student = await self.user_repository.find_by_id(student_id)
        if not student:
            logger.warning(f"Student deletion failed: Student not found - {student_id}")
            raise AppException(
                status_code=404,
                detail="Student not found",
                error_code="student_not_found"
            )
        
        # Verify it's a student
        if student.get("role") != "student":
            logger.warning(f"Student deletion failed: Not a student - {student_id}")
            raise AppException(
                status_code=400,
                detail="User is not a student",
                error_code="not_a_student"
            )
        
        # Delete student
        success = await self.user_repository.delete(student_id)
        if not success:
            logger.error(f"Student deletion failed: Delete operation failed for student {student_id}")
            raise AppException(
                status_code=500,
                detail="Failed to delete student",
                error_code="delete_failed"
            )
        
        return True
    
    async def get_students(self, skip: int = 0, limit: int = 100, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get a list of students
        """
        # Get students by level if specified
        if level:
            if level not in settings.SCHOOL_LEVELS:
                logger.warning(f"Students retrieval failed: Invalid level - {level}")
                raise AppException(
                    status_code=400,
                    detail=f"Invalid level. Must be one of {settings.SCHOOL_LEVELS}",
                    error_code="invalid_level"
                )
            return await self.user_repository.find_students_by_level(level, skip, limit)
        
        # Get all students
        return await self.user_repository.find_students(skip, limit)
    
    async def count_students(self) -> int:
        """
        Count the number of students
        """
        return await self.user_repository.count_students()
    
    async def get_student_progress(self, student_id: str) -> Dict[str, Any]:
        """
        Get a student's progress
        """
        # Find the student
        student = await self.user_repository.find_by_id(student_id)
        if not student:
            logger.warning(f"Student progress retrieval failed: Student not found - {student_id}")
            raise AppException(
                status_code=404,
                detail="Student not found",
                error_code="student_not_found"
            )
        
        # Verify it's a student
        if student.get("role") != "student":
            logger.warning(f"Student progress retrieval failed: Not a student - {student_id}")
            raise AppException(
                status_code=400,
                detail="User is not a student",
                error_code="not_a_student"
            )
        
        # Get student level
        student_level = student.get("student_profile", {}).get("level")
        if not student_level:
            logger.warning(f"Student progress retrieval failed: Student has no level - {student_id}")
            raise AppException(
                status_code=400,
                detail="Student has no level",
                error_code="no_level"
            )
        
        # Count total memocards for student's level
        total_memocards = await self.memocard_repository.count_memocards_by_level(student_level)
        
        # Calculate student progress
        progress = await self.response_repository.calculate_student_progress(student_id, total_memocards)
        
        return {
            "student_id": student_id,
            "progress": progress
        } 