"""
Logging configuration for the AI Software Factory.

Sets up structured logging with JSON format support.
"""

import logging
import logging.config
from pathlib import Path
from pythonjsonlogger import jsonlogger
from datetime import datetime


def setup_logging(
    level: str = "INFO",
    log_file: str = "logs/factory.log",
    use_json: bool = False
) -> None:
    """
    Setup logging configuration.

    Args:
        level: Logging level
        log_file: Path to log file
        use_json: Whether to use JSON format
    """
    # Create logs directory
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    # Create logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level))
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, level))
    
    if use_json:
        file_formatter = jsonlogger.JsonFormatter()
    else:
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
