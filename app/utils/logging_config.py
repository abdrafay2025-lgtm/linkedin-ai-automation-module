"""
Structured Logging Configuration.
Standardizes log formats across all services and validators.
"""

import logging
import sys
from app.config.settings import settings


def setup_logger(module_name: str) -> logging.Logger:
    """
    Configures and returns a standardized logger instance.

    Args:
        module_name (str): Identifier of the calling module (typically __name__).

    Returns:
        logging.Logger: Pre-configured logger instance.
    """
    logger = logging.getLogger(module_name)
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Avoid duplicate handlers if already initialized
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False
    return logger