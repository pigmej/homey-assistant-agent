"""
Unit tests for configuration constants.

This module tests the constants defined in the homey_assistant.config.constants module
to ensure they have the expected values and types.
"""

import pytest
from homey_assistant.config.constants import (
    # Agent Configuration
    DEFAULT_MAX_TOOL_STEPS,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAXIMUM_REMOTE_CALLS,
    
    # Language and Voice Settings
    DEFAULT_LANGUAGE,
    DEFAULT_VOICE_NAME,
    DEFAULT_VOICE_GENDER,
    DEFAULT_SPEAKING_RATE,
    
    # STT Configuration
    DEFAULT_STT_MODEL,
    DEFAULT_STT_LANGUAGES,
    DEFAULT_STT_PUNCTUATE,
    
    # LLM Configuration
    DEFAULT_LLM_MODEL,
    
    # MCP Configuration
    DEFAULT_MCP_CONFIG_PATH,
    
    # Agent Instructions
    DEFAULT_AGENT_INSTRUCTIONS,
    DEFAULT_GREETING_INSTRUCTIONS,
    
    # Room Input Options
    DEFAULT_VIDEO_ENABLED
)


class TestConstants:
    """Test cases for configuration constants."""
    
    def test_agent_configuration_constants(self):
        """Test agent configuration constants have expected types and values."""
        assert isinstance(DEFAULT_MAX_TOOL_STEPS, int)
        assert DEFAULT_MAX_TOOL_STEPS > 0
        
        assert isinstance(DEFAULT_TEMPERATURE, float)
        assert 0.0 <= DEFAULT_TEMPERATURE <= 1.0
        
        assert isinstance(DEFAULT_MAXIMUM_REMOTE_CALLS, int)
        assert DEFAULT_MAXIMUM_REMOTE_CALLS > 0
    
    def test_language_and_voice_settings(self):
        """Test language and voice settings have expected types and formats."""
        assert isinstance(DEFAULT_LANGUAGE, str)
        assert len(DEFAULT_LANGUAGE) >= 2
        assert "-" in DEFAULT_LANGUAGE
        
        assert isinstance(DEFAULT_VOICE_NAME, str)
        assert len(DEFAULT_VOICE_NAME) > 0
        
        assert isinstance(DEFAULT_VOICE_GENDER, str)
        assert DEFAULT_VOICE_GENDER in ["male", "female", "neutral"]
        
        assert isinstance(DEFAULT_SPEAKING_RATE, float)
        assert DEFAULT_SPEAKING_RATE > 0
    
    def test_stt_configuration(self):
        """Test STT configuration constants have expected types and values."""
        assert isinstance(DEFAULT_STT_MODEL, str)
        assert len(DEFAULT_STT_MODEL) > 0
        
        assert isinstance(DEFAULT_STT_LANGUAGES, list)
        assert len(DEFAULT_STT_LANGUAGES) > 0
        assert all(isinstance(lang, str) for lang in DEFAULT_STT_LANGUAGES)
        
        assert isinstance(DEFAULT_STT_PUNCTUATE, bool)
    
    def test_llm_configuration(self):
        """Test LLM configuration constants have expected types and values."""
        assert isinstance(DEFAULT_LLM_MODEL, str)
        assert len(DEFAULT_LLM_MODEL) > 0
    
    def test_mcp_configuration(self):
        """Test MCP configuration constants have expected types and values."""
        assert isinstance(DEFAULT_MCP_CONFIG_PATH, str)
        assert len(DEFAULT_MCP_CONFIG_PATH) > 0
        assert DEFAULT_MCP_CONFIG_PATH.endswith(".json")
    
    def test_agent_instructions(self):
        """Test agent instructions constants have expected types and content."""
        assert isinstance(DEFAULT_AGENT_INSTRUCTIONS, str)
        assert len(DEFAULT_AGENT_INSTRUCTIONS) > 0
        
        # Check for key phrases in instructions
        required_phrases = [
            "AI assistant",
            "Homey smart home platform",
            "polish language",
            "MCP servers",
            "Memory Retrieval"
        ]
        for phrase in required_phrases:
            assert phrase in DEFAULT_AGENT_INSTRUCTIONS
        
        assert isinstance(DEFAULT_GREETING_INSTRUCTIONS, str)
        assert len(DEFAULT_GREETING_INSTRUCTIONS) > 0
        assert "Greet the user" in DEFAULT_GREETING_INSTRUCTIONS
    
    def test_room_input_options(self):
        """Test room input options constants have expected types and values."""
        assert isinstance(DEFAULT_VIDEO_ENABLED, bool)