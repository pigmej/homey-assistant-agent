"""
Session Management for Homey Assistant Agent.

This module handles the creation and configuration of agent sessions,
including STT, TTS, and LLM component setup with configurable providers.
"""

import logging
from typing import List, Optional, Any

from livekit.agents import AgentSession, mcp, RoomInputOptions
from livekit.plugins import google, silero, noise_cancellation

from ..config.constants import (
    DEFAULT_MAX_TOOL_STEPS,
    DEFAULT_VIDEO_ENABLED,
)
from ..config.providers import (
    ProviderConfigLoader,
    ProviderFactory,
    TTSConfig,
    STTConfig,
    LLMConfig,
)

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages agent session creation and configuration.

    This class handles the setup of AgentSession with properly configured
    STT, TTS, and LLM components for the Homey Assistant using configurable providers.
    """

    def __init__(
        self,
        max_tool_steps: int = DEFAULT_MAX_TOOL_STEPS,
        video_enabled: bool = DEFAULT_VIDEO_ENABLED,
        tts_config: Optional[TTSConfig] = None,
        stt_config: Optional[STTConfig] = None,
        llm_config: Optional[LLMConfig] = None,
    ) -> None:
        """
        Initialize the SessionManager with configuration parameters.

        Args:
            max_tool_steps: Maximum consecutive MCP tool calls allowed
            video_enabled: Whether video is enabled in room input
            tts_config: TTS provider configuration (loaded from env if None)
            stt_config: STT provider configuration (loaded from env if None)
            llm_config: LLM provider configuration (loaded from env if None)
        """
        self.max_tool_steps = max_tool_steps
        self.video_enabled = video_enabled

        # Load provider configurations from environment if not provided
        self.tts_config = tts_config or ProviderConfigLoader.load_tts_config()
        self.stt_config = stt_config or ProviderConfigLoader.load_stt_config()
        self.llm_config = llm_config or ProviderConfigLoader.load_llm_config()

        logger.info(
            f"SessionManager initialized with TTS: {self.tts_config.provider.value}, "
            f"STT: {self.stt_config.provider.value}, LLM: {self.llm_config.provider.value}"
        )

    def create_session(
        self, mcp_servers: List[mcp.MCPServer], vad: Optional[Any] = None
    ) -> AgentSession:
        """
        Create and configure an AgentSession.

        Args:
            mcp_servers: List of MCP servers to use
            vad: Voice Activity Detection instance

        Returns:
            AgentSession: Configured agent session

        Raises:
            Exception: If session creation fails
        """
        try:
            logger.info(f"Creating agent session with {len(mcp_servers)} MCP servers")

            session = AgentSession(
                max_tool_steps=self.max_tool_steps,
                vad=vad,
                stt=self._configure_stt(),
                tts=self._configure_tts(),
                llm=self._configure_llm(),
                mcp_servers=mcp_servers,
            )

            logger.info("Agent session created successfully")
            return session

        except Exception as e:
            logger.error(f"Failed to create agent session: {e}")
            raise

    def _configure_stt(self) -> Any:
        """
        Configure Speech-to-Text component using provider factory.

        Returns:
            Configured STT instance

        Raises:
            Exception: If STT configuration fails
        """
        try:
            logger.debug(
                f"Configuring STT with provider: {self.stt_config.provider.value}"
            )
            return ProviderFactory.create_stt(self.stt_config)

        except Exception as e:
            logger.error(f"Failed to configure STT: {e}")
            raise

    def _configure_tts(self) -> Any:
        """
        Configure Text-to-Speech component using provider factory.

        Returns:
            Configured TTS instance

        Raises:
            Exception: If TTS configuration fails
        """
        try:
            logger.debug(
                f"Configuring TTS with provider: {self.tts_config.provider.value}"
            )
            return ProviderFactory.create_tts(self.tts_config)

        except Exception as e:
            logger.error(f"Failed to configure TTS: {e}")
            raise

    def _configure_llm(self) -> Any:
        """
        Configure Large Language Model component using provider factory.

        Returns:
            Configured LLM instance

        Raises:
            Exception: If LLM configuration fails
        """
        try:
            logger.debug(
                f"Configuring LLM with provider: {self.llm_config.provider.value}"
            )
            return ProviderFactory.create_llm(self.llm_config)

        except Exception as e:
            logger.error(f"Failed to configure LLM: {e}")
            raise

    def create_room_input_options(self) -> RoomInputOptions:
        """
        Create room input options for the session.

        Returns:
            RoomInputOptions: Configured room input options
        """
        try:
            logger.debug(
                f"Creating room input options with video_enabled: {self.video_enabled}"
            )

            options = RoomInputOptions(
                video_enabled=self.video_enabled,
                # LiveKit Cloud enhanced noise cancellation
                # - If self-hosting, omit this parameter
                # - For telephony applications, use `BVCTelephony` for best results
                noise_cancellation=noise_cancellation.BVC(),
            )

            logger.debug("Room input options created successfully")
            return options

        except Exception as e:
            logger.error(f"Failed to create room input options: {e}")
            raise
