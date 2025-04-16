from typing import Any, Dict, List, Optional
import os
from pydantic import BaseSettings, validator
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "MathsIA API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_key_change_in_production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "mathsia_db")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Available school levels
    SCHOOL_LEVELS: List[str] = ["6e", "5e", "4e", "3e", "2nde", "1ere", "Terminale"]
    
    # User roles
    USER_ROLES: List[str] = ["admin", "student"]
    
    # Memocard types
    MEMOCARD_TYPES: List[str] = ["true_false", "multiple_choice", "text", "numeric"]
    
    # Difficulty levels
    DIFFICULTY_LEVELS: List[str] = ["easy", "medium", "hard", "expert"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 