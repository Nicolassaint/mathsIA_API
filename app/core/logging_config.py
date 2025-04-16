import sys
import json
import logging
from pydantic import BaseModel
from typing import Dict, Any, Optional
import time
from app.core.config import settings

# Assurer que uvicorn est importé
try:
    import uvicorn.logging
except ImportError:
    # Fallback si uvicorn n'est pas disponible
    class DefaultFormatter(logging.Formatter):
        pass
    
    uvicorn = type('', (), {})
    uvicorn.logging = type('', (), {})
    uvicorn.logging.DefaultFormatter = DefaultFormatter

class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the log record.
    """
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the record as JSON.
        """
        log_data = {
            "timestamp": int(time.time()),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if it exists
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }
        
        # Add extra fields if they exist
        if hasattr(record, "extra"):
            log_data.update(record.extra)
            
        return json.dumps(log_data)

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    logger_name = "mathsia_api"
    log_format = "%(levelprefix)s | %(asctime)s | %(message)s"
    log_level = settings.LOG_LEVEL
    
    # Créer le logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    logger.handlers = []  # Supprimer les handlers existants
    
    # Créer le handler
    handler = logging.StreamHandler(sys.stderr)
    
    # Configurer le formateur selon l'environnement
    if settings.ENVIRONMENT == "development":
        formatter = uvicorn.logging.DefaultFormatter(
            fmt=log_format,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        formatter = JsonFormatter("%(levelprefix)s %(message)s")
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

logger = setup_logging() 