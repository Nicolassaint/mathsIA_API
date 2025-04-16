from typing import Dict, List, Optional, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.base import BaseRepository
from app.core.security import get_password_hash

class UserRepository(BaseRepository):
    """Repository for user data"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "users")
    
    async def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find a user by username"""
        return await self.find_one({"username": username})
    
    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find a user by email"""
        return await self.find_one({"email": email})
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        # Hash the password
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
        
        # Set created_at and updated_at
        now = datetime.utcnow()
        user_data["created_at"] = now
        user_data["updated_at"] = now
        
        # Create the user
        return await self.create(user_data)
    
    async def update_user(self, id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a user"""
        # Set updated_at
        user_data["updated_at"] = datetime.utcnow()
        
        # Update the user
        return await self.update(id, user_data)
    
    async def update_password(self, id: str, password: str) -> Optional[Dict[str, Any]]:
        """Update a user's password"""
        # Hash the password
        hashed_password = get_password_hash(password)
        
        # Update the user
        return await self.update(id, {
            "hashed_password": hashed_password,
            "updated_at": datetime.utcnow()
        })
    
    async def update_last_login(self, id: str) -> Optional[Dict[str, Any]]:
        """Update a user's last login timestamp"""
        # Update the user
        return await self.update(id, {
            "last_login": datetime.utcnow()
        })
    
    async def find_students(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find all students"""
        return await self.find_many(
            {"role": "student"}, 
            skip=skip, 
            limit=limit,
            sort=[("created_at", -1)]
        )
    
    async def count_students(self) -> int:
        """Count all students"""
        return await self.count({"role": "student"})
    
    async def find_students_by_level(self, level: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find students by level"""
        return await self.find_many(
            {"role": "student", "student_profile.level": level}, 
            skip=skip, 
            limit=limit
        ) 