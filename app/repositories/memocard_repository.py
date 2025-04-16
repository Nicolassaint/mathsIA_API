from typing import Dict, List, Optional, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.base import BaseRepository

class MemocardRepository(BaseRepository):
    """Repository for memocard data"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "memocards")
    
    async def create_memocard(self, memocard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new memocard"""
        # Set created_at and updated_at
        now = datetime.utcnow()
        memocard_data["created_at"] = now
        memocard_data["updated_at"] = now
        
        # Create the memocard
        return await self.create(memocard_data)
    
    async def update_memocard(self, id: str, memocard_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a memocard"""
        # Set updated_at
        memocard_data["updated_at"] = datetime.utcnow()
        
        # Update the memocard
        return await self.update(id, memocard_data)
    
    async def find_memocards_by_level(
        self, 
        level: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Find memocards by level"""
        return await self.find_many(
            {"level": level, "is_active": True}, 
            skip=skip, 
            limit=limit,
            sort=[("created_at", -1)]
        )
    
    async def count_memocards_by_level(self, level: str) -> int:
        """Count memocards by level"""
        return await self.count({"level": level, "is_active": True})
    
    async def find_memocards_by_level_and_difficulty(
        self, 
        level: str, 
        difficulty: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Find memocards by level and difficulty"""
        return await self.find_many(
            {"level": level, "difficulty": difficulty, "is_active": True}, 
            skip=skip, 
            limit=limit
        )
    
    async def find_memocards_by_level_and_subject(
        self, 
        level: str, 
        subject: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Find memocards by level and subject"""
        return await self.find_many(
            {"level": level, "subject": subject, "is_active": True}, 
            skip=skip, 
            limit=limit
        )
    
    async def find_memocards_by_level_and_chapter(
        self, 
        level: str, 
        chapter: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Find memocards by level and chapter"""
        return await self.find_many(
            {"level": level, "chapter": chapter, "is_active": True}, 
            skip=skip, 
            limit=limit
        )
        
    async def find_memocards_for_student(
        self,
        student_level: str,
        responded_ids: List[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Find memocards for a student, excluding those already answered"""
        query = {"level": student_level, "is_active": True}
        
        # Exclude already answered memocards if provided
        if responded_ids and len(responded_ids) > 0:
            # Convert string IDs to ObjectId
            object_ids = [ObjectId(id) for id in responded_ids]
            query["_id"] = {"$nin": object_ids}
            
        return await self.find_many(
            query,
            skip=skip,
            limit=limit,
            sort=[("difficulty", 1)]  # Sort by difficulty, easiest first
        )
        
    async def get_subjects_for_level(self, level: str) -> List[str]:
        """Get all subjects for a level"""
        pipeline = [
            {"$match": {"level": level, "is_active": True}},
            {"$group": {"_id": "$subject"}},
            {"$project": {"_id": 0, "subject": "$_id"}},
            {"$sort": {"subject": 1}}
        ]
        
        result = await self.aggregate(pipeline)
        return [doc.get("subject") for doc in result]
        
    async def get_chapters_for_level_and_subject(self, level: str, subject: str) -> List[str]:
        """Get all chapters for a level and subject"""
        pipeline = [
            {"$match": {"level": level, "subject": subject, "is_active": True}},
            {"$group": {"_id": "$chapter"}},
            {"$project": {"_id": 0, "chapter": "$_id"}},
            {"$sort": {"chapter": 1}}
        ]
        
        result = await self.aggregate(pipeline)
        return [doc.get("chapter") for doc in result] 