import os

if not os.path.exists("LogFiles"):
    os.makedirs("LogFiles")
    
LOG_FILE = "LogFiles/emailsvc.log"

# debug levels
DEBUG_LEVEL = os.getenv("DEBUG_LEVEL", "INFO")

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
            "level": DEBUG_LEVEL,
            "class": "logging.FileHandler",
            "formatter": "advanced",
            "filename": LOG_FILE,
        }
    },
    "loggers": {
        "app": {
            "handlers": ["file"],
            "level": DEBUG_LEVEL,
            "propagate": False,
        }
    },
}

# dictConfig(logging_config)
