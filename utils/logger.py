"""
Logging configuration for Car Buyer Assist RAG Application.

This module provides centralized logging setup with support for both
file and console output, structured formatting, and configurable log levels.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from config.constants import PathConfig
from config.settings import settings


# Color codes for console output
class LogColors:
    """ANSI color codes for terminal output."""
    GREY = '\033[90m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD_RED = '\033[91m\033[1m'
    RESET = '\033[0m'


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels in console output."""
    
    LEVEL_COLORS = {
        logging.DEBUG: LogColors.GREY,
        logging.INFO: LogColors.BLUE,
        logging.WARNING: LogColors.YELLOW,
        logging.ERROR: LogColors.RED,
        logging.CRITICAL: LogColors.BOLD_RED,
    }
    
    def format(self, record):
        """Format log record with colors for console output."""
        # Save original levelname
        original_levelname = record.levelname
        
        # Add color to levelname
        if record.levelno in self.LEVEL_COLORS:
            color = self.LEVEL_COLORS[record.levelno]
            record.levelname = f"{color}{record.levelname}{LogColors.RESET}"
        
        # Format the record
        result = super().format(record)
        
        # Restore original levelname
        record.levelname = original_levelname
        
        return result


def setup_logging(
    log_level: Optional[str] = None,
    log_to_file: bool = True,
    log_to_console: bool = True
) -> None:
    """
    Configure application-wide logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                  If None, uses value from settings.
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
    """
    # Determine log level
    level_name = log_level or settings.log_level
    level = getattr(logging, level_name.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    if log_to_file:
        PathConfig.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Format strings
    file_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Add file handler
    if log_to_file:
        file_handler = logging.FileHandler(PathConfig.LOG_FILE, encoding='utf-8')
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(file_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Add console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = ColoredFormatter(console_format, datefmt=date_format)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # Suppress verbose logging from third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)
    logging.getLogger('chromadb').setLevel(logging.WARNING)
    logging.getLogger('langchain').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the specified module.
    
    Args:
        name: Name of the module (typically __name__)
        
    Returns:
        Logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started")
    """
    return logging.getLogger(name)


# Initialize logging on module import
setup_logging()
