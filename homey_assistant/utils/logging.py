"""
Logging Utilities

This module provides centralized logging configuration and utilities
for the Homey Assistant application, including structured logging,
correlation ID support, and proper log formatting.
"""

import logging
import logging.config
import sys
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional, Union
from pathlib import Path


# Context variable for correlation ID tracking
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class CorrelationFilter(logging.Filter):
    """
    Logging filter that adds correlation ID to log records.
    
    This filter automatically adds the current correlation ID to all log records,
    enabling request tracing across the application.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation ID to the log record."""
        record.correlation_id = correlation_id.get() or 'N/A'
        return True


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter for structured logging.
    
    Provides consistent formatting with correlation IDs and context information.
    """
    
    def __init__(self, include_correlation: bool = True):
        """
        Initialize the structured formatter.
        
        Args:
            include_correlation: Whether to include correlation ID in the format
        """
        self.include_correlation = include_correlation
        
        if include_correlation:
            fmt = "%(asctime)s [%(levelname)s] [%(correlation_id)s] %(name)s: %(message)s"
        else:
            fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            
        super().__init__(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")


def generate_correlation_id() -> str:
    """
    Generate a new correlation ID.
    
    Returns:
        A unique correlation ID string
    """
    return str(uuid.uuid4())[:8]


def set_correlation_id(corr_id: Optional[str] = None) -> str:
    """
    Set the correlation ID for the current context.
    
    Args:
        corr_id: Optional correlation ID. If None, a new one is generated.
        
    Returns:
        The correlation ID that was set
    """
    if corr_id is None:
        corr_id = generate_correlation_id()
    
    correlation_id.set(corr_id)
    return corr_id


def get_correlation_id() -> Optional[str]:
    """
    Get the current correlation ID.
    
    Returns:
        The current correlation ID or None if not set
    """
    return correlation_id.get()


def configure_logging(
    level: Union[str, int] = logging.INFO,
    log_file: Optional[str] = None,
    enable_correlation: bool = True,
    separate_agent_logs: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Configure application logging with structured format and correlation IDs.
    
    Args:
        level: Logging level (e.g., logging.INFO, "DEBUG")
        log_file: Optional path to log file. If None, only console logging is used.
        enable_correlation: Whether to enable correlation ID tracking
        separate_agent_logs: Whether to separate agent conversation logs
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
    """
    # Convert string level to logging constant if needed
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Create formatters
    console_formatter = StructuredFormatter(include_correlation=enable_correlation)
    file_formatter = StructuredFormatter(include_correlation=enable_correlation)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    
    if enable_correlation:
        console_handler.addFilter(CorrelationFilter())
    
    # Add console handler to root logger
    root_logger.addHandler(console_handler)
    root_logger.setLevel(level)
    
    # Create file handler if log file is specified
    if log_file:
        from logging.handlers import RotatingFileHandler
        
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(file_formatter)
        
        if enable_correlation:
            file_handler.addFilter(CorrelationFilter())
        
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers for better control
    _configure_specific_loggers(level, separate_agent_logs)
    
    # Log the configuration
    logger = logging.getLogger(__name__)
    logger.info("Logging configuration completed")
    logger.debug(f"Log level set to: {logging.getLevelName(level)}")
    if log_file:
        logger.debug(f"File logging enabled: {log_file}")
    if enable_correlation:
        logger.debug("Correlation ID tracking enabled")


def _configure_specific_loggers(level: int, separate_agent_logs: bool) -> None:
    """
    Configure specific loggers for different components.
    
    Args:
        level: Base logging level
        separate_agent_logs: Whether to separate agent conversation logs
    """
    # Configure LiveKit agents logger
    livekit_logger = logging.getLogger("livekit.agents")
    livekit_logger.setLevel(max(level, logging.INFO))  # Don't go below INFO for LiveKit
    
    # Configure MCP logger
    mcp_logger = logging.getLogger("mcp")
    mcp_logger.setLevel(level)
    
    # Configure application loggers
    app_loggers = [
        "homey_assistant",
        "homey_assistant.config",
        "homey_assistant.agent",
        "homey_assistant.utils"
    ]
    
    for logger_name in app_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
    
    # If separating agent logs, configure a separate handler for conversation logs
    if separate_agent_logs:
        _configure_agent_conversation_logger()


def _configure_agent_conversation_logger() -> None:
    """Configure separate logger for agent conversations."""
    conversation_logger = logging.getLogger("homey_assistant.agent.conversation")
    
    # Create a simple formatter for conversation logs
    conversation_formatter = logging.Formatter(
        "%(asctime)s [CONVERSATION] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Create separate handler for conversation logs
    conversation_handler = logging.StreamHandler(sys.stdout)
    conversation_handler.setFormatter(conversation_formatter)
    conversation_handler.setLevel(logging.INFO)
    
    # Add handler only to conversation logger (don't propagate to root)
    conversation_logger.addHandler(conversation_handler)
    conversation_logger.propagate = False
    conversation_logger.setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    This is a convenience function that ensures consistent logger naming
    and configuration across the application.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    **context: Any
) -> None:
    """
    Log a message with additional context information.
    
    Args:
        logger: Logger instance to use
        level: Logging level
        message: Log message
        **context: Additional context key-value pairs
    """
    if context:
        context_str = " | ".join(f"{k}={v}" for k, v in context.items())
        full_message = f"{message} | {context_str}"
    else:
        full_message = message
    
    logger.log(level, full_message)


# Convenience functions for common logging patterns
def log_error_with_context(
    logger: logging.Logger,
    message: str,
    error: Exception,
    **context: Any
) -> None:
    """
    Log an error with exception details and context.
    
    Args:
        logger: Logger instance to use
        message: Error message
        error: Exception that occurred
        **context: Additional context information
    """
    context['error_type'] = type(error).__name__
    context['error_message'] = str(error)
    
    log_with_context(logger, logging.ERROR, message, **context)


def log_performance(
    logger: logging.Logger,
    operation: str,
    duration_ms: float,
    **context: Any
) -> None:
    """
    Log performance information for an operation.
    
    Args:
        logger: Logger instance to use
        operation: Name of the operation
        duration_ms: Duration in milliseconds
        **context: Additional context information
    """
    context['duration_ms'] = round(duration_ms, 2)
    
    log_with_context(
        logger,
        logging.INFO,
        f"Performance: {operation} completed",
        **context
    )


def setup_logging(
    level: Union[str, int] = logging.INFO,
    log_file: Optional[str] = None,
    enable_correlation: bool = True
) -> None:
    """
    Set up application logging with default configuration.
    
    This is a convenience function that configures logging with sensible
    defaults for the Homey Assistant application.
    
    Args:
        level: Logging level (default: INFO)
        log_file: Optional path to log file
        enable_correlation: Whether to enable correlation ID tracking
    """
    configure_logging(
        level=level,
        log_file=log_file,
        enable_correlation=enable_correlation,
        separate_agent_logs=True
    )