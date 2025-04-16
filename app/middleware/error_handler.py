from fastapi import Request, status
from fastapi.responses import JSONResponse
from jose import JWTError
from fastapi.encoders import jsonable_encoder
from app.core.logging_config import logger
from pymongo.errors import DuplicateKeyError, OperationFailure

class AppException(Exception):
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
    ):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code


async def app_exception_handler(request: Request, exc: AppException):
    """
    Handle application-specific exceptions
    """
    logger.error(f"AppException: {exc.detail}", extra={"path": request.url.path, "error_code": exc.error_code})
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({
            "error": {
                "code": exc.error_code or "app_error",
                "message": exc.detail,
                "status": exc.status_code
            }
        }),
    )


async def jwt_exception_handler(request: Request, exc: JWTError):
    """
    Handle JWT exceptions
    """
    logger.error(f"JWTError: {str(exc)}", extra={"path": request.url.path})
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=jsonable_encoder({
            "error": {
                "code": "invalid_token",
                "message": "Could not validate credentials",
                "status": status.HTTP_401_UNAUTHORIZED
            }
        }),
    )


async def mongo_duplicate_key_handler(request: Request, exc: DuplicateKeyError):
    """
    Handle MongoDB duplicate key errors
    """
    logger.error(f"DuplicateKeyError: {str(exc)}", extra={"path": request.url.path})
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=jsonable_encoder({
            "error": {
                "code": "duplicate_key",
                "message": "An item with these details already exists",
                "status": status.HTTP_409_CONFLICT
            }
        }),
    )


async def mongo_operation_failure_handler(request: Request, exc: OperationFailure):
    """
    Handle MongoDB operation failures
    """
    logger.error(f"OperationFailure: {str(exc)}", extra={"path": request.url.path})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({
            "error": {
                "code": "database_error",
                "message": "Database operation failed",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR
            }
        }),
    )


async def validation_exception_handler(request: Request, exc: Exception):
    """
    Handle validation exceptions
    """
    logger.error(f"ValidationError: {str(exc)}", extra={"path": request.url.path})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "error": {
                "code": "validation_error",
                "message": str(exc),
                "status": status.HTTP_422_UNPROCESSABLE_ENTITY
            }
        }),
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions
    """
    logger.error(f"Unhandled Exception: {str(exc)}", extra={"path": request.url.path})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({
            "error": {
                "code": "server_error",
                "message": "An unexpected error occurred",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR
            }
        }),
    ) 