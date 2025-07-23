"""
Main application entry point for Homey Assistant Agent.

This module provides the main entry point for the LiveKit voice agent
that integrates with Homey smart home platform through MCP servers.
"""

import logging

from dotenv import load_dotenv
from livekit import agents
from livekit.plugins import silero

from homey_assistant.config.mcp_config import MCPConfigLoader, MCPConfigurationError
from homey_assistant.agent.assistant import HomeyAssistant
from homey_assistant.agent.session import SessionManager
from homey_assistant.config.constants import DEFAULT_GREETING_INSTRUCTIONS
from homey_assistant.utils.logging import setup_logging

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)


def prewarm(proc: agents.JobProcess) -> None:
    """
    Prewarm function for agent initialization.
    
    This function is called during agent startup to preload resources
    and configurations that will be used during agent execution.
    
    Args:
        proc: The job process instance to store preloaded data
    """
    try:
        logger.info("Starting agent prewarm process")
        
        # Load VAD (Voice Activity Detection) model
        logger.debug("Loading VAD model")
        proc.userdata["vad"] = silero.VAD.load()
        logger.debug("VAD model loaded successfully")
        
        # Load MCP server configurations
        logger.debug("Loading MCP server configurations")
        config_loader = MCPConfigLoader()
        try:
            mcp_servers = config_loader.load_servers()
            proc.userdata["mcp_servers"] = mcp_servers
            logger.info(f"Loaded {len(mcp_servers)} MCP servers")
        except MCPConfigurationError as e:
            logger.error(f"MCP configuration error: {e}")
            proc.userdata["mcp_servers"] = []
        except Exception as e:
            logger.error(f"Unexpected error loading MCP servers: {e}")
            proc.userdata["mcp_servers"] = []
        
        logger.info("Agent prewarm completed successfully")
        
    except Exception as e:
        logger.error(f"Error during agent prewarm: {e}")
        # Set defaults to ensure agent can still start
        proc.userdata["vad"] = None
        proc.userdata["mcp_servers"] = []


async def entrypoint(ctx: agents.JobContext) -> None:
    """
    Main entrypoint for the LiveKit agent.
    
    This function is called when a new agent session is created.
    It sets up the agent session with all necessary components
    and starts the interaction with the user.
    
    Args:
        ctx: The job context containing room and process information
    """
    try:
        logger.info("Starting agent entrypoint")
        
        # Get preloaded data from prewarm
        mcp_servers = ctx.proc.userdata.get("mcp_servers", [])
        vad = ctx.proc.userdata.get("vad")
        
        logger.info(f"Creating session with {len(mcp_servers)} MCP servers")
        
        # Create session manager and agent session
        session_manager = SessionManager()
        session = session_manager.create_session(mcp_servers=mcp_servers, vad=vad)
        
        # Create room input options
        room_input_options = session_manager.create_room_input_options()
        
        # Create assistant agent
        assistant = HomeyAssistant()
        
        # Start the agent session
        logger.info("Starting agent session")
        await session.start(
            room=ctx.room,
            agent=assistant,
            room_input_options=room_input_options,
        )
        
        # Connect to the room
        logger.info("Connecting to room")
        await ctx.connect()
        
        # Generate initial greeting
        logger.info("Generating initial greeting")
        await session.generate_reply(instructions=DEFAULT_GREETING_INSTRUCTIONS)
        
        logger.info("Agent session started successfully")
        
    except Exception as e:
        logger.error(f"Error in agent entrypoint: {e}")
        raise


def main() -> None:
    """
    Main application entry point.
    
    Sets up logging and starts the LiveKit agent with the configured
    entrypoint and prewarm functions.
    """
    try:
        # Set up application logging
        setup_logging()
        logger.info("Starting Homey Assistant Agent")
        
        # Run the LiveKit agent
        agents.cli.run_app(
            agents.WorkerOptions(
                entrypoint_fnc=entrypoint,
                prewarm_fnc=prewarm,
            )
        )
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise


if __name__ == "__main__":
    main()
