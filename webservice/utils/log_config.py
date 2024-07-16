import os
import logging
from logging.config import dictConfig

if not os.path.exists("LogFiles"):
    os.makedirs("LogFiles")
    
APP_LOG_FILE = "LogFiles/app.log"
SQLALCHEMY_LOG_FILE = "LogFiles/sqlalchemy.log"
UVICORN_LOG_FILE = "LogFiles/uvicorn.log"

# debug levels
UVICORN_DEBUG_LEVEL = os.getenv("UVICORN_DEBUG_LEVEL", "INFO")
SQLALCHEMY_DEBUG_LEVEL = os.getenv("SQLALCHEMY_DEBUG_LEVEL", "INFO")
APP_DEBUG_LEVEL = os.getenv("APP_DEBUG_LEVEL", "DEBUG")
print(f"UVICORN_DEBUG_LEVEL set to => {UVICORN_DEBUG_LEVEL}")
print(f"SQLALCHEMY_DEBUG_LEVEL set to => {SQLALCHEMY_DEBUG_LEVEL}")
print(f"APP_DEBUG_LEVEL set to => {APP_DEBUG_LEVEL}")

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]",
        },
        "advanced": {
            'format': "[%(asctime)s] %(levelname)s %(filename)s:%(lineno)d %(funcName)20s - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "detailed",
        },
        "file": {
            "level": APP_DEBUG_LEVEL,
            "class": "logging.FileHandler",
            "formatter": "advanced",
            "filename": APP_LOG_FILE,
        },
        "uvicorn": {
            "level": UVICORN_DEBUG_LEVEL,
            "class": "logging.FileHandler",
            "formatter": "advanced",
            "filename": UVICORN_LOG_FILE,
        },
        "sqlalchemy": {
            "level": SQLALCHEMY_DEBUG_LEVEL,
            "class": "logging.FileHandler",
            "formatter": "advanced",
            "filename": SQLALCHEMY_LOG_FILE,
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["uvicorn"],
            "level": UVICORN_DEBUG_LEVEL,
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["uvicorn"],
            "level": UVICORN_DEBUG_LEVEL,
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["uvicorn"],
            "level": UVICORN_DEBUG_LEVEL,
            "propagate": False,
        },
        "app": {
            "handlers": ["file"],
            "level": APP_DEBUG_LEVEL,
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "handlers": ["sqlalchemy"],
            "level": SQLALCHEMY_DEBUG_LEVEL,
            "propagate": False,
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"],
    },
}

try:
    dictConfig(logging_config)
except Exception as e:
    print(f"Error configuring logger: {e}")  # This should print in case of an exception

# Additional print statements for testing
logging.debug("Logger is successfully configured!")  # Should log
