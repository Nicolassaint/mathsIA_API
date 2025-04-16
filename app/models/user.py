from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from app.core.config import settings

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class UserBase(BaseModel):
    """Base user model"""
    username: str
    email: EmailStr
    full_name: str
    role: str = Field(..., description="User role", enum=settings.USER_ROLES)
    is_active: bool = True
    
    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "role": "student",
                "is_active": True
            }
        }

class StudentProfile(BaseModel):
    """Student profile model"""
    level: str = Field(..., description="School level", enum=settings.SCHOOL_LEVELS)
    class_name: Optional[str] = None
    birth_date: Optional[datetime] = None
    
    class Config:
        schema_extra = {
            "example": {
                "level": "3e",
                "class_name": "3e B",
                "birth_date": "2007-01-01T00:00:00Z"
            }
        }

class UserInDB(UserBase):
    """User model as stored in the database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    student_profile: Optional[StudentProfile] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        } 