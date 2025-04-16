from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId
from app.core.config import settings
from app.models.user import PyObjectId

class MemocardBase(BaseModel):
    """Base memocard model"""
    title: str
    description: str
    level: str = Field(..., description="School level", enum=settings.SCHOOL_LEVELS)
    difficulty: str = Field(..., description="Difficulty level", enum=settings.DIFFICULTY_LEVELS)
    subject: str
    chapter: str
    type: str = Field(..., description="Question type", enum=settings.MEMOCARD_TYPES)
    is_active: bool = True
    tags: List[str] = []
    
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
                "tags": ["pythagore", "triangle", "rectangle"]
            }
        }

class TrueFalseContent(BaseModel):
    """Content for true/false questions"""
    statement: str
    correct_answer: bool
    
    class Config:
        schema_extra = {
            "example": {
                "statement": "Dans un triangle rectangle, le carré de l'hypoténuse est égal à la somme des carrés des deux autres côtés.",
                "correct_answer": True
            }
        }

class MultipleChoiceContent(BaseModel):
    """Content for multiple choice questions"""
    question: str
    options: List[str]
    correct_options: List[int]  # Indices of correct options
    
    class Config:
        schema_extra = {
            "example": {
                "question": "Quelles sont les propriétés du triangle rectangle ?",
                "options": [
                    "Il possède un angle droit",
                    "Tous ses angles sont égaux",
                    "Le théorème de Pythagore s'y applique",
                    "Il est toujours isocèle"
                ],
                "correct_options": [0, 2]
            }
        }

class TextContent(BaseModel):
    """Content for text response questions"""
    question: str
    correct_answer: str
    case_sensitive: bool = False
    
    class Config:
        schema_extra = {
            "example": {
                "question": "Comment s'appelle le théorème qui s'applique uniquement aux triangles rectangles ?",
                "correct_answer": "théorème de pythagore",
                "case_sensitive": False
            }
        }

class NumericContent(BaseModel):
    """Content for numeric response questions"""
    question: str
    correct_answer: float
    tolerance: float = 0.0  # Tolerance for rounding errors
    unit: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "question": "Dans un triangle rectangle, si les cathètes mesurent 3 cm et 4 cm, quelle est la longueur de l'hypoténuse ?",
                "correct_answer": 5.0,
                "tolerance": 0.1,
                "unit": "cm"
            }
        }

class MemocardInDB(MemocardBase):
    """Memocard model as stored in the database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_by: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    content: Dict[str, Any]  # Will store the appropriate content based on type
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        } 