"""
Unit tests for the SessionManager class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List

from homey_assistant.agent.session import SessionManager
from homey_assistant.config.constants import (
    DEFAULT_MAX_TOOL_STEPS,
    DEFAULT_TEMPERATURE,
    DEFAULT_LANGUAGE,
    DEFAULT_VOICE_NAME,
    DEFAULT_STT_MODEL,
    DEFAULT_LLM_MODEL,
)


class TestSessionManager:
    """Test cases for the SessionManager class."""

    def test_session_manager_initialization_with_defaults(self):
        """Test SessionManager initializes correctly with default values."""
        manager = SessionManager()

        assert manager.max_tool_steps == DEFAULT_MAX_TOOL_STEPS
        assert manager.temperature == DEFAULT_TEMPERATURE
        assert manager.language == DEFAULT_LANGUAGE
        assert manager.voice_name == DEFAULT_VOICE_NAME
        assert manager.stt_model == DEFAULT_STT_MODEL
        assert manager.llm_model == DEFAULT_LLM_MODEL

    def test_session_manager_initialization_with_custom_values(self):
        """Test SessionManager initializes correctly with custom values."""
        custom_max_steps = 15
        custom_temperature = 0.5
        custom_language = "en-US"

        manager = SessionManager(
            max_tool_steps=custom_max_steps,
            temperature=custom_temperature,
            language=custom_language,
        )

        assert manager.max_tool_steps == custom_max_steps
        assert manager.temperature == custom_temperature
        assert manager.language == custom_language

    @patch("homey_assistant.agent.session.google.STT")
    def test_configure_stt(self, mock_stt_class):
        """Test STT configuration."""
        mock_stt_instance = Mock()
        mock_stt_class.return_value = mock_stt_instance

        manager = SessionManager()
        stt = manager._configure_stt()

        # Verify STT was created with correct parameters
        mock_stt_class.assert_called_once_with(
            model=DEFAULT_STT_MODEL,
            languages=manager.stt_languages,
            punctuate=manager.stt_punctuate,
        )
        assert stt == mock_stt_instance

    @patch("homey_assistant.agent.session.google.TTS")
    def test_configure_tts(self, mock_tts_class):
        """Test TTS configuration."""
        mock_tts_instance = Mock()
        mock_tts_class.return_value = mock_tts_instance

        manager = SessionManager()
        tts = manager._configure_tts()

        # Verify TTS was created with correct parameters
        mock_tts_class.assert_called_once_with(
            gender=manager.voice_gender,
            voice_name=manager.voice_name,
            language=manager.language,
            speaking_rate=manager.speaking_rate,
        )
        assert tts == mock_tts_instance

    @patch("homey_assistant.agent.session.google.LLM")
    def test_configure_llm(self, mock_llm_class):
        """Test LLM configuration."""
        mock_llm_instance = Mock()
        mock_llm_class.return_value = mock_llm_instance

        manager = SessionManager()
        llm = manager._configure_llm()

        # Verify LLM was created with correct parameters
        mock_llm_class.assert_called_once_with(
            model=manager.llm_model,
            temperature=manager.temperature,
            automatic_function_calling_config={
                "maximum_remote_calls": manager.maximum_remote_calls
            },
        )
        assert llm == mock_llm_instance

    @patch("homey_assistant.agent.session.noise_cancellation.BVC")
    @patch("homey_assistant.agent.session.RoomInputOptions")
    def test_create_room_input_options(self, mock_room_options_class, mock_bvc):
        """Test room input options creation."""
        mock_room_options_instance = Mock()
        mock_room_options_class.return_value = mock_room_options_instance
        mock_bvc_instance = Mock()
        mock_bvc.return_value = mock_bvc_instance

        manager = SessionManager()
        options = manager.create_room_input_options()

        # Verify RoomInputOptions was created with correct parameters
        mock_room_options_class.assert_called_once_with(
            video_enabled=manager.video_enabled,
            noise_cancellation=mock_bvc_instance,
        )
        assert options == mock_room_options_instance

    @patch("homey_assistant.agent.session.AgentSession")
    @patch("homey_assistant.agent.session.google.STT")
    @patch("homey_assistant.agent.session.google.TTS")
    @patch("homey_assistant.agent.session.google.LLM")
    def test_create_session(
        self, mock_llm_class, mock_tts_class, mock_stt_class, mock_session_class
    ):
        """Test agent session creation."""
        # Setup mocks
        mock_stt = Mock()
        mock_tts = Mock()
        mock_llm = Mock()
        mock_session = Mock()
        mock_vad = Mock()
        mock_mcp_servers = [Mock(), Mock()]

        mock_stt_class.return_value = mock_stt
        mock_tts_class.return_value = mock_tts
        mock_llm_class.return_value = mock_llm
        mock_session_class.return_value = mock_session

        manager = SessionManager()
        session = manager.create_session(mock_mcp_servers, mock_vad)

        # Verify AgentSession was created with correct parameters
        mock_session_class.assert_called_once_with(
            max_tool_steps=manager.max_tool_steps,
            vad=mock_vad,
            stt=mock_stt,
            tts=mock_tts,
            llm=mock_llm,
            mcp_servers=mock_mcp_servers,
        )
        assert session == mock_session

    @patch("homey_assistant.agent.session.AgentSession")
    def test_create_session_without_vad(self, mock_session_class):
        """Test agent session creation without VAD."""
        mock_session = Mock()
        mock_mcp_servers = []
        mock_session_class.return_value = mock_session

        with (
            patch.object(SessionManager, "_configure_stt") as mock_stt,
            patch.object(SessionManager, "_configure_tts") as mock_tts,
            patch.object(SessionManager, "_configure_llm") as mock_llm,
        ):
            manager = SessionManager()
            session = manager.create_session(mock_mcp_servers)

            # Verify AgentSession was created with vad=None
            mock_session_class.assert_called_once_with(
                max_tool_steps=manager.max_tool_steps,
                vad=None,
                stt=mock_stt.return_value,
                tts=mock_tts.return_value,
                llm=mock_llm.return_value,
                mcp_servers=mock_mcp_servers,
            )

    @patch("homey_assistant.agent.session.google.STT")
    def test_configure_stt_error_handling(self, mock_stt_class):
        """Test STT configuration error handling."""
        mock_stt_class.side_effect = Exception("STT configuration failed")

        manager = SessionManager()

        with pytest.raises(Exception, match="STT configuration failed"):
            manager._configure_stt()

    @patch("homey_assistant.agent.session.google.TTS")
    def test_configure_tts_error_handling(self, mock_tts_class):
        """Test TTS configuration error handling."""
        mock_tts_class.side_effect = Exception("TTS configuration failed")

        manager = SessionManager()

        with pytest.raises(Exception, match="TTS configuration failed"):
            manager._configure_tts()

    @patch("homey_assistant.agent.session.google.LLM")
    def test_configure_llm_error_handling(self, mock_llm_class):
        """Test LLM configuration error handling."""
        mock_llm_class.side_effect = Exception("LLM configuration failed")

        manager = SessionManager()

        with pytest.raises(Exception, match="LLM configuration failed"):
            manager._configure_llm()

    @patch("homey_assistant.agent.session.AgentSession")
    def test_create_session_error_handling(self, mock_session_class):
        """Test session creation error handling."""
        mock_session_class.side_effect = Exception("Session creation failed")

        manager = SessionManager()

        with pytest.raises(Exception, match="Session creation failed"):
            manager.create_session([])

    def test_stt_languages_default_copy(self):
        """Test that STT languages list is properly copied from defaults."""
        manager1 = SessionManager()
        manager2 = SessionManager()

        # Modify one manager's languages
        manager1.stt_languages.append("en-US")

        # Verify the other manager's languages are not affected
        assert "en-US" not in manager2.stt_languages
        assert len(manager1.stt_languages) != len(manager2.stt_languages)

    @patch("homey_assistant.agent.session.noise_cancellation.BVC")
    @patch("homey_assistant.agent.session.RoomInputOptions")
    def test_create_room_input_options_error_handling(
        self, mock_room_options_class, mock_bvc
    ):
        """Test error handling in room input options creation."""
        mock_bvc.side_effect = Exception("BVC initialization failed")

        manager = SessionManager()

        with pytest.raises(Exception, match="BVC initialization failed"):
            manager.create_room_input_options()

    def test_session_manager_with_all_custom_parameters(self):
        """Test SessionManager initialization with all custom parameters."""
        custom_params = {
            "max_tool_steps": 30,
            "temperature": 0.3,
            "maximum_remote_calls": 50,
            "language": "en-US",
            "voice_name": "en-US-Standard-A",
            "voice_gender": "male",
            "speaking_rate": 0.9,
            "stt_model": "custom_model",
            "stt_languages": ["en-US", "es-ES"],
            "stt_punctuate": True,
            "llm_model": "custom_llm",
            "video_enabled": True,
        }

        manager = SessionManager(**custom_params)

        # Verify all parameters were set correctly
        for param, value in custom_params.items():
            assert getattr(manager, param) == value

    @patch("homey_assistant.agent.session.logger")
    def test_session_manager_logging(self, mock_logger):
        """Test that SessionManager logs initialization."""
        SessionManager()

        # Verify logging was called
        mock_logger.info.assert_called_with(
            "SessionManager initialized with configuration"
        )

    @patch("homey_assistant.agent.session.logger")
    def test_session_creation_logging(self, mock_logger):
        """Test logging during session creation."""
        with (
            patch("homey_assistant.agent.session.AgentSession") as mock_session_class,
            patch.object(SessionManager, "_configure_stt") as mock_stt,
            patch.object(SessionManager, "_configure_tts") as mock_tts,
            patch.object(SessionManager, "_configure_llm") as mock_llm,
        ):
            manager = SessionManager()
            manager.create_session([])

            # Verify logging calls
            mock_logger.info.assert_any_call(
                "Creating agent session with 0 MCP servers"
            )
            mock_logger.info.assert_any_call("Agent session created successfully")

    @patch("homey_assistant.agent.session.logger")
    def test_session_creation_error_logging(self, mock_logger):
        """Test error logging during session creation."""
        with patch(
            "homey_assistant.agent.session.AgentSession",
            side_effect=Exception("Test error"),
        ):
            manager = SessionManager()

            with pytest.raises(Exception, match="Test error"):
                manager.create_session([])

            # Verify error logging
            mock_logger.error.assert_called_with(
                "Failed to create agent session: Test error"
            )

    def test_integration_with_mcp_servers(self):
        """Test integration with MCP servers."""
        mock_mcp_servers = [Mock(), Mock()]

        with (
            patch("homey_assistant.agent.session.AgentSession") as mock_session_class,
            patch.object(SessionManager, "_configure_stt") as mock_stt,
            patch.object(SessionManager, "_configure_tts") as mock_tts,
            patch.object(SessionManager, "_configure_llm") as mock_llm,
        ):
            manager = SessionManager()
            session = manager.create_session(mock_mcp_servers)

            # Verify MCP servers were passed to AgentSession
            mock_session_class.assert_called_once()
            call_kwargs = mock_session_class.call_args.kwargs
            assert call_kwargs["mcp_servers"] == mock_mcp_servers
