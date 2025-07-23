"""
Tests for logging utilities.

This module contains unit tests for the logging configuration
and utility functions in the homey_assistant.utils.logging module.
"""

import logging
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from homey_assistant.utils.logging import (
    configure_logging,
    get_logger,
    set_correlation_id,
    get_correlation_id,
    generate_correlation_id,
    log_with_context,
    log_error_with_context,
    log_performance,
    CorrelationFilter,
    StructuredFormatter,
)


class TestLoggingUtilities(unittest.TestCase):
    """Test cases for logging utilities."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear any existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.NOTSET)

    def tearDown(self):
        """Clean up after tests."""
        # Reset logging configuration
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.WARNING)

    def test_correlation_id_generation(self):
        """Test correlation ID generation and management."""
        # Test generation
        corr_id = generate_correlation_id()
        self.assertIsInstance(corr_id, str)
        self.assertEqual(len(corr_id), 8)

        # Test setting and getting
        set_correlation_id(corr_id)
        self.assertEqual(get_correlation_id(), corr_id)

        # Test auto-generation
        new_corr_id = set_correlation_id()
        self.assertIsInstance(new_corr_id, str)
        self.assertEqual(len(new_corr_id), 8)
        self.assertEqual(get_correlation_id(), new_corr_id)

    def test_correlation_filter(self):
        """Test correlation filter functionality."""
        # Set up correlation ID
        test_corr_id = "test123"
        set_correlation_id(test_corr_id)

        # Create filter and test record
        filter_obj = CorrelationFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )

        # Apply filter
        result = filter_obj.filter(record)

        # Verify filter result and correlation ID addition
        self.assertTrue(result)
        self.assertEqual(record.correlation_id, test_corr_id)

    def test_structured_formatter(self):
        """Test structured formatter functionality."""
        # Test with correlation ID
        formatter = StructuredFormatter(include_correlation=True)
        record = logging.LogRecord(
            name="test.module",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )
        record.correlation_id = "test123"

        formatted = formatter.format(record)
        self.assertIn("[INFO]", formatted)
        self.assertIn("[test123]", formatted)
        self.assertIn("test.module", formatted)
        self.assertIn("test message", formatted)

        # Test without correlation ID
        formatter_no_corr = StructuredFormatter(include_correlation=False)
        formatted_no_corr = formatter_no_corr.format(record)
        self.assertIn("[INFO]", formatted_no_corr)
        self.assertNotIn("[test123]", formatted_no_corr)
        self.assertIn("test.module", formatted_no_corr)
        self.assertIn("test message", formatted_no_corr)

    def test_configure_logging_console_only(self):
        """Test logging configuration with console output only."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            configure_logging(level=logging.DEBUG, enable_correlation=True)

            # Test logging
            logger = get_logger("test.module")
            set_correlation_id("test456")
            logger.info("Test message")

            # Verify root logger configuration
            root_logger = logging.getLogger()
            self.assertEqual(root_logger.level, logging.DEBUG)
            self.assertTrue(len(root_logger.handlers) >= 1)

    def test_configure_logging_with_file(self):
        """Test logging configuration with file output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            configure_logging(
                level=logging.INFO, log_file=str(log_file), enable_correlation=True
            )

            # Test logging
            logger = get_logger("test.module")
            set_correlation_id("file789")
            logger.info("File test message")

            # Verify file was created and contains log
            self.assertTrue(log_file.exists())

            with open(log_file, "r") as f:
                content = f.read()
                self.assertIn("File test message", content)
                self.assertIn("[file789]", content)

    def test_get_logger(self):
        """Test logger retrieval."""
        logger = get_logger("test.component")
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test.component")

    def test_log_with_context(self):
        """Test logging with context information."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            configure_logging(level=logging.DEBUG)
            logger = get_logger("test.context")

            log_with_context(
                logger,
                logging.INFO,
                "Operation completed",
                user_id="123",
                operation="test_op",
                duration=1.5,
            )

            # Note: We can't easily capture the exact output due to logging complexity,
            # but we can verify the function doesn't raise exceptions

    def test_log_error_with_context(self):
        """Test error logging with context."""
        with patch("sys.stdout", new_callable=StringIO):
            configure_logging(level=logging.DEBUG)
            logger = get_logger("test.error")

            try:
                raise ValueError("Test error")
            except ValueError as e:
                log_error_with_context(
                    logger,
                    "Operation failed",
                    e,
                    operation="test_operation",
                    user_id="456",
                )

            # Verify function completes without exceptions

    def test_log_performance(self):
        """Test performance logging."""
        with patch("sys.stdout", new_callable=StringIO):
            configure_logging(level=logging.DEBUG)
            logger = get_logger("test.performance")

            log_performance(
                logger, "database_query", 123.45, query_type="SELECT", table="users"
            )

            # Verify function completes without exceptions


if __name__ == "__main__":
    unittest.main()
