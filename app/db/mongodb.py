from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.logging_config import logger
from urllib.parse import quote_plus

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db = MongoDB()

async def connect_to_mongo():
    """
    Connect to MongoDB
    """
    # Build connection URL with authentication if credentials are provided
    mongo_url = settings.MONGODB_URL
    
    if settings.MONGODB_USERNAME and settings.MONGODB_PASSWORD:
        # If the URL is a standard mongodb:// format and credentials are separate
        if mongo_url.startswith("mongodb://") and "@" not in mongo_url:
            username = quote_plus(settings.MONGODB_USERNAME)
            password = quote_plus(settings.MONGODB_PASSWORD)
            auth_source = settings.MONGODB_AUTH_SOURCE
            
            # Split the URL to insert credentials
            prefix = "mongodb://"
            remaining = mongo_url[len(prefix):]
            
            # Ensure there's a / after the host and before any query parameters
            if remaining.endswith('/'):
                mongo_url = f"{prefix}{username}:{password}@{remaining}"
            else:
                # Check if we have a path segment after the host
                if '/' in remaining:
                    host, path = remaining.split('/', 1)
                    mongo_url = f"{prefix}{username}:{password}@{host}/{path}"
                else:
                    # No path segment, add a trailing slash
                    mongo_url = f"{prefix}{username}:{password}@{remaining}/"
            
            # Add authSource if not already in the URL
            if "authSource=" not in mongo_url:
                separator = "&" if "?" in mongo_url else "?"
                mongo_url = f"{mongo_url}{separator}authSource={auth_source}"
    
    logger.info(f"Connecting to MongoDB at {mongo_url.replace(quote_plus(settings.MONGODB_PASSWORD) if settings.MONGODB_PASSWORD else '', '***')}")
    db.client = AsyncIOMotorClient(mongo_url)
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