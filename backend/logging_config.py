import logging
import os
from logging.config import dictConfig

from dotenv import load_dotenv

load_dotenv()


def setup_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": log_level,
                },
            },
            "root": {
                "handlers": ["console"],
                "level": log_level,
            },
            "loggers": {
                # Uvicorn logging
                "uvicorn": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": False,
                },
                # Your internal app modules
                "agents": {
                    "handlers": ["console"],
                    "level": log_level,
                    "propagate": False,
                },
                "agents.agent_loader": {
                    "handlers": ["console"],
                    "level": log_level,
                    "propagate": False,
                },
                "agents.graph_builder": {
                    "handlers": ["console"],
                    "level": log_level,
                    "propagate": False,
                },
                "agents.routes": {
                    "handlers": ["console"],
                    "level": log_level,
                    "propagate": False,
                },
                "agents.tools": {
                    "handlers": ["console"],
                    "level": log_level,
                    "propagate": False,
                },
                # Noisy third-party libraries
                "llama_index": {
                    "handlers": ["console"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "httpx": {
                    "handlers": ["console"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "httpcore": {
                    "handlers": ["console"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "fsspec": {
                    "handlers": ["console"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "openai": {
                    "handlers": ["console"],
                    "level": "WARNING",
                    "propagate": False,
                },
            },
        }
    )

    restrict_third_party_loggers()


def restrict_third_party_loggers():
    """
    Ensures any other 3rd party loggers not explicitly named are also restricted to WARNING.
    """
    for name in logging.root.manager.loggerDict:
        if name.startswith(("llama_index", "httpx", "fsspec", "openai")):
            logging.getLogger(name).setLevel(logging.WARNING)
