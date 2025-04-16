from typing import Dict, List, Optional, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.base import BaseRepository
from app.models.response import StudentProgress

class ResponseRepository(BaseRepository):
    """Repository for student response data"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "responses")
    
    async def create_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new response"""
        # Set created_at
        response_data["created_at"] = datetime.utcnow()
        
        # Create the response
        return await self.create(response_data)
    
    async def find_responses_by_student(
        self, 
        student_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Find responses by student ID"""
        return await self.find_many(
            {"student_id": ObjectId(student_id)}, 
            skip=skip, 
            limit=limit,
            sort=[("created_at", -1)]
        )
    
    async def find_responses_by_memocard(
        self, 
        memocard_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Find responses by memocard ID"""
        return await self.find_many(
            {"memocard_id": ObjectId(memocard_id)}, 
            skip=skip, 
            limit=limit,
            sort=[("created_at", -1)]
        )
    
    async def find_responses_by_student_and_memocard(
        self, 
        student_id: str, 
        memocard_id: str
    ) -> List[Dict[str, Any]]:
        """Find responses by student ID and memocard ID"""
        return await self.find_many(
            {
                "student_id": ObjectId(student_id),
                "memocard_id": ObjectId(memocard_id)
            },
            sort=[("created_at", -1)]
        )
    
    async def has_student_answered_memocard(self, student_id: str, memocard_id: str) -> bool:
        """Check if a student has already answered a memocard"""
        count = await self.count({
            "student_id": ObjectId(student_id),
            "memocard_id": ObjectId(memocard_id)
        })
        return count > 0
    
    async def get_student_answered_memocard_ids(self, student_id: str) -> List[str]:
        """Get IDs of memocards already answered by a student"""
        pipeline = [
            {"$match": {"student_id": ObjectId(student_id)}},
            {"$group": {"_id": "$memocard_id"}},
            {"$project": {"_id": 1}}
        ]
        
        result = await self.aggregate(pipeline)
        return [str(doc.get("_id")) for doc in result]
        
    async def calculate_student_progress(self, student_id: str, total_memocards_by_level: int) -> StudentProgress:
        """Calculate student progress statistics"""
        student_id_obj = ObjectId(student_id)
        
        # Get basic counts
        total_responses = await self.count({"student_id": student_id_obj})
        
        if total_responses == 0:
            return StudentProgress(total_memocards=total_memocards_by_level)
        
        # Get unique answered memocards
        unique_memocards_pipeline = [
            {"$match": {"student_id": student_id_obj}},
            {"$group": {"_id": "$memocard_id"}}
        ]
        unique_memocards = await self.aggregate(unique_memocards_pipeline)
        answered_memocards = len(unique_memocards)
        
        # Get correct answers count
        correct_answers = await self.count({
            "student_id": student_id_obj,
            "is_correct": True
        })
        
        # Calculate accuracy rate
        accuracy_rate = (correct_answers / total_responses) * 100 if total_responses > 0 else 0.0
        
        # Calculate average time
        time_pipeline = [
            {"$match": {"student_id": student_id_obj, "time_spent_seconds": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": None, "avg_time": {"$avg": "$time_spent_seconds"}}}
        ]
        time_result = await self.aggregate(time_pipeline)
        average_time_seconds = time_result[0].get("avg_time") if time_result else 0.0
        
        # Get statistics by difficulty
        by_difficulty_pipeline = [
            {
                "$lookup": {
                    "from": "memocards",
                    "localField": "memocard_id",
                    "foreignField": "_id",
                    "as": "memocard"
                }
            },
            {"$unwind": "$memocard"},
            {"$match": {"student_id": student_id_obj}},
            {
                "$group": {
                    "_id": "$memocard.difficulty",
                    "answered": {"$sum": 1},
                    "correct": {"$sum": {"$cond": [{"$eq": ["$is_correct", True]}, 1, 0]}}
                }
            }
        ]
        difficulty_results = await self.aggregate(by_difficulty_pipeline)
        
        by_difficulty = {}
        for result in difficulty_results:
            difficulty = result.get("_id")
            answered = result.get("answered", 0)
            correct = result.get("correct", 0)
            accuracy = (correct / answered) * 100 if answered > 0 else 0.0
            
            by_difficulty[difficulty] = {
                "answered": answered,
                "correct": correct,
                "accuracy": accuracy,
                # Total will be filled in later when joined with memocards data
                "total": 0
            }
        
        # Get statistics by subject
        by_subject_pipeline = [
            {
                "$lookup": {
                    "from": "memocards",
                    "localField": "memocard_id",
                    "foreignField": "_id",
                    "as": "memocard"
                }
            },
            {"$unwind": "$memocard"},
            {"$match": {"student_id": student_id_obj}},
            {
                "$group": {
                    "_id": "$memocard.subject",
                    "answered": {"$sum": 1},
                    "correct": {"$sum": {"$cond": [{"$eq": ["$is_correct", True]}, 1, 0]}}
                }
            }
        ]
        subject_results = await self.aggregate(by_subject_pipeline)
        
        by_subject = {}
        for result in subject_results:
            subject = result.get("_id")
            answered = result.get("answered", 0)
            correct = result.get("correct", 0)
            accuracy = (correct / answered) * 100 if answered > 0 else 0.0
            
            by_subject[subject] = {
                "answered": answered,
                "correct": correct,
                "accuracy": accuracy,
                # Total will be filled in later when joined with memocards data
                "total": 0
            }
        
        return StudentProgress(
            total_memocards=total_memocards_by_level,
            answered_memocards=answered_memocards,
            correct_answers=correct_answers,
            accuracy_rate=accuracy_rate,
            average_time_seconds=average_time_seconds,
            by_difficulty=by_difficulty,
            by_subject=by_subject
        ) 