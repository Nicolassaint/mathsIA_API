import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from jose import JWTError
from pymongo.errors import DuplicateKeyError, OperationFailure
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging_config import logger
from app.middleware.error_handler import (
    AppException, 
    app_exception_handler, 
    jwt_exception_handler,
    mongo_duplicate_key_handler,
    mongo_operation_failure_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.middleware.logging import LoggingMiddleware
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.db.init_db import init_db

# Import routers
from app.api.routes.auth import router as auth_router
from app.api.routes.admin.students import router as admin_students_router
from app.api.routes.admin.memocards import router as admin_memocards_router
from app.api.routes.student.profile import router as student_profile_router
from app.api.routes.student.memocards import router as student_memocards_router
from app.api.routes.student.progress import router as student_progress_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    await connect_to_mongo()
    await init_db()
    logger.info("Startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await close_mongo_connection()
    logger.info("Shutdown complete")

# Create the FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="RESTful API for MathsIA, a memocard system for math learning.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(JWTError, jwt_exception_handler)
app.add_exception_handler(DuplicateKeyError, mongo_duplicate_key_handler)
app.add_exception_handler(OperationFailure, mongo_operation_failure_handler)
app.add_exception_handler(ValueError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint
    """
    return {"message": "Welcome to MathsIA API", "version": "0.1.0"}

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health():
    """
    Health check endpoint
    """
    return {"status": "ok"}

# Include routers
api_prefix = settings.API_V1_PREFIX

# Auth routes
app.include_router(auth_router, prefix=api_prefix)

# Admin routes
app.include_router(admin_students_router, prefix=f"{api_prefix}/admin")
app.include_router(admin_memocards_router, prefix=f"{api_prefix}/admin")

# Student routes
app.include_router(student_profile_router, prefix=f"{api_prefix}/student")
app.include_router(student_memocards_router, prefix=f"{api_prefix}/student")
app.include_router(student_progress_router, prefix=f"{api_prefix}/student")

# Custom OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version="0.1.0",
        description="RESTful API for MathsIA, a memocard system for math learning.",
        routes=app.routes,
    )
    
    # Organize tags
    openapi_schema["tags"] = [
        {"name": "Authentication", "description": "Authentication operations"},
        {"name": "Admin - Students", "description": "Admin operations related to students"},
        {"name": "Admin - Memocards", "description": "Admin operations related to memocards"},
        {"name": "Student - Profile", "description": "Student profile operations"},
        {"name": "Student - Memocards", "description": "Student memocard operations"},
        {"name": "Student - Progress", "description": "Student progress operations"},
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Run the application
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 