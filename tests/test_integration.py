"""
Integration tests for Homey Assistant Agent.

This module contains integration tests that verify the interaction between
different components of the Homey Assistant Agent.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import tempfile
import json

from homey_assistant.config.mcp_config import MCPConfigLoader
from homey_assistant.agent.assistant import HomeyAssistant
from homey_assistant.agent.session import SessionManager
from homey_assistant.config.constants import DEFAULT_GREETING_INSTRUCTIONS


class TestAgentIntegration:
    """Integration tests for agent components."""
    
    @patch('homey_assistant.agent.session.AgentSession')
    @patch('homey_assistant.agent.session.google.STT')
    @patch('homey_assistant.agent.session.google.TTS')
    @patch('homey_assistant.agent.session.google.LLM')
    @patch('homey_assistant.agent.session.noise_cancellation.BVC')
    def test_complete_agent_initialization_flow(
        self, mock_bvc, mock_llm_class, mock_tts_class, mock_stt_class, mock_session_class
    ):
        """Test the complete agent initialization flow."""
        # Setup mocks
        mock_stt = Mock()
        mock_tts = Mock()
        mock_llm = Mock()
        mock_session = Mock()
        mock_bvc_instance = Mock()
        mock_room = Mock()
        mock_room_input_options = Mock()
        
        mock_stt_class.return_value = mock_stt
        mock_tts_class.return_value = mock_tts
        mock_llm_class.return_value = mock_llm
        mock_session_class.return_value = mock_session
        mock_bvc.return_value = mock_bvc_instance
        
        # Create temporary MCP config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "servers": {
                    "test_server": {
                        "type": "http",
                        "url": "http://example.com/mcp"
                    }
                }
            }, f)
            config_path = f.name
        
        try:
            # Load MCP servers
            with patch('homey_assistant.config.mcp_config.mcp.MCPServerHTTP') as mock_http:
                mock_mcp_server = Mock()
                mock_http.return_value = mock_mcp_server
                
                config_loader = MCPConfigLoader(config_path)
                mcp_servers = config_loader.load_servers()
                
                # Create session manager and session
                session_manager = SessionManager()
                session = session_manager.create_session(mcp_servers)
                
                # Create assistant
                assistant = HomeyAssistant()
                
                # Start session
                session.start = Mock()
                session.generate_reply = Mock()
                
                # Test session start
                session.start(
                    room=mock_room,
                    agent=assistant,
                    room_input_options=mock_room_input_options,
                )
                
                # Verify session was started with correct parameters
                session.start.assert_called_once_with(
                    room=mock_room,
                    agent=assistant,
                    room_input_options=mock_room_input_options,
                )
                
                # Test greeting generation
                session.generate_reply(instructions=DEFAULT_GREETING_INSTRUCTIONS)
                
                # Verify greeting was generated
                session.generate_reply.assert_called_once_with(
                    instructions=DEFAULT_GREETING_INSTRUCTIONS
                )
        finally:
            os.unlink(config_path)
    
    @patch('homey_assistant.config.mcp_config.mcp.MCPServerHTTP')
    @patch('homey_assistant.config.mcp_config.mcp.MCPServerStdio')
    def test_mcp_server_integration(self, mock_stdio, mock_http):
        """Test integration with MCP servers."""
        # Setup mocks
        mock_http_server = Mock()
        mock_stdio_server = Mock()
        mock_http.return_value = mock_http_server
        mock_stdio.return_value = mock_stdio_server
        
        # Create temporary MCP config file with both server types
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "servers": {
                    "http_server": {
                        "type": "http",
                        "url": "http://example.com/mcp"
                    },
                    "stdio_server": {
                        "type": "stdio",
                        "command": "python",
                        "args": ["-m", "server"]
                    }
                }
            }, f)
            config_path = f.name
        
        try:
            # Load MCP servers
            config_loader = MCPConfigLoader(config_path)
            mcp_servers = config_loader.load_servers()
            
            # Verify both server types were created
            assert len(mcp_servers) == 2
            
            # Create session with MCP servers
            with patch('homey_assistant.agent.session.AgentSession') as mock_session_class, \
                 patch.object(SessionManager, '_configure_stt'), \
                 patch.object(SessionManager, '_configure_tts'), \
                 patch.object(SessionManager, '_configure_llm'):
                
                mock_session = Mock()
                mock_session_class.return_value = mock_session
                
                session_manager = SessionManager()
                session = session_manager.create_session(mcp_servers)
                
                # Verify session was created with MCP servers
                mock_session_class.assert_called_once()
                call_kwargs = mock_session_class.call_args.kwargs
                assert call_kwargs['mcp_servers'] == mcp_servers
        finally:
            os.unlink(config_path)
    
    @patch('homey_assistant.agent.session.AgentSession')
    def test_session_lifecycle_management(self, mock_session_class):
        """Test session lifecycle management."""
        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_room = Mock()
        mock_room_input_options = Mock()
        mock_vad = Mock()
        
        # Create session manager and session
        with patch.object(SessionManager, '_configure_stt'), \
             patch.object(SessionManager, '_configure_tts'), \
             patch.object(SessionManager, '_configure_llm'):
            
            session_manager = SessionManager()
            session = session_manager.create_session([], mock_vad)
            
            # Create assistant
            assistant = HomeyAssistant()
            
            # Test session start
            session.start = Mock()
            session.generate_reply = Mock()
            session.stop = Mock()
            
            # Start session
            session.start(
                room=mock_room,
                agent=assistant,
                room_input_options=mock_room_input_options,
            )
            
            # Verify session was started
            session.start.assert_called_once()
            
            # Generate reply
            session.generate_reply(instructions="Test instructions")
            
            # Verify reply was generated
            session.generate_reply.assert_called_once_with(instructions="Test instructions")
            
            # Stop session
            session.stop()
            
            # Verify session was stopped
            session.stop.assert_called_once()
    
    @patch('homey_assistant.agent.session.logger')
    def test_error_handling_and_logging(self, mock_logger):
        """Test error handling and logging during integration."""
        # Test error during MCP server loading
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "servers": {
                    "invalid_server": {
                        "type": "unsupported"
                    }
                }
            }, f)
            config_path = f.name
        
        try:
            # Load MCP servers with invalid configuration
            config_loader = MCPConfigLoader(config_path)
            mcp_servers = config_loader.load_servers()
            
            # Verify no servers were loaded due to invalid configuration
            assert len(mcp_servers) == 0
            
            # Test error during session creation
            with patch('homey_assistant.agent.session.AgentSession', side_effect=Exception("Test error")):
                session_manager = SessionManager()
                
                with pytest.raises(Exception, match="Test error"):
                    session_manager.create_session([])
                
                # Verify error was logged
                mock_logger.error.assert_called_with("Failed to create agent session: Test error")
        finally:
            os.unlink(config_path)