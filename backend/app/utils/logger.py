"""
Structured logging for VeriClip AI.
Exports logs to Cloud Logging in production.
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str,
    level: str = "INFO",
    format_string: Optional[str] = None,
) -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Optional custom format

    Returns:
        Configured logger instance
    """
    if format_string is None:
        format_string = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Avoid adding duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(format_string))
        logger.addHandler(handler)

    return logger
