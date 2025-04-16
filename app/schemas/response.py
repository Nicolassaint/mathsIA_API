from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.response import StudentProgress

class ResponseCreate(BaseModel):
    """Schema for creating a response"""
    memocard_id: str
    answer: Any  # Can be bool, int, str, float, or list of ints depending on question type
    time_spent_seconds: Optional[int] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "memocard_id": "5f7c7f3b9c4a8e1b3c8d7f6f",
                "answer": 5.0,
                "time_spent_seconds": 45
            }
        }
    )

class ResponseResponse(BaseModel):
    """Schema for response response"""
    id: str
    student_id: str
    memocard_id: str
    answer: Any
    is_correct: bool
    feedback: Optional[str] = None
    time_spent_seconds: Optional[int] = None
    attempts: int
    created_at: datetime
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "5f7c7f3b9c4a8e1b3c8d7f70",
                "student_id": "5f7c7f3b9c4a8e1b3c8d7f6e",
                "memocard_id": "5f7c7f3b9c4a8e1b3c8d7f6f",
                "answer": 5.0,
                "is_correct": True,
                "feedback": "Bonne réponse !",
                "time_spent_seconds": 45,
                "attempts": 1,
                "created_at": "2023-01-01T00:00:00Z"
            }
        }
    )

class ProgressResponse(BaseModel):
    """Schema for progress response"""
    student_id: str
    progress: StudentProgress
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "student_id": "5f7c7f3b9c4a8e1b3c8d7f6e",
                "progress": {
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
        }
    )