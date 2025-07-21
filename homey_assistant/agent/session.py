"""
Session Management for Homey Assistant Agent.

This module handles the creation and configuration of agent sessions,
including STT, TTS, and LLM component setup.
"""

import logging
from typing import List, Optional, Any

from livekit.agents import AgentSession, mcp, RoomInputOptions
from livekit.plugins import google, silero, noise_cancellation

from ..config.constants import (
    DEFAULT_MAX_TOOL_STEPS,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAXIMUM_REMOTE_CALLS,
    DEFAULT_LANGUAGE,
    DEFAULT_VOICE_NAME,
    DEFAULT_VOICE_GENDER,
    DEFAULT_SPEAKING_RATE,
    DEFAULT_STT_MODEL,
    DEFAULT_STT_LANGUAGES,
    DEFAULT_STT_PUNCTUATE,
    DEFAULT_LLM_MODEL,
    DEFAULT_VIDEO_ENABLED,
)

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages agent session creation and configuration.
    
    This class handles the setup of AgentSession with properly configured
    STT, TTS, and LLM components for the Homey Assistant.
    """
    
    def __init__(
        self,
        max_tool_steps: int = DEFAULT_MAX_TOOL_STEPS,
        temperature: float = DEFAULT_TEMPERATURE,
        maximum_remote_calls: int = DEFAULT_MAXIMUM_REMOTE_CALLS,
        language: str = DEFAULT_LANGUAGE,
        voice_name: str = DEFAULT_VOICE_NAME,
        voice_gender: str = DEFAULT_VOICE_GENDER,
        speaking_rate: float = DEFAULT_SPEAKING_RATE,
        stt_model: str = DEFAULT_STT_MODEL,
        stt_languages: List[str] = None,
        stt_punctuate: bool = DEFAULT_STT_PUNCTUATE,
        llm_model: str = DEFAULT_LLM_MODEL,
        video_enabled: bool = DEFAULT_VIDEO_ENABLED,
    ) -> None:
        """
        Initialize the SessionManager with configuration parameters.
        
        Args:
            max_tool_steps: Maximum consecutive MCP tool calls allowed
            temperature: LLM temperature setting
            maximum_remote_calls: Maximum remote function calls
            language: Default language for TTS and STT
            voice_name: TTS voice name
            voice_gender: TTS voice gender
            speaking_rate: TTS speaking rate
            stt_model: STT model to use
            stt_languages: List of languages for STT
            stt_punctuate: Whether to punctuate STT output
            llm_model: LLM model to use
            video_enabled: Whether video is enabled in room input
        """
        self.max_tool_steps = max_tool_steps
        self.temperature = temperature
        self.maximum_remote_calls = maximum_remote_calls
        self.language = language
        self.voice_name = voice_name
        self.voice_gender = voice_gender
        self.speaking_rate = speaking_rate
        self.stt_model = stt_model
        self.stt_languages = stt_languages or DEFAULT_STT_LANGUAGES.copy()
        self.stt_punctuate = stt_punctuate
        self.llm_model = llm_model
        self.video_enabled = video_enabled
        
        logger.info("SessionManager initialized with configuration")
    
    def create_session(
        self,
        mcp_servers: List[mcp.MCPServer],
        vad: Optional[Any] = None
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
    
    def _configure_stt(self) -> google.STT:
        """
        Configure Speech-to-Text component.
        
        Returns:
            google.STT: Configured STT instance
            
        Raises:
            Exception: If STT configuration fails
        """
        try:
            logger.debug(f"Configuring STT with model: {self.stt_model}, languages: {self.stt_languages}")
            
            stt = google.STT(
                model=self.stt_model,
                languages=self.stt_languages,
                punctuate=self.stt_punctuate
            )
            
            logger.debug("STT configured successfully")
            return stt
            
        except Exception as e:
            logger.error(f"Failed to configure STT: {e}")
            raise
    
    def _configure_tts(self) -> google.TTS:
        """
        Configure Text-to-Speech component.
        
        Returns:
            google.TTS: Configured TTS instance
            
        Raises:
            Exception: If TTS configuration fails
        """
        try:
            logger.debug(f"Configuring TTS with voice: {self.voice_name}, language: {self.language}")
            
            tts = google.TTS(
                gender=self.voice_gender,
                voice_name=self.voice_name,
                language=self.language,
                speaking_rate=self.speaking_rate,
            )
            
            logger.debug("TTS configured successfully")
            return tts
            
        except Exception as e:
            logger.error(f"Failed to configure TTS: {e}")
            raise
    
    def _configure_llm(self) -> google.LLM:
        """
        Configure Large Language Model component.
        
        Returns:
            google.LLM: Configured LLM instance
            
        Raises:
            Exception: If LLM configuration fails
        """
        try:
            logger.debug(f"Configuring LLM with model: {self.llm_model}, temperature: {self.temperature}")
            
            llm = google.LLM(
                model=self.llm_model,
                temperature=self.temperature,
                automatic_function_calling_config={
                    "maximum_remote_calls": self.maximum_remote_calls
                },
            )
            
            logger.debug("LLM configured successfully")
            return llm
            
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
            logger.debug(f"Creating room input options with video_enabled: {self.video_enabled}")
            
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