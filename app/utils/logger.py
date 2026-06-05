"""
Logger utility for WidgetWall application
"""

import sys
import os
import logging
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional


class Logger:
    """Custom logger for WidgetWall application."""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if Logger._logger is None:
            Logger._logger = self._setup_logger()
    
    def _setup_logger(
        self,
        log_file: Optional[Path] = None,
        level: str = "INFO",
        max_bytes: int = 1024 * 1024,
        backup_count: int = 3
    ) -> logging.Logger:
        """Setup the logger with file and console handlers."""
        
        logger = logging.getLogger("WidgetWall")
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        logger.handlers.clear()
        
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)
        
        # File handler
        if log_file is None:
            log_file = Path(__file__).parent.parent.parent / "widgetwall.log"
        
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            logger.addHandler(file_handler)
        except ImportError:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            logger.addHandler(file_handler)
        
        return logger
    
    def debug(self, message: str, exc_info: bool = False):
        Logger._logger.debug(message, exc_info=exc_info)
    
    def info(self, message: str, exc_info: bool = False):
        Logger._logger.info(message, exc_info=exc_info)
    
    def warning(self, message: str, exc_info: bool = False):
        Logger._logger.warning(message, exc_info=exc_info)
    
    def error(self, message: str, exc_info: bool = True):
        Logger._logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = True):
        Logger._logger.critical(message, exc_info=exc_info)
    
    def log_exception(self, message: str = "Unexpected error"):
        self.error(message, exc_info=True)
    
    def section(self, title: str, char: str = "=", length: int = 60):
        self.info(char * length)
        self.info(f"  {title}")
        self.info(char * length)


# Module-level logger instance
logger = Logger()


def setup_logger(
    log_file: Optional[Path] = None,
    level: str = "INFO"
) -> Logger:
    """Setup and return the logger instance."""
    global logger
    logger = Logger()
    logger._setup_logger(log_file, level)
    return logger


def get_logger() -> Logger:
    """Get the logger instance."""
    if logger is None:
        return Logger()
    return logger


