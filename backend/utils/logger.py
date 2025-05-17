import logging
import os

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    return logger
