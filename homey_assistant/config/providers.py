"""
Provider Configuration for TTS, STT, and LLM services.

This module handles configuration and creation of different AI service providers
including ElevenLabs TTS, Google TTS/STT/LLM, and other supported providers.
"""

import logging
import os
from enum import Enum
from typing import Any, Optional
from dataclasses import dataclass

from livekit.plugins import google, elevenlabs, openai, deepgram
from livekit.plugins.elevenlabs import VoiceSettings

logger = logging.getLogger(__name__)


class TTSProvider(Enum):
    """Supported TTS providers."""

    GOOGLE = "google"
    ELEVENLABS = "elevenlabs"


class STTProvider(Enum):
    """Supported STT providers."""

    GOOGLE = "google"
    DEEPGRAM = "deepgram"


class LLMProvider(Enum):
    """Supported LLM providers."""

    GOOGLE = "google"
    OPENAI = "openai"


@dataclass
class TTSConfig:
    """Configuration for TTS providers."""

    provider: TTSProvider
    # Common settings
    language: str = "pl-PL"
    speaking_rate: float = 1.15

    # Google-specific settings
    voice_name: Optional[str] = None
    voice_gender: Optional[str] = None

    # ElevenLabs-specific settings
    voice_id: Optional[str] = None
    model_id: Optional[str] = None
    stability: Optional[float] = None
    similarity_boost: Optional[float] = None
    style: Optional[float] = None
    speed: Optional[float] = None
    use_speaker_boost: Optional[bool] = None


@dataclass
class STTConfig:
    """Configuration for STT providers."""

    provider: STTProvider
    model: str = "latest_long"
    languages: list = None
    punctuate: bool = False

    # Deepgram-specific settings
    smart_format: Optional[bool] = None
    interim_results: Optional[bool] = None

    def __post_init__(self):
        if self.languages is None:
            self.languages = ["pl-PL"]


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""

    provider: LLMProvider
    model: str = "gemini-2.5-flash"
    temperature: float = 0.7
    maximum_remote_calls: int = 100

    # OpenAI-specific settings
    max_tokens: Optional[int] = None


class ProviderFactory:
    """Factory class for creating configured provider instances."""

    @staticmethod
    def create_tts(config: TTSConfig) -> Any:
        """
        Create a TTS instance based on configuration.

        Args:
            config: TTS configuration

        Returns:
            Configured TTS instance

        Raises:
            ValueError: If provider is not supported
            Exception: If provider creation fails
        """
        try:
            logger.debug(f"Creating TTS provider: {config.provider.value}")

            if config.provider == TTSProvider.GOOGLE:
                return ProviderFactory._create_google_tts(config)
            elif config.provider == TTSProvider.ELEVENLABS:
                return ProviderFactory._create_elevenlabs_tts(config)
            else:
                raise ValueError(f"Unsupported TTS provider: {config.provider}")

        except Exception as e:
            logger.error(f"Failed to create TTS provider {config.provider.value}: {e}")
            raise

    @staticmethod
    def create_stt(config: STTConfig) -> Any:
        """
        Create an STT instance based on configuration.

        Args:
            config: STT configuration

        Returns:
            Configured STT instance

        Raises:
            ValueError: If provider is not supported
            Exception: If provider creation fails
        """
        try:
            logger.debug(f"Creating STT provider: {config.provider.value}")

            if config.provider == STTProvider.GOOGLE:
                return ProviderFactory._create_google_stt(config)
            elif config.provider == STTProvider.DEEPGRAM:
                return ProviderFactory._create_deepgram_stt(config)
            else:
                raise ValueError(f"Unsupported STT provider: {config.provider}")

        except Exception as e:
            logger.error(f"Failed to create STT provider {config.provider.value}: {e}")
            raise

    @staticmethod
    def create_llm(config: LLMConfig) -> Any:
        """
        Create an LLM instance based on configuration.

        Args:
            config: LLM configuration

        Returns:
            Configured LLM instance

        Raises:
            ValueError: If provider is not supported
            Exception: If provider creation fails
        """
        try:
            logger.debug(f"Creating LLM provider: {config.provider.value}")

            if config.provider == LLMProvider.GOOGLE:
                return ProviderFactory._create_google_llm(config)
            elif config.provider == LLMProvider.OPENAI:
                return ProviderFactory._create_openai_llm(config)
            else:
                raise ValueError(f"Unsupported LLM provider: {config.provider}")

        except Exception as e:
            logger.error(f"Failed to create LLM provider {config.provider.value}: {e}")
            raise

    @staticmethod
    def _create_google_tts(config: TTSConfig) -> google.TTS:
        """Create Google TTS instance."""
        kwargs = {
            "language": config.language,
            "speaking_rate": config.speaking_rate,
        }

        if config.voice_name:
            kwargs["voice_name"] = config.voice_name
        if config.voice_gender:
            kwargs["gender"] = config.voice_gender

        return google.TTS(**kwargs)

    @staticmethod
    def _create_elevenlabs_tts(config: TTSConfig) -> elevenlabs.TTS:
        """Create ElevenLabs TTS instance using the new simplified API (v1.1.6+)."""
        kwargs = {}

        # Set voice_id if specified
        if config.voice_id:
            kwargs["voice_id"] = config.voice_id

        # Set model if specified
        if config.model_id:
            kwargs["model"] = config.model_id

        # Create VoiceSettings if any custom settings are provided
        if any(
            [
                config.stability is not None,
                config.similarity_boost is not None,
                config.style is not None,
                config.speed is not None,
                config.use_speaker_boost is not None,
            ]
        ):
            voice_settings_kwargs = {
                "stability": config.stability if config.stability is not None else 0.5,
                "similarity_boost": config.similarity_boost
                if config.similarity_boost is not None
                else 0.75,
            }

            if config.style is not None:
                voice_settings_kwargs["style"] = config.style
            if config.speed is not None:
                voice_settings_kwargs["speed"] = config.speed
            if config.use_speaker_boost is not None:
                voice_settings_kwargs["use_speaker_boost"] = config.use_speaker_boost

            kwargs["voice_settings"] = VoiceSettings(**voice_settings_kwargs)

        # Add API key - the plugin checks both ELEVEN_API_KEY and ELEVENLABS_API_KEY
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if api_key:
            kwargs["api_key"] = api_key

        return elevenlabs.TTS(**kwargs)

    @staticmethod
    def _create_google_stt(config: STTConfig) -> google.STT:
        """Create Google STT instance."""
        return google.STT(
            model=config.model, languages=config.languages, punctuate=config.punctuate
        )

    @staticmethod
    def _create_deepgram_stt(config: STTConfig) -> deepgram.STT:
        """Create Deepgram STT instance."""
        kwargs = {
            "model": config.model,
            "language": config.languages[0] if config.languages else "pl-PL",
        }

        if config.smart_format is not None:
            kwargs["smart_format"] = config.smart_format
        if config.interim_results is not None:
            kwargs["interim_results"] = config.interim_results
        if config.punctuate is not None:
            kwargs["punctuate"] = config.punctuate

        return deepgram.STT(**kwargs)

    @staticmethod
    def _create_google_llm(config: LLMConfig) -> google.LLM:
        """Create Google LLM instance."""
        return google.LLM(
            model=config.model,
            temperature=config.temperature,
            automatic_function_calling_config={
                "maximum_remote_calls": config.maximum_remote_calls
            },
        )

    @staticmethod
    def _create_openai_llm(config: LLMConfig) -> openai.LLM:
        """Create OpenAI LLM instance."""
        kwargs = {
            "model": config.model,
            "temperature": config.temperature,
        }

        if config.max_tokens:
            kwargs["max_tokens"] = config.max_tokens

        return openai.LLM(**kwargs)


class ProviderConfigLoader:
    """Loads provider configurations from environment variables and defaults."""

    @staticmethod
    def load_tts_config() -> TTSConfig:
        """
        Load TTS configuration from environment variables.

        Returns:
            TTSConfig: Loaded TTS configuration
        """
        provider_name = os.getenv("TTS_PROVIDER", "google").lower()

        try:
            provider = TTSProvider(provider_name)
        except ValueError:
            logger.warning(
                f"Unknown TTS provider '{provider_name}', defaulting to Google"
            )
            provider = TTSProvider.GOOGLE

        config = TTSConfig(
            provider=provider,
            language=os.getenv("TTS_LANGUAGE", "pl-PL"),
            speaking_rate=float(os.getenv("TTS_SPEAKING_RATE", "1.15")),
        )

        # Provider-specific settings
        if provider == TTSProvider.GOOGLE:
            config.voice_name = os.getenv(
                "TTS_GOOGLE_VOICE_NAME", "pl-PL-Chirp3-HD-Despina"
            )
            config.voice_gender = os.getenv("TTS_GOOGLE_VOICE_GENDER", "female")
        elif provider == TTSProvider.ELEVENLABS:
            config.voice_id = os.getenv("TTS_ELEVENLABS_VOICE_ID")
            config.model_id = os.getenv(
                "TTS_ELEVENLABS_MODEL_ID", "eleven_multilingual_v2"
            )

            # Optional ElevenLabs settings
            stability = os.getenv("TTS_ELEVENLABS_STABILITY")
            if stability:
                config.stability = float(stability)

            similarity_boost = os.getenv("TTS_ELEVENLABS_SIMILARITY_BOOST")
            if similarity_boost:
                config.similarity_boost = float(similarity_boost)

            style = os.getenv("TTS_ELEVENLABS_STYLE")
            if style:
                config.style = float(style)

            speed = config.speaking_rate
            if speed:
                config.speed = float(speed)

            use_speaker_boost = os.getenv("TTS_ELEVENLABS_USE_SPEAKER_BOOST")
            if use_speaker_boost:
                config.use_speaker_boost = use_speaker_boost.lower() == "true"

        logger.info(
            f"Loaded TTS config: provider={provider.value}, language={config.language}"
        )
        return config

    @staticmethod
    def load_stt_config() -> STTConfig:
        """
        Load STT configuration from environment variables.

        Returns:
            STTConfig: Loaded STT configuration
        """
        provider_name = os.getenv("STT_PROVIDER", "google").lower()

        try:
            provider = STTProvider(provider_name)
        except ValueError:
            logger.warning(
                f"Unknown STT provider '{provider_name}', defaulting to Google"
            )
            provider = STTProvider.GOOGLE

        languages_str = os.getenv("STT_LANGUAGES", "pl-PL")
        languages = [lang.strip() for lang in languages_str.split(",")]

        config = STTConfig(
            provider=provider,
            model=os.getenv(
                "STT_MODEL",
                "latest_long" if provider == STTProvider.GOOGLE else "nova-2",
            ),
            languages=languages,
            punctuate=os.getenv("STT_PUNCTUATE", "false").lower() == "true",
        )

        # Deepgram-specific settings
        if provider == STTProvider.DEEPGRAM:
            smart_format = os.getenv("STT_DEEPGRAM_SMART_FORMAT")
            if smart_format:
                config.smart_format = smart_format.lower() == "true"

            interim_results = os.getenv("STT_DEEPGRAM_INTERIM_RESULTS")
            if interim_results:
                config.interim_results = interim_results.lower() == "true"

        logger.info(
            f"Loaded STT config: provider={provider.value}, model={config.model}"
        )
        return config

    @staticmethod
    def load_llm_config() -> LLMConfig:
        """
        Load LLM configuration from environment variables.

        Returns:
            LLMConfig: Loaded LLM configuration
        """
        provider_name = os.getenv("LLM_PROVIDER", "google").lower()

        try:
            provider = LLMProvider(provider_name)
        except ValueError:
            logger.warning(
                f"Unknown LLM provider '{provider_name}', defaulting to Google"
            )
            provider = LLMProvider.GOOGLE

        # Set default model based on provider
        default_model = (
            "gemini-2.5-flash" if provider == LLMProvider.GOOGLE else "gpt-4o-mini"
        )

        config = LLMConfig(
            provider=provider,
            model=os.getenv("LLM_MODEL", default_model),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            maximum_remote_calls=int(os.getenv("LLM_MAX_REMOTE_CALLS", "100")),
        )

        # OpenAI-specific settings
        if provider == LLMProvider.OPENAI:
            max_tokens = os.getenv("LLM_OPENAI_MAX_TOKENS")
            if max_tokens:
                config.max_tokens = int(max_tokens)

        logger.info(
            f"Loaded LLM config: provider={provider.value}, model={config.model}"
        )
        return config
