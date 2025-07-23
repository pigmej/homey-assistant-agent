"""
MCP (Model Context Protocol) server configuration loader.

This module handles loading and validation of MCP server configurations from JSON files,
creating appropriate MCP server instances, and providing proper error handling.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from livekit.agents import mcp

from .constants import DEFAULT_MCP_CONFIG_PATH

logger = logging.getLogger(__name__)


class MCPConfigurationError(Exception):
    """Raised when there's an error in MCP server configuration."""

    pass


class MCPConfigLoader:
    """
    Loads and validates MCP server configurations from JSON files.

    This class handles the loading of MCP server configurations, validates them,
    and creates appropriate MCP server instances (HTTP or stdio) based on the
    configuration type.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the MCP configuration loader.

        Args:
            config_path: Path to the MCP configuration JSON file.
                        Defaults to DEFAULT_MCP_CONFIG_PATH if not provided.
        """
        self.config_path = config_path or DEFAULT_MCP_CONFIG_PATH

    def load_servers(self) -> List[mcp.MCPServer]:
        """
        Load MCP server configurations and return list of MCP server instances.

        Returns:
            List of configured MCP server instances.

        Raises:
            MCPConfigurationError: If there's an error loading or parsing the configuration.
        """
        if not os.path.exists(self.config_path):
            logger.warning(
                f"MCP configuration file not found: {self.config_path}. "
                "Continuing with no MCP servers."
            )
            return []

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise MCPConfigurationError(
                f"Invalid JSON in MCP configuration file {self.config_path}: {e}"
            ) from e
        except IOError as e:
            raise MCPConfigurationError(
                f"Error reading MCP configuration file {self.config_path}: {e}"
            ) from e

        if not isinstance(config, dict):
            raise MCPConfigurationError(
                f"MCP configuration must be a JSON object, got {type(config).__name__}"
            )

        servers_config = config.get("servers", {})
        if not isinstance(servers_config, dict):
            raise MCPConfigurationError("MCP configuration 'servers' must be an object")

        servers = []
        for server_name, server_config in servers_config.items():
            try:
                server = self._create_server(server_name, server_config)
                if server:
                    servers.append(server)
            except Exception as e:
                logger.error(f"Failed to create MCP server '{server_name}': {e}")
                # Continue with other servers instead of failing completely
                continue

        logger.info(
            f"Successfully loaded {len(servers)} MCP servers from {self.config_path}"
        )
        return servers

    def _create_server(
        self, server_name: str, server_config: Dict[str, Any]
    ) -> Optional[mcp.MCPServer]:
        """
        Create an MCP server instance based on configuration.

        Args:
            server_name: Name of the server for logging purposes.
            server_config: Server configuration dictionary.

        Returns:
            MCP server instance or None if configuration is invalid.

        Raises:
            MCPConfigurationError: If server configuration is invalid.
        """
        if not isinstance(server_config, dict):
            raise MCPConfigurationError(
                f"Server '{server_name}' configuration must be an object"
            )

        server_type = server_config.get("type")
        if not server_type:
            raise MCPConfigurationError(
                f"Server '{server_name}' missing required 'type' field"
            )

        if server_type == "http":
            return self._create_http_server(server_name, server_config)
        elif server_type == "stdio":
            return self._create_stdio_server(server_name, server_config)
        else:
            raise MCPConfigurationError(
                f"Server '{server_name}' has unsupported type '{server_type}'. "
                "Supported types: 'http', 'stdio'"
            )

    def _create_http_server(
        self, server_name: str, server_config: Dict[str, Any]
    ) -> mcp.MCPServerHTTP:
        """
        Create an HTTP MCP server instance.

        Args:
            server_name: Name of the server for logging purposes.
            server_config: Server configuration dictionary.

        Returns:
            HTTP MCP server instance.

        Raises:
            MCPConfigurationError: If HTTP server configuration is invalid.
        """
        url = server_config.get("url")
        if not url:
            raise MCPConfigurationError(
                f"HTTP server '{server_name}' missing required 'url' field"
            )

        if not isinstance(url, str):
            raise MCPConfigurationError(
                f"HTTP server '{server_name}' 'url' must be a string"
            )

        logger.debug(f"Creating HTTP MCP server '{server_name}' with URL: {url}")
        return mcp.MCPServerHTTP(url)

    def _create_stdio_server(
        self, server_name: str, server_config: Dict[str, Any]
    ) -> mcp.MCPServerStdio:
        """
        Create a stdio MCP server instance.

        Args:
            server_name: Name of the server for logging purposes.
            server_config: Server configuration dictionary.

        Returns:
            Stdio MCP server instance.

        Raises:
            MCPConfigurationError: If stdio server configuration is invalid.
        """
        command = server_config.get("command")
        if not command:
            raise MCPConfigurationError(
                f"Stdio server '{server_name}' missing required 'command' field"
            )

        if not isinstance(command, str):
            raise MCPConfigurationError(
                f"Stdio server '{server_name}' 'command' must be a string"
            )

        args = server_config.get("args", [])
        if not isinstance(args, list):
            raise MCPConfigurationError(
                f"Stdio server '{server_name}' 'args' must be a list"
            )

        # Validate that all args are strings
        for i, arg in enumerate(args):
            if not isinstance(arg, str):
                raise MCPConfigurationError(
                    f"Stdio server '{server_name}' args[{i}] must be a string, got {type(arg).__name__}"
                )

        logger.debug(
            f"Creating stdio MCP server '{server_name}' with command: {command}, args: {args}"
        )
        return mcp.MCPServerStdio(command, args)
