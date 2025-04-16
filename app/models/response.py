from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.user import PyObjectId

class ResponseBase(BaseModel):
    """Base student response model"""
    student_id: PyObjectId
    memocard_id: PyObjectId
    answer: Any  # Can be bool, int, str, float, or list of ints depending on question type
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        schema_extra = {
            "example": {
                "student_id": "5f7c7f3b9c4a8e1b3c8d7f6e",
                "memocard_id": "5f7c7f3b9c4a8e1b3c8d7f6f",
                "answer": 5.0
            }
        }

class ResponseInDB(ResponseBase):
    """Response model as stored in the database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_correct: bool
    feedback: Optional[str] = None
    time_spent_seconds: Optional[int] = None
    attempts: int = 1
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        schema_extra = {
            "example": {
                "student_id": "5f7c7f3b9c4a8e1b3c8d7f6e",
                "memocard_id": "5f7c7f3b9c4a8e1b3c8d7f6f",
                "answer": 5.0,
                "is_correct": True,
                "feedback": "Bonne réponse !",
                "time_spent_seconds": 45,
                "attempts": 1
            }
        }

class StudentProgress(BaseModel):
    """Student progress statistics"""
    total_memocards: int = 0
    answered_memocards: int = 0
    correct_answers: int = 0
    accuracy_rate: float = 0.0
    average_time_seconds: float = 0.0
    by_difficulty: Dict[str, Dict[str, Any]] = {}
    by_subject: Dict[str, Dict[str, Any]] = {}
    
    class Config:
        schema_extra = {
            "example": {
                "total_memocards": 100,
                "answered_memocards": 50,
                "correct_answers": 45,
                "accuracy_rate": 90.0,
                "average_time_seconds": 30.5,
                "by_difficulty": {
                    "easy": {"total": 30, "answered": 25, "correct": 24, "accuracy": 96.0},
                    "medium": {"total": 40, "answered": 20, "correct": 18, "accuracy": 90.0},
                    "hard": {"total": 20, "answered": 5, "correct": 3, "accuracy": 60.0},
                    "expert": {"total": 10, "answered": 0, "correct": 0, "accuracy": 0.0}
                },
                "by_subject": {
                    "Géométrie": {"total": 40, "answered": 20, "correct": 18, "accuracy": 90.0},
                    "Algèbre": {"total": 30, "answered": 15, "correct": 14, "accuracy": 93.3},
                    "Calcul": {"total": 30, "answered": 15, "correct": 13, "accuracy": 86.7}
                }
            }
        } 