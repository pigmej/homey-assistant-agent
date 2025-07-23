# Provider Configuration Guide

The Homey Assistant Agent supports multiple configurable providers for TTS (Text-to-Speech), STT (Speech-to-Text), and LLM (Large Language Model) services. This guide explains how to configure and use different providers.

## Supported Providers

### TTS (Text-to-Speech) Providers

1. **Google TTS** (`google`) - Default
   - High-quality neural voices
   - Multiple language support
   - Configurable voice gender and speaking rate

2. **ElevenLabs TTS** (`elevenlabs`)
   - Premium AI voice synthesis
   - Custom voice cloning
   - Advanced voice settings (stability, similarity boost, style, speed)

### STT (Speech-to-Text) Providers

1. **Google STT** (`google`) - Default
   - Accurate speech recognition
   - Multiple language support
   - Punctuation and formatting options

2. **Deepgram STT** (`deepgram`)
   - Fast real-time transcription
   - Smart formatting
   - Interim results support

### LLM (Large Language Model) Providers

1. **Google Gemini** (`google`) - Default
   - Latest Gemini models
   - Function calling support
   - Optimized for conversational AI

2. **OpenAI** (`openai`)
   - GPT-4 and GPT-3.5 models
   - Reliable performance
   - Configurable token limits

## Configuration

### Environment Variables

Configure providers using environment variables in your `.env` file. See `.env.example` for a comprehensive configuration template with detailed explanations:

```bash
# TTS Configuration
TTS_PROVIDER=elevenlabs  # or google
TTS_LANGUAGE=pl-PL
TTS_SPEAKING_RATE=1.15

# ElevenLabs specific
ELEVEN_API_KEY=your_api_key
TTS_ELEVENLABS_VOICE_ID=your_voice_id
TTS_ELEVENLABS_MODEL_ID=eleven_multilingual_v2

# STT Configuration
STT_PROVIDER=deepgram  # or google
STT_LANGUAGES=pl-PL
STT_PUNCTUATE=true

# Deepgram specific
DEEPGRAM_API_KEY=your_api_key
STT_DEEPGRAM_SMART_FORMAT=true

# LLM Configuration
LLM_PROVIDER=openai  # or google
LLM_TEMPERATURE=0.7
LLM_MAX_REMOTE_CALLS=100

# OpenAI specific
OPENAI_API_KEY=your_api_key
LLM_MODEL=gpt-4o-mini
```

### API Keys Required

Make sure to set up the required API keys for your chosen providers:

- **Google Services**: Set `GOOGLE_APPLICATION_CREDENTIALS` to your service account JSON file path
- **ElevenLabs**: Set `ELEVEN_API_KEY` with your ElevenLabs API key
- **Deepgram**: Set `DEEPGRAM_API_KEY` with your Deepgram API key
- **OpenAI**: Set `OPENAI_API_KEY` with your OpenAI API key

## Usage Examples

### Using ElevenLabs TTS

```bash
# Set provider to ElevenLabs
TTS_PROVIDER=elevenlabs
ELEVEN_API_KEY=sk-your-api-key
TTS_ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
TTS_ELEVENLABS_STABILITY=0.5
TTS_ELEVENLABS_SIMILARITY_BOOST=0.75
```

### Using Deepgram STT

```bash
# Set provider to Deepgram
STT_PROVIDER=deepgram
DEEPGRAM_API_KEY=your-deepgram-api-key
STT_MODEL=nova-2
STT_DEEPGRAM_SMART_FORMAT=true
```

### Using OpenAI LLM

```bash
# Set provider to OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key
LLM_MODEL=gpt-4o-mini
LLM_OPENAI_MAX_TOKENS=4096
```

## Testing Configuration

Run the provider test script to verify your configuration:

```bash
python test_providers.py
```

This will show your current provider settings and verify that the configuration system is working correctly.

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all required LiveKit plugins are installed:
   ```bash
   uv sync
   ```

2. **API Key Issues**: Verify your API keys are correctly set and have the necessary permissions.

3. **Model Not Found**: Check that the specified model names are correct for your chosen provider.

### Logging

Enable debug logging to see detailed provider initialization:

```bash
LOG_LEVEL=DEBUG
```

## Advanced Configuration

### Programmatic Configuration

You can also configure providers programmatically:

```python
from homey_assistant.config.providers import (
    TTSConfig, STTConfig, LLMConfig,
    TTSProvider, STTProvider, LLMProvider,
    ProviderFactory
)

# Create custom TTS config
tts_config = TTSConfig(
    provider=TTSProvider.ELEVENLABS,
    language="en-US",
    voice_id="your_voice_id"
)

# Create TTS instance
tts = ProviderFactory.create_tts(tts_config)
```

### Custom Provider Settings

Each provider supports specific settings. Refer to the provider documentation for advanced configuration options:

- [Google Cloud Speech](https://cloud.google.com/speech-to-text/docs)
- [ElevenLabs API](https://elevenlabs.io/docs)
- [Deepgram API](https://developers.deepgram.com/)
- [OpenAI API](https://platform.openai.com/docs)