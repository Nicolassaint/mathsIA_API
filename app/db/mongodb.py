from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.logging_config import logger

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db = MongoDB()

async def connect_to_mongo():
    """
    Connect to MongoDB
    """
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.db = db.client[settings.MONGODB_DB_NAME]
    logger.info("Connected to MongoDB")

async def close_mongo_connection():
    """
    Close MongoDB connection
    """
    logger.info("Closing MongoDB connection")
    if db.client:
        db.client.close()
    logger.info("MongoDB connection closed")

def get_database():
    """
    Get database instance
    """
    return db.db 