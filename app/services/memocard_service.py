from typing import Dict, List, Optional, Any, Union
from fastapi import Depends
from bson import ObjectId

from app.repositories.memocard_repository import MemocardRepository
from app.repositories.response_repository import ResponseRepository
from app.db.mongodb import get_database
from app.core.logging_config import logger
from app.middleware.error_handler import AppException
from app.schemas.memocard import MemocardCreate, MemocardUpdate
from app.core.config import settings

class MemocardService:
    """Service for handling memocard-related operations"""
    
    def __init__(
        self, 
        memocard_repository: MemocardRepository = Depends(lambda: MemocardRepository(get_database())),
        response_repository: ResponseRepository = Depends(lambda: ResponseRepository(get_database()))
    ):
        self.memocard_repository = memocard_repository
        self.response_repository = response_repository
    
    async def create_memocard(self, memocard_data: MemocardCreate, created_by: str) -> Dict[str, Any]:
        """
        Create a new memocard
        """
        # Validate level
        if memocard_data.level not in settings.SCHOOL_LEVELS:
            logger.warning(f"Memocard creation failed: Invalid level - {memocard_data.level}")
            raise AppException(
                status_code=400,
                detail=f"Invalid level. Must be one of {settings.SCHOOL_LEVELS}",
                error_code="invalid_level"
            )
        
        # Validate difficulty
        if memocard_data.difficulty not in settings.DIFFICULTY_LEVELS:
            logger.warning(f"Memocard creation failed: Invalid difficulty - {memocard_data.difficulty}")
            raise AppException(
                status_code=400,
                detail=f"Invalid difficulty. Must be one of {settings.DIFFICULTY_LEVELS}",
                error_code="invalid_difficulty"
            )
        
        # Validate type
        if memocard_data.type not in settings.MEMOCARD_TYPES:
            logger.warning(f"Memocard creation failed: Invalid type - {memocard_data.type}")
            raise AppException(
                status_code=400,
                detail=f"Invalid type. Must be one of {settings.MEMOCARD_TYPES}",
                error_code="invalid_type"
            )
        
        # Convert Pydantic model to dict
        memocard_dict = memocard_data.dict()
        
        # Add created_by
        memocard_dict["created_by"] = ObjectId(created_by)
        
        # Create memocard
        memocard = await self.memocard_repository.create_memocard(memocard_dict)
        
        return memocard
        
    async def update_memocard(self, memocard_id: str, memocard_data: MemocardUpdate) -> Dict[str, Any]:
        """
        Update a memocard
        """
        # Find the memocard
        memocard = await self.memocard_repository.find_by_id(memocard_id)
        if not memocard:
            logger.warning(f"Memocard update failed: Memocard not found - {memocard_id}")
            raise AppException(
                status_code=404,
                detail="Memocard not found",
                error_code="memocard_not_found"
            )
        
        # Validate level if provided
        if memocard_data.level is not None and memocard_data.level not in settings.SCHOOL_LEVELS:
            logger.warning(f"Memocard update failed: Invalid level - {memocard_data.level}")
            raise AppException(
                status_code=400,
                detail=f"Invalid level. Must be one of {settings.SCHOOL_LEVELS}",
                error_code="invalid_level"
            )
        
        # Validate difficulty if provided
        if memocard_data.difficulty is not None and memocard_data.difficulty not in settings.DIFFICULTY_LEVELS:
            logger.warning(f"Memocard update failed: Invalid difficulty - {memocard_data.difficulty}")
            raise AppException(
                status_code=400,
                detail=f"Invalid difficulty. Must be one of {settings.DIFFICULTY_LEVELS}",
                error_code="invalid_difficulty"
            )
        
        # Convert Pydantic model to dict, removing None values
        update_data = {k: v for k, v in memocard_data.dict().items() if v is not None}
        
        # Update memocard
        updated_memocard = await self.memocard_repository.update_memocard(memocard_id, update_data)
        if not updated_memocard:
            logger.error(f"Memocard update failed: Update operation failed for memocard {memocard_id}")
            raise AppException(
                status_code=500,
                detail="Failed to update memocard",
                error_code="update_failed"
            )
        
        return updated_memocard
    
    async def get_memocard(self, memocard_id: str) -> Dict[str, Any]:
        """
        Get a memocard by ID
        """
        # Find the memocard
        memocard = await self.memocard_repository.find_by_id(memocard_id)
        if not memocard:
            logger.warning(f"Memocard retrieval failed: Memocard not found - {memocard_id}")
            raise AppException(
                status_code=404,
                detail="Memocard not found",
                error_code="memocard_not_found"
            )
        
        return memocard
    
    async def delete_memocard(self, memocard_id: str) -> bool:
        """
        Delete a memocard
        """
        # Find the memocard
        memocard = await self.memocard_repository.find_by_id(memocard_id)
        if not memocard:
            logger.warning(f"Memocard deletion failed: Memocard not found - {memocard_id}")
            raise AppException(
                status_code=404,
                detail="Memocard not found",
                error_code="memocard_not_found"
            )
        
        # Delete memocard
        success = await self.memocard_repository.delete(memocard_id)
        if not success:
            logger.error(f"Memocard deletion failed: Delete operation failed for memocard {memocard_id}")
            raise AppException(
                status_code=500,
                detail="Failed to delete memocard",
                error_code="delete_failed"
            )
        
        return True
    
    async def get_memocards(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        level: Optional[str] = None,
        difficulty: Optional[str] = None,
        subject: Optional[str] = None,
        chapter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get a list of memocards with optional filters
        """
        # Validate level if provided
        if level is not None and level not in settings.SCHOOL_LEVELS:
            logger.warning(f"Memocards retrieval failed: Invalid level - {level}")
            raise AppException(
                status_code=400,
                detail=f"Invalid level. Must be one of {settings.SCHOOL_LEVELS}",
                error_code="invalid_level"
            )
        
        # Validate difficulty if provided
        if difficulty is not None and difficulty not in settings.DIFFICULTY_LEVELS:
            logger.warning(f"Memocards retrieval failed: Invalid difficulty - {difficulty}")
            raise AppException(
                status_code=400,
                detail=f"Invalid difficulty. Must be one of {settings.DIFFICULTY_LEVELS}",
                error_code="invalid_difficulty"
            )
        
        # Apply filters
        if level and difficulty:
            return await self.memocard_repository.find_memocards_by_level_and_difficulty(level, difficulty, skip, limit)
        elif level and subject:
            return await self.memocard_repository.find_memocards_by_level_and_subject(level, subject, skip, limit)
        elif level and chapter:
            return await self.memocard_repository.find_memocards_by_level_and_chapter(level, chapter, skip, limit)
        elif level:
            return await self.memocard_repository.find_memocards_by_level(level, skip, limit)
        else:
            # No filters, get all memocards
            return await self.memocard_repository.find_many({}, skip, limit)
    
    async def get_memocards_for_student(
        self,
        student_id: str,
        student_level: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get memocards for a student, excluding those already answered
        """
        # Validate level
        if student_level not in settings.SCHOOL_LEVELS:
            logger.warning(f"Memocards retrieval failed: Invalid level - {student_level}")
            raise AppException(
                status_code=400,
                detail=f"Invalid level. Must be one of {settings.SCHOOL_LEVELS}",
                error_code="invalid_level"
            )
        
        # Get IDs of memocards already answered by the student
        answered_memocard_ids = await self.response_repository.get_student_answered_memocard_ids(student_id)
        
        # Get memocards for student
        return await self.memocard_repository.find_memocards_for_student(
            student_level,
            answered_memocard_ids,
            skip,
            limit
        )
    
    async def verify_answer(
        self,
        memocard_id: str,
        student_id: str,
        answer: Any,
        time_spent_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Verify a student's answer to a memocard
        """
        # Find the memocard
        memocard = await self.memocard_repository.find_by_id(memocard_id)
        if not memocard:
            logger.warning(f"Answer verification failed: Memocard not found - {memocard_id}")
            raise AppException(
                status_code=404,
                detail="Memocard not found",
                error_code="memocard_not_found"
            )
        
        # Check if memocard is active
        if not memocard.get("is_active", False):
            logger.warning(f"Answer verification failed: Memocard is inactive - {memocard_id}")
            raise AppException(
                status_code=400,
                detail="Memocard is inactive",
                error_code="inactive_memocard"
            )
        
        # Get previous responses
        previous_responses = await self.response_repository.find_responses_by_student_and_memocard(student_id, memocard_id)
        
        # Calculate attempts
        attempts = len(previous_responses) + 1
        
        # Verify answer based on memocard type
        memocard_type = memocard.get("type")
        content = memocard.get("content", {})
        is_correct = False
        feedback = ""
        
        if memocard_type == "true_false":
            correct_answer = content.get("correct_answer")
            is_correct = answer == correct_answer
            feedback = "Bonne réponse !" if is_correct else "Réponse incorrecte. La bonne réponse est : " + ("Vrai" if correct_answer else "Faux")
        
        elif memocard_type == "multiple_choice":
            correct_options = content.get("correct_options", [])
            
            # Normalize answer to list if it's not already
            answer_list = answer if isinstance(answer, list) else [answer]
            
            # Check if answer matches all correct options
            is_correct = sorted(answer_list) == sorted(correct_options)
            
            if is_correct:
                feedback = "Bonne réponse !"
            else:
                options = content.get("options", [])
                correct_texts = [options[i] for i in correct_options if i < len(options)]
                feedback = "Réponse incorrecte. La bonne réponse est : " + ", ".join(correct_texts)
        
        elif memocard_type == "text":
            correct_answer = content.get("correct_answer", "")
            case_sensitive = content.get("case_sensitive", False)
            
            # Normalize for case insensitivity if needed
            if not case_sensitive:
                answer = answer.lower()
                correct_answer = correct_answer.lower()
            
            is_correct = answer == correct_answer
            feedback = "Bonne réponse !" if is_correct else f"Réponse incorrecte. La bonne réponse est : {correct_answer}"
        
        elif memocard_type == "numeric":
            correct_answer = float(content.get("correct_answer", 0))
            tolerance = float(content.get("tolerance", 0))
            
            # Convert answer to float
            try:
                numeric_answer = float(answer)
            except (ValueError, TypeError):
                is_correct = False
                feedback = f"Réponse invalide. La réponse doit être un nombre."
            else:
                # Check if answer is within tolerance
                is_correct = abs(numeric_answer - correct_answer) <= tolerance
                
                if is_correct:
                    feedback = "Bonne réponse !"
                else:
                    unit = content.get("unit", "")
                    unit_suffix = f" {unit}" if unit else ""
                    feedback = f"Réponse incorrecte. La bonne réponse est : {correct_answer}{unit_suffix}"
        
        else:
            logger.error(f"Answer verification failed: Unknown memocard type - {memocard_type}")
            raise AppException(
                status_code=400,
                detail="Unknown memocard type",
                error_code="unknown_memocard_type"
            )
        
        # Create response record
        response_data = {
            "student_id": ObjectId(student_id),
            "memocard_id": ObjectId(memocard_id),
            "answer": answer,
            "is_correct": is_correct,
            "feedback": feedback,
            "attempts": attempts
        }
        
        if time_spent_seconds is not None:
            response_data["time_spent_seconds"] = time_spent_seconds
        
        response = await self.response_repository.create_response(response_data)
        
        return response 