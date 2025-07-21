"""
Utilities Module

This module contains utility functions and classes used throughout
the Homey Assistant application, including logging configuration
and helper functions.
"""

from .logging import (
    configure_logging,
    get_logger,
    set_correlation_id,
    get_correlation_id,
    generate_correlation_id,
    log_with_context,
    log_error_with_context,
    log_performance,
    CorrelationFilter,
    StructuredFormatter
)

__all__ = [
    "configure_logging",
    "get_logger", 
    "set_correlation_id",
    "get_correlation_id",
    "generate_correlation_id",
    "log_with_context",
    "log_error_with_context",
    "log_performance",
    "CorrelationFilter",
    "StructuredFormatter"
]