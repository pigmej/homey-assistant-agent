"""
Homey Assistant Agent Implementation.

This module contains the HomeyAssistant class which defines the AI assistant
behavior and instructions for the Homey smart home platform integration.
"""

from typing import Optional
from livekit.agents import Agent

from homey_assistant.config.constants import DEFAULT_AGENT_INSTRUCTIONS


class HomeyAssistant(Agent):
    """
    AI Assistant agent for Homey smart home platform.

    This agent provides voice-based interaction with Homey smart home devices
    and services, supporting Polish language by default and integrating with
    various MCP servers for extended functionality.
    """

    def __init__(self, instructions: Optional[str] = None) -> None:
        """
        Initialize the Homey Assistant agent.

        Args:
            instructions: Custom instructions for the agent. If None, uses default
                         instructions optimized for Homey smart home interaction.
        """
        if instructions is None:
            instructions = self._get_default_instructions()

        super().__init__(instructions=instructions)

    def _get_default_instructions(self) -> str:
        """
        Get the default instructions for the Homey Assistant.

        Returns:
            str: Comprehensive instructions for the assistant's behavior.
        """
        return DEFAULT_AGENT_INSTRUCTIONS
