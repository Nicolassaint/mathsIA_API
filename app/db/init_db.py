from app.core.logging_config import logger
from app.core.security import get_password_hash
from app.db.mongodb import get_database
from app.core.config import settings
from pymongo import IndexModel, ASCENDING, TEXT

async def init_db():
    """
    Initialize the database with default data and indexes
    """
    db = get_database()
    logger.info("Creating collections and indexes...")
    
    # Create indexes for users collection
    await db.users.create_indexes([
        IndexModel([("email", ASCENDING)], unique=True),
        IndexModel([("username", ASCENDING)], unique=True)
    ])
    
    # Create indexes for memocards collection
    await db.memocards.create_indexes([
        IndexModel([("title", TEXT)]),
        IndexModel([("level", ASCENDING)]),
        IndexModel([("difficulty", ASCENDING)]),
        IndexModel([("subject", ASCENDING)])
    ])
    
    # Create indexes for responses collection
    await db.responses.create_indexes([
        IndexModel([("student_id", ASCENDING)]),
        IndexModel([("memocard_id", ASCENDING)]),
        IndexModel([("created_at", ASCENDING)])
    ])
    
    # Check if admin user exists, if not create one
    admin_user = await db.users.find_one({"role": "admin"})
    if not admin_user:
        logger.info("Creating default admin user...")
        default_admin = {
            "username": "admin",
            "email": "admin@mathsia.com",
            "hashed_password": get_password_hash("admin"),  # Change in production!
            "full_name": "Admin User",
            "role": "admin",
            "is_active": True
        }
        await db.users.insert_one(default_admin)
        logger.info("Default admin user created successfully")
    
    logger.info("Database initialization completed successfully") 