import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging_config import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging requests and responses
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate a unique request ID
        request_id = str(time.time())
        
        # Get client information
        client_host = request.client.host if request.client else "unknown"
        
        # Log request information
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "client_ip": client_host,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "headers": dict(request.headers),
            }
        )
        
        # Process the request and get the response
        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response information
            logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "processing_time": process_time,
                }
            )
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            
            # Log error information
            logger.error(
                f"Request failed: {request.method} {request.url.path} - {str(e)}",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "processing_time": process_time,
                }
            )
            
            raise 