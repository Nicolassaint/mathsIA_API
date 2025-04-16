from typing import Optional
from pydantic import BaseModel

class TokenPayload(BaseModel):
    """Token payload schema"""
    sub: str
    exp: int
    type: str

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }

class RefreshToken(BaseModel):
    """Refresh token request schema"""
    refresh_token: str
    
    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }

class Login(BaseModel):
    """Login request schema"""
    username: str
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe",
                "password": "secretpassword"
            }
        }

class PasswordChange(BaseModel):
    """Password change request schema"""
    current_password: str
    new_password: str
    
    class Config:
        schema_extra = {
            "example": {
                "current_password": "oldpassword",
                "new_password": "newpassword"
            }
        } 