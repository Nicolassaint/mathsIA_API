from typing import Any, Dict, List, Optional, Union
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.logging_config import logger

class BaseRepository:
    """Base repository class for MongoDB collections"""
    
    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str):
        self.db = database
        self.collection_name = collection_name
        self.collection = database[collection_name]
    
    async def find_by_id(self, id: Union[str, ObjectId]) -> Optional[Dict[str, Any]]:
        """Find a document by ID"""
        if isinstance(id, str):
            id = ObjectId(id)
        
        document = await self.collection.find_one({"_id": id})
        return document
    
    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find one document by query"""
        document = await self.collection.find_one(query)
        return document
    
    async def find_many(
        self, 
        query: Dict[str, Any], 
        skip: int = 0, 
        limit: int = 100,
        sort: List[tuple] = None
    ) -> List[Dict[str, Any]]:
        """Find many documents by query with pagination and sorting"""
        cursor = self.collection.find(query).skip(skip).limit(limit)
        
        if sort:
            cursor = cursor.sort(sort)
            
        documents = await cursor.to_list(length=limit)
        return documents
    
    async def count(self, query: Dict[str, Any]) -> int:
        """Count documents matching a query"""
        count = await self.collection.count_documents(query)
        return count
    
    async def create(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document"""
        result = await self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document
    
    async def update(self, id: Union[str, ObjectId], update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a document by ID"""
        if isinstance(id, str):
            id = ObjectId(id)
            
        result = await self.collection.update_one(
            {"_id": id},
            {"$set": update}
        )
        
        if result.modified_count == 0:
            return None
            
        return await self.find_by_id(id)
    
    async def delete(self, id: Union[str, ObjectId]) -> bool:
        """Delete a document by ID"""
        if isinstance(id, str):
            id = ObjectId(id)
            
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count > 0
    
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run an aggregation pipeline"""
        cursor = self.collection.aggregate(pipeline)
        documents = await cursor.to_list(length=None)
        return documents 