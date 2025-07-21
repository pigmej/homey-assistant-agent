"""
Unit tests for MCP configuration loader.

Tests various scenarios including valid configurations, invalid configurations,
missing files, and error handling.
"""

import json
import os
import tempfile
import pytest
from unittest.mock import patch, mock_open

from homey_assistant.config.mcp_config import MCPConfigLoader, MCPConfigurationError
from homey_assistant.config.constants import DEFAULT_MCP_CONFIG_PATH


class TestMCPConfigLoader:
    """Test cases for MCPConfigLoader class."""
    
    def test_init_default_path(self):
        """Test initialization with default config path."""
        loader = MCPConfigLoader()
        assert loader.config_path == DEFAULT_MCP_CONFIG_PATH
    
    def test_init_custom_path(self):
        """Test initialization with custom config path."""
        custom_path = "/custom/path/mcp.json"
        loader = MCPConfigLoader(custom_path)
        assert loader.config_path == custom_path
    
    def test_load_servers_missing_file(self):
        """Test loading servers when config file doesn't exist."""
        loader = MCPConfigLoader("nonexistent.json")
        servers = loader.load_servers()
        assert servers == []
    
    def test_load_servers_valid_config(self, mcp_config_file, valid_mcp_config):
        """Test loading servers with valid configuration."""
        with patch('homey_assistant.config.mcp_config.mcp.MCPServerHTTP'), \
             patch('homey_assistant.config.mcp_config.mcp.MCPServerStdio'):
            loader = MCPConfigLoader(mcp_config_file)
            servers = loader.load_servers()
            assert len(servers) == 2
    
    def test_load_servers_invalid_json(self, temp_config_file):
        """Test loading servers with invalid JSON."""
        with open(temp_config_file, 'w') as f:
            f.write("invalid json content")
        
        loader = MCPConfigLoader(temp_config_file)
        with pytest.raises(MCPConfigurationError, match="Invalid JSON"):
            loader.load_servers()
    
    def test_load_servers_non_dict_config(self, temp_config_file):
        """Test loading servers when config is not a dictionary."""
        with open(temp_config_file, 'w') as f:
            json.dump(["not", "a", "dict"], f)
        
        loader = MCPConfigLoader(temp_config_file)
        with pytest.raises(MCPConfigurationError, match="must be a JSON object"):
            loader.load_servers()
    
    def test_load_servers_invalid_servers_config(self, temp_config_file):
        """Test loading servers when servers config is not a dictionary."""
        config = {"servers": "not a dict"}
        
        with open(temp_config_file, 'w') as f:
            json.dump(config, f)
        
        loader = MCPConfigLoader(temp_config_file)
        with pytest.raises(MCPConfigurationError, match="'servers' must be an object"):
            loader.load_servers()
    
    def test_load_servers_empty_config(self, temp_config_file):
        """Test loading servers with empty configuration."""
        config = {}
        
        with open(temp_config_file, 'w') as f:
            json.dump(config, f)
        
        loader = MCPConfigLoader(temp_config_file)
        servers = loader.load_servers()
        assert servers == []
    
    def test_create_http_server_valid(self):
        """Test creating HTTP server with valid configuration."""
        loader = MCPConfigLoader()
        server_config = {
            "type": "http",
            "url": "http://example.com/mcp"
        }
        
        with patch('homey_assistant.config.mcp_config.mcp.MCPServerHTTP') as mock_http:
            server = loader._create_http_server("test_server", server_config)
            mock_http.assert_called_once_with("http://example.com/mcp")
    
    def test_create_http_server_missing_url(self):
        """Test creating HTTP server without URL."""
        loader = MCPConfigLoader()
        server_config = {"type": "http"}
        
        with pytest.raises(MCPConfigurationError, match="missing required 'url' field"):
            loader._create_http_server("test_server", server_config)
    
    def test_create_http_server_invalid_url_type(self):
        """Test creating HTTP server with non-string URL."""
        loader = MCPConfigLoader()
        server_config = {
            "type": "http",
            "url": 123
        }
        
        with pytest.raises(MCPConfigurationError, match="'url' must be a string"):
            loader._create_http_server("test_server", server_config)
    
    def test_create_stdio_server_valid(self):
        """Test creating stdio server with valid configuration."""
        loader = MCPConfigLoader()
        server_config = {
            "type": "stdio",
            "command": "python",
            "args": ["-m", "server"]
        }
        
        with patch('homey_assistant.config.mcp_config.mcp.MCPServerStdio') as mock_stdio:
            server = loader._create_stdio_server("test_server", server_config)
            mock_stdio.assert_called_once_with("python", ["-m", "server"])
    
    def test_create_stdio_server_missing_command(self):
        """Test creating stdio server without command."""
        loader = MCPConfigLoader()
        server_config = {"type": "stdio"}
        
        with pytest.raises(MCPConfigurationError, match="missing required 'command' field"):
            loader._create_stdio_server("test_server", server_config)
    
    def test_create_stdio_server_invalid_command_type(self):
        """Test creating stdio server with non-string command."""
        loader = MCPConfigLoader()
        server_config = {
            "type": "stdio",
            "command": 123
        }
        
        with pytest.raises(MCPConfigurationError, match="'command' must be a string"):
            loader._create_stdio_server("test_server", server_config)
    
    def test_create_stdio_server_invalid_args_type(self):
        """Test creating stdio server with non-list args."""
        loader = MCPConfigLoader()
        server_config = {
            "type": "stdio",
            "command": "python",
            "args": "not a list"
        }
        
        with pytest.raises(MCPConfigurationError, match="'args' must be a list"):
            loader._create_stdio_server("test_server", server_config)
    
    def test_create_stdio_server_invalid_arg_type(self):
        """Test creating stdio server with non-string arg in args list."""
        loader = MCPConfigLoader()
        server_config = {
            "type": "stdio",
            "command": "python",
            "args": ["-m", 123]
        }
        
        with pytest.raises(MCPConfigurationError, match="args\\[1\\] must be a string"):
            loader._create_stdio_server("test_server", server_config)
    
    def test_create_stdio_server_no_args(self):
        """Test creating stdio server without args (should default to empty list)."""
        loader = MCPConfigLoader()
        server_config = {
            "type": "stdio",
            "command": "python"
        }
        
        with patch('homey_assistant.config.mcp_config.mcp.MCPServerStdio') as mock_stdio:
            server = loader._create_stdio_server("test_server", server_config)
            mock_stdio.assert_called_once_with("python", [])
    
    def test_create_server_invalid_type(self):
        """Test creating server with unsupported type."""
        loader = MCPConfigLoader()
        server_config = {"type": "unsupported"}
        
        with pytest.raises(MCPConfigurationError, match="unsupported type 'unsupported'"):
            loader._create_server("test_server", server_config)
    
    def test_create_server_missing_type(self):
        """Test creating server without type field."""
        loader = MCPConfigLoader()
        server_config = {}
        
        with pytest.raises(MCPConfigurationError, match="missing required 'type' field"):
            loader._create_server("test_server", server_config)
    
    def test_create_server_non_dict_config(self):
        """Test creating server with non-dictionary configuration."""
        loader = MCPConfigLoader()
        
        with pytest.raises(MCPConfigurationError, match="configuration must be an object"):
            loader._create_server("test_server", "not a dict")
    
    def test_load_servers_continues_on_server_error(self, temp_config_file):
        """Test that loading continues when individual server creation fails."""
        config = {
            "servers": {
                "valid_server": {
                    "type": "http",
                    "url": "http://example.com/mcp"
                },
                "invalid_server": {
                    "type": "invalid_type"
                },
                "another_valid_server": {
                    "type": "stdio",
                    "command": "python"
                }
            }
        }
        
        with open(temp_config_file, 'w') as f:
            json.dump(config, f)
        
        loader = MCPConfigLoader(temp_config_file)
        with patch('homey_assistant.config.mcp_config.mcp.MCPServerHTTP'), \
             patch('homey_assistant.config.mcp_config.mcp.MCPServerStdio'):
            servers = loader.load_servers()
            # Should load 2 valid servers, skip the invalid one
            assert len(servers) == 2
    
    def test_load_servers_with_fixture_files(self):
        """Test loading servers using fixture files."""
        # Test with valid fixture
        fixture_path = "tests/fixtures/valid_mcp_config.json"
        loader = MCPConfigLoader(fixture_path)
        with patch('homey_assistant.config.mcp_config.mcp.MCPServerHTTP'), \
             patch('homey_assistant.config.mcp_config.mcp.MCPServerStdio'):
            servers = loader.load_servers()
            assert len(servers) == 2
        
        # Test with invalid fixture
        fixture_path = "tests/fixtures/invalid_mcp_config.json"
        loader = MCPConfigLoader(fixture_path)
        with patch('homey_assistant.config.mcp_config.mcp.MCPServerHTTP'), \
             patch('homey_assistant.config.mcp_config.mcp.MCPServerStdio'):
            # Should only create valid servers and skip invalid ones
            servers = loader.load_servers()
            assert len(servers) == 0
    
    def test_load_servers_io_error(self):
        """Test handling of IO errors when loading servers."""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', side_effect=IOError("Permission denied")):
            loader = MCPConfigLoader("some_path.json")
            with pytest.raises(MCPConfigurationError, match="Error reading MCP configuration file"):
                loader.load_servers()
    
    def test_load_servers_with_environment_variable(self):
        """Test loading servers with path from environment variable."""
        with patch.dict('os.environ', {'MCP_CONFIG_PATH': 'custom_path.json'}), \
             patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='{"servers":{}}')):
            
            loader = MCPConfigLoader(os.environ.get('MCP_CONFIG_PATH'))
            servers = loader.load_servers()
            assert servers == []
            assert loader.config_path == 'custom_path.json'