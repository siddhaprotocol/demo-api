"""
Logging configuration for the application.
"""

import logging
import sys
from typing import Dict, Optional


class LoggerFactory:
    """Factory for creating and configuring loggers."""

    _loggers: Dict[str, logging.Logger] = {}
    _initialized = False

    @classmethod
    def initialize(cls, level: int = logging.INFO) -> None:
        """Initialize the logging system."""
        if cls._initialized:
            return

        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        if not root_logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            root_logger.addHandler(handler)

        cls._initialized = True

    @classmethod
    def get_logger(cls, name: Optional[str] = None) -> logging.Logger:
        """
        Get or create a logger with the given name.

        Args:
            name: Logger name, typically the module name

        Returns:
            Configured logger instance
        """
        if not cls._initialized:
            cls.initialize()

        if name is None:
            return logging.getLogger()

        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)

        return cls._loggers[name]


LoggerFactory.initialize()

get_logger = LoggerFactory.get_logger
