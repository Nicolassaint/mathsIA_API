from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.core.config import settings
from app.models.memocard import TrueFalseContent, MultipleChoiceContent, TextContent, NumericContent

class MemocardCreate(BaseModel):
    """Schema for creating a memocard"""
    title: str
    description: str
    level: str = Field(..., description="School level", enum=settings.SCHOOL_LEVELS)
    difficulty: str = Field(..., description="Difficulty level", enum=settings.DIFFICULTY_LEVELS)
    subject: str
    chapter: str
    type: str = Field(..., description="Question type", enum=settings.MEMOCARD_TYPES)
    is_active: bool = True
    tags: List[str] = []
    content: Dict[str, Any]
    
    @validator("level")
    def level_must_be_valid(cls, v):
        if v not in settings.SCHOOL_LEVELS:
            raise ValueError(f"Level must be one of {settings.SCHOOL_LEVELS}")
        return v
    
    @validator("difficulty")
    def difficulty_must_be_valid(cls, v):
        if v not in settings.DIFFICULTY_LEVELS:
            raise ValueError(f"Difficulty must be one of {settings.DIFFICULTY_LEVELS}")
        return v
    
    @validator("type")
    def type_must_be_valid(cls, v):
        if v not in settings.MEMOCARD_TYPES:
            raise ValueError(f"Type must be one of {settings.MEMOCARD_TYPES}")
        return v
    
    @validator("content")
    def validate_content(cls, v, values):
        if "type" not in values:
            raise ValueError("Type is required to validate content")
        
        card_type = values["type"]
        try:
            if card_type == "true_false":
                TrueFalseContent(**v)
            elif card_type == "multiple_choice":
                MultipleChoiceContent(**v)
            elif card_type == "text":
                TextContent(**v)
            elif card_type == "numeric":
                NumericContent(**v)
            else:
                raise ValueError(f"Unknown card type: {card_type}")
        except Exception as e:
            raise ValueError(f"Invalid content for type {card_type}: {str(e)}")
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Pythagore - Application directe",
                "description": "Application directe du théorème de Pythagore dans un triangle rectangle",
                "level": "4e",
                "difficulty": "medium",
                "subject": "Géométrie",
                "chapter": "Théorème de Pythagore",
                "type": "numeric",
                "is_active": True,
                "tags": ["pythagore", "triangle", "rectangle"],
                "content": {
                    "question": "Dans un triangle rectangle, si les cathètes mesurent 3 cm et 4 cm, quelle est la longueur de l'hypoténuse ?",
                    "correct_answer": 5.0,
                    "tolerance": 0.1,
                    "unit": "cm"
                }
            }
        }

class MemocardUpdate(BaseModel):
    """Schema for updating a memocard"""
    title: Optional[str] = None
    description: Optional[str] = None
    level: Optional[str] = None
    difficulty: Optional[str] = None
    subject: Optional[str] = None
    chapter: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    content: Optional[Dict[str, Any]] = None
    
    @validator("level")
    def level_must_be_valid(cls, v):
        if v is not None and v not in settings.SCHOOL_LEVELS:
            raise ValueError(f"Level must be one of {settings.SCHOOL_LEVELS}")
        return v
    
    @validator("difficulty")
    def difficulty_must_be_valid(cls, v):
        if v is not None and v not in settings.DIFFICULTY_LEVELS:
            raise ValueError(f"Difficulty must be one of {settings.DIFFICULTY_LEVELS}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Pythagore - Application directe (Update)",
                "difficulty": "easy",
                "content": {
                    "question": "Dans un triangle rectangle, si les cathètes mesurent 5 cm et 12 cm, quelle est la longueur de l'hypoténuse ?",
                    "correct_answer": 13.0,
                    "tolerance": 0.1,
                    "unit": "cm"
                }
            }
        }

class MemocardResponse(BaseModel):
    """Schema for memocard response"""
    id: str
    title: str
    description: str
    level: str
    difficulty: str
    subject: str
    chapter: str
    type: str
    is_active: bool
    tags: List[str]
    content: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "id": "5f7c7f3b9c4a8e1b3c8d7f6f",
                "title": "Pythagore - Application directe",
                "description": "Application directe du théorème de Pythagore dans un triangle rectangle",
                "level": "4e",
                "difficulty": "medium",
                "subject": "Géométrie",
                "chapter": "Théorème de Pythagore",
                "type": "numeric",
                "is_active": True,
                "tags": ["pythagore", "triangle", "rectangle"],
                "content": {
                    "question": "Dans un triangle rectangle, si les cathètes mesurent 3 cm et 4 cm, quelle est la longueur de l'hypoténuse ?",
                    "correct_answer": 5.0,
                    "tolerance": 0.1,
                    "unit": "cm"
                },
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
        } 