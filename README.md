# Homey Assistant Agent

A LiveKit voice agent that integrates with the Homey smart home platform through MCP (Model Context Protocol) servers.

## Project Overview

The Homey Assistant Agent is a voice-enabled AI assistant designed to help users control and manage their Homey smart home devices through natural language interactions. The agent uses LiveKit for real-time audio communication, Google's speech-to-text and text-to-speech services, and integrates with Homey through MCP servers.

This is meant to be used with https://github.com/pigmej/homey-assistant-nextjs which does not differ much from livekit example.

## Project Structure

```
homey_assistant/
├── __init__.py
├── agent/
│   ├── __init__.py
│   ├── assistant.py        # HomeyAssistant agent class
│   └── session.py          # Agent session management
├── config/
│   ├── __init__.py
│   ├── constants.py        # Application constants
│   └── mcp_config.py       # MCP server configuration loading
└── utils/
    ├── __init__.py
    └── logging.py          # Logging utilities
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Node.js and npm (for MCP servers)
- LiveKit account (for voice communication)
- Google Cloud account (for STT and TTS services)
  - Technically that would work with ANY SST/TTS or Live model BUT all others are super expensive.
  - I had the best results with OpenAI Realtime models.

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd homey-assistant-agent
   ```

2. Install dependencies:
   ```bash
   pip install uv
   uv sync
   ```

3. Create a `.env` file with your API keys and configuration:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret
   ```

4. Create an MCP configuration file (`mcp.json`):
   ```json
   {
     "servers": {
       "homey": {
         "type": "http",
         "url": "http://your-homey-mcp-server-url/mcp/"
       },
     }
   }
   ```

## Usage

### Running the Agent

```bash
python main.py
```

### Docker

You can also run the agent using Docker:

```bash
docker-compose up
```

Or build and run the Docker image directly:

```bash
docker build -t homey-assistant-agent .
docker run -v ./mcp.json:/app/mcp.json:ro -v ./.env:/app/.env:ro homey-assistant-agent
```

## Configuration Options

### MCP Configuration

The MCP configuration file (`mcp.json`) defines the MCP servers that the agent will connect to. Each server can be one of two types:

- **HTTP Server**: Connects to an MCP server over HTTP
  ```json
  {
    "type": "http",
    "url": "http://server-url/mcp/"
  }
  ```

- **Stdio Server**: Spawns a local process and communicates with it over standard I/O
  ```json
  {
    "type": "stdio",
    "command": "command-to-run",
    "args": ["arg1", "arg2"]
  }
  ```

### Agent Configuration

The agent behavior can be configured through environment variables or by modifying the constants in `homey_assistant/config/constants.py`:

- `MAX_TOOL_STEPS`: Maximum number of consecutive MCP tool calls (default: 20) - helpfull to raise when you expect a lot of calls to tools (ie get all zones temps etc)
- `TEMPERATURE`: LLM temperature parameter (default: 0.7) - less randomness
- `SPEAKING_RATE`: TTS speaking rate (default: 1.15) - 15% faster basically
- `LANGUAGE`: Default language code (default: "pl-PL") - I wanted polish :)
- `VOICE_NAME`: TTS voice name (default: "pl-PL-Chirp3-HD-Despina") - best (?) polish voice on Gemini

## Development

### Running Tests

```bash
pytest
```

### Adding New Features

1. Update the requirements and design documents
2. Implement the changes following the project structure
3. Add appropriate tests
4. Update documentation

## License

[License information]