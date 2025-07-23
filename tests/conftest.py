"""
Pytest configuration and fixtures for Homey Assistant tests.

This module provides common fixtures and configuration for unit and integration tests.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator, List

import pytest
from unittest.mock import Mock, patch

from homey_assistant.config.mcp_config import MCPConfigLoader
from homey_assistant.agent.assistant import HomeyAssistant
from homey_assistant.agent.session import SessionManager
from homey_assistant.utils.logging import configure_logging, set_correlation_id


@pytest.fixture(scope="function")
def temp_dir() -> Generator[Path, None, None]:
    """
    Create a temporary directory for test files.

    Returns:
        Path to a temporary directory that will be cleaned up after the test.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture(scope="function")
def temp_config_file(temp_dir: Path) -> Generator[Path, None, None]:
    """
    Create a temporary MCP configuration file.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path to a temporary configuration file.
    """
    config_path = temp_dir / "mcp.json"
    yield config_path


@pytest.fixture(scope="function")
def valid_mcp_config() -> Dict[str, Any]:
    """
    Return a valid MCP server configuration.

    Returns:
        Dictionary containing a valid MCP configuration.
    """
    return {
        "servers": {
            "http_server": {"type": "http", "url": "http://example.com/mcp"},
            "stdio_server": {
                "type": "stdio",
                "command": "python",
                "args": ["-m", "server"],
            },
        }
    }


@pytest.fixture(scope="function")
def invalid_mcp_config() -> Dict[str, Any]:
    """
    Return an invalid MCP server configuration.

    Returns:
        Dictionary containing an invalid MCP configuration.
    """
    return {
        "servers": {
            "invalid_server": {"type": "unsupported"},
            "missing_url": {"type": "http"},
        }
    }


@pytest.fixture(scope="function")
def mcp_config_file(temp_config_file: Path, valid_mcp_config: Dict[str, Any]) -> Path:
    """
    Create a temporary MCP configuration file with valid content.

    Args:
        temp_config_file: Path to temporary config file
        valid_mcp_config: Valid MCP configuration dictionary

    Returns:
        Path to the configuration file.
    """
    with open(temp_config_file, "w") as f:
        json.dump(valid_mcp_config, f)
    return temp_config_file


@pytest.fixture(scope="function")
def invalid_mcp_config_file(
    temp_config_file: Path, invalid_mcp_config: Dict[str, Any]
) -> Path:
    """
    Create a temporary MCP configuration file with invalid content.

    Args:
        temp_config_file: Path to temporary config file
        invalid_mcp_config: Invalid MCP configuration dictionary

    Returns:
        Path to the configuration file.
    """
    with open(temp_config_file, "w") as f:
        json.dump(invalid_mcp_config, f)
    return temp_config_file


@pytest.fixture(scope="function")
def mock_mcp_servers() -> List[Mock]:
    """
    Create mock MCP server instances.

    Returns:
        List of mock MCP server objects.
    """
    return [Mock(), Mock()]


@pytest.fixture(scope="function")
def mock_vad() -> Mock:
    """
    Create a mock Voice Activity Detection (VAD) instance.

    Returns:
        Mock VAD object.
    """
    return Mock()


@pytest.fixture(scope="function")
def mock_room() -> Mock:
    """
    Create a mock LiveKit room instance.

    Returns:
        Mock Room object.
    """
    return Mock()


@pytest.fixture(scope="function")
def mock_job_context() -> Mock:
    """
    Create a mock JobContext instance.

    Returns:
        Mock JobContext object with proc attribute.
    """
    mock_context = Mock()
    mock_context.proc = Mock()
    mock_context.proc.userdata = {}
    return mock_context


@pytest.fixture(scope="function")
def mock_job_process() -> Mock:
    """
    Create a mock JobProcess instance.

    Returns:
        Mock JobProcess object with userdata attribute.
    """
    mock_process = Mock()
    mock_process.userdata = {}
    return mock_process


@pytest.fixture(scope="function")
def configured_logging():
    """
    Configure logging for tests.

    Sets up logging with a test correlation ID and returns to default
    configuration after the test.
    """
    # Configure logging for tests
    configure_logging(level="DEBUG")
    set_correlation_id("test-correlation-id")

    yield

    # Reset logging after test
    root_logger = pytest.importorskip("logging").getLogger()
    root_logger.handlers.clear()


@pytest.fixture(scope="function")
def homey_assistant() -> HomeyAssistant:
    """
    Create a HomeyAssistant instance for testing.

    Returns:
        Initialized HomeyAssistant object.
    """
    return HomeyAssistant()


@pytest.fixture(scope="function")
def session_manager() -> SessionManager:
    """
    Create a SessionManager instance for testing.

    Returns:
        Initialized SessionManager object.
    """
    return SessionManager()


@pytest.fixture(scope="function")
def mcp_config_loader() -> MCPConfigLoader:
    """
    Create an MCPConfigLoader instance for testing.

    Returns:
        Initialized MCPConfigLoader object.
    """
    return MCPConfigLoader()
