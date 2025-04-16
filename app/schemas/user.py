from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from app.core.config import settings
from app.models.user import StudentProfile

class UserCreate(BaseModel):
    """Schema for creating a user"""
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: str = Field(..., description="User role", enum=settings.USER_ROLES)
    student_profile: Optional[StudentProfile] = None
    
    @field_validator("role")
    def role_must_be_valid(cls, v):
        if v not in settings.USER_ROLES:
            raise ValueError(f"Role must be one of {settings.USER_ROLES}")
        return v
    
    @field_validator("student_profile")
    def validate_student_profile(cls, v, info):
        values = info.data
        if "role" in values and values["role"] == "student" and v is None:
            raise ValueError("Student profile is required for student role")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "email": "john.doe@example.com",
                "password": "secretpassword",
                "full_name": "John Doe",
                "role": "student",
                "student_profile": {
                    "level": "3e",
                    "class_name": "3e B",
                    "birth_date": "2007-01-01T00:00:00Z"
                }
            }
        }
    )

class UserUpdate(BaseModel):
    """Schema for updating a user"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    student_profile: Optional[StudentProfile] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "John Doe Updated",
                "student_profile": {
                    "level": "4e",
                    "class_name": "4e A"
                }
            }
        }
    )

class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    username: str
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    student_profile: Optional[StudentProfile] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "5f7c7f3b9c4a8e1b3c8d7f6e",
                "username": "johndoe",
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "role": "student",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "last_login": "2023-01-02T10:30:00Z",
                "student_profile": {
                    "level": "3e",
                    "class_name": "3e B",
                    "birth_date": "2007-01-01T00:00:00Z"
                }
            }
        }
    )