"""
Unit tests for the HomeyAssistant agent class.
"""

import pytest
from unittest.mock import patch
from homey_assistant.agent.assistant import HomeyAssistant


class TestHomeyAssistant:
    """Test cases for the HomeyAssistant class."""
    
    def test_assistant_initialization_with_default_instructions(self):
        """Test that HomeyAssistant initializes correctly with default instructions."""
        assistant = HomeyAssistant()
        
        # Verify the assistant is properly initialized
        assert assistant is not None
        assert hasattr(assistant, 'instructions')
        assert assistant.instructions is not None
        assert len(assistant.instructions) > 0
        
        # Verify key elements are in the default instructions
        instructions = assistant.instructions
        assert "Homey smart home platform" in instructions
        assert "polish language" in instructions
        assert "MCP servers" in instructions
        assert "Memory Retrieval" in instructions
        assert "User Identification" in instructions
    
    def test_assistant_initialization_with_custom_instructions(self):
        """Test that HomeyAssistant initializes correctly with custom instructions."""
        custom_instructions = "You are a test assistant with custom behavior."
        assistant = HomeyAssistant(instructions=custom_instructions)
        
        # Verify the assistant uses the custom instructions
        assert assistant is not None
        assert assistant.instructions == custom_instructions
    
    def test_default_instructions_content(self):
        """Test that default instructions contain required elements."""
        assistant = HomeyAssistant()
        instructions = assistant.instructions
        
        # Test for key instruction components
        required_elements = [
            "helpful AI assistant",
            "Homey smart home platform",
            "polish language",
            "Keep your messages short",
            "Greet the user very shortly",
            "Welcome user just with 'Hey'",
            "MCP servers",
            "Voice mode",
            "ask for confirmation",
            "Knowledge Graph MCP Server",
            "User Identification",
            "Memory Retrieval",
            "Memory Update"
        ]
        
        for element in required_elements:
            assert element in instructions, f"Missing required element: {element}"
    
    def test_assistant_inherits_from_agent(self):
        """Test that HomeyAssistant properly inherits from Agent."""
        from livekit.agents import Agent
        
        assistant = HomeyAssistant()
        assert isinstance(assistant, Agent)
    
    def test_get_default_instructions_method(self):
        """Test the _get_default_instructions private method."""
        assistant = HomeyAssistant()
        default_instructions = assistant._get_default_instructions()
        
        assert isinstance(default_instructions, str)
        assert len(default_instructions) > 0
        assert "Homey smart home platform" in default_instructions
    
    def test_assistant_with_none_instructions(self):
        """Test that passing None for instructions uses defaults."""
        assistant = HomeyAssistant(instructions=None)
        default_assistant = HomeyAssistant()
        
        assert assistant.instructions == default_assistant.instructions
    
    def test_assistant_with_empty_string_instructions(self):
        """Test that passing empty string for instructions is preserved."""
        assistant = HomeyAssistant(instructions="")
        
        assert assistant.instructions == ""
        
    def test_assistant_with_constants_instructions(self):
        """Test that assistant can be initialized with instructions from constants."""
        from homey_assistant.config.constants import DEFAULT_AGENT_INSTRUCTIONS
        
        # Create assistant with instructions from constants
        assistant = HomeyAssistant(instructions=DEFAULT_AGENT_INSTRUCTIONS)
        
        # Verify the assistant uses the provided instructions
        assert assistant.instructions == DEFAULT_AGENT_INSTRUCTIONS
    
    def test_assistant_parent_class_initialization(self):
        """Test that parent Agent class is initialized correctly."""
        with patch('homey_assistant.agent.assistant.Agent.__init__', return_value=None) as mock_init:
            custom_instructions = "Custom test instructions"
            
            # Create assistant with custom instructions
            assistant = HomeyAssistant(instructions=custom_instructions)
            
            # Verify parent class was initialized with correct parameters
            mock_init.assert_called_once_with(instructions=custom_instructions)
    
    def test_assistant_instructions_consistency(self):
        """Test that default instructions are consistent with constants."""
        from homey_assistant.config.constants import DEFAULT_AGENT_INSTRUCTIONS
        
        assistant = HomeyAssistant()
        default_instructions = assistant._get_default_instructions()
        
        # Verify key phrases are consistent between constants and method
        key_phrases = [
            "Homey smart home platform",
            "polish language",
            "MCP servers",
            "Memory Retrieval"
        ]
        
        for phrase in key_phrases:
            assert (phrase in DEFAULT_AGENT_INSTRUCTIONS) == (phrase in default_instructions), \
                f"Inconsistency for phrase '{phrase}' between constants and method"