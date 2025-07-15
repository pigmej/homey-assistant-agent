import os
import json
from typing import List, Dict, Any

from dotenv import load_dotenv

from livekit import agents, api
from livekit.agents import AgentSession, Agent, mcp, RoomInputOptions
from livekit.plugins import google, silero, noise_cancellation

load_dotenv()


def load_mcp_servers_from_json(config_path: str) -> List[mcp.MCPServer]:
    """Load MCP server configurations from JSON file and return list of MCP server instances."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"MCP configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        config = json.load(f)

    servers = []

    for server_config in config.get("servers", []):
        server_type = server_config.get("type")

        if server_type == "http":
            url = server_config.get("url")
            if url:
                servers.append(mcp.MCPServerHTTP(url))

        elif server_type == "stdio":
            command = server_config.get("command")
            args = server_config.get("args", [])
            if command:
                servers.append(mcp.MCPServerStdio(command, args))

    return servers


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="You are a helpful AI assistant for Homey smart home platform. Use polish language by default. Keep your messages short and concise. Greet the user very shortly. Welcome user just with 'Hey'"
            "You can help with home automation, device control, and smart home management. "
            "You have access to various tools through MCP servers. The main one is Homey itself. Treat it as a default one. You're operating in Voice mode."
            "Before executing any MCP tool, always ask for confirmation from the user unless the name of a tool starts with 'list' or 'search' then execute it without confirmation."
            "Use Knowledge Graph MCP Server for memory retrieval and storage."
            """Follow these steps for each interaction:
            1. User Identification:
               - You should assume that you are interacting with default_user
               - If you have not identified default_user, proactively try to do so.
            2. Memory Retrieval:
               - Retrieve all relevant information from your knowledge graph
               - Always refer to your knowledge graph as your "memory"
            3. Memory
               - While conversing with the user, be attentive to any new information that falls into these categories:
                 a) Basic Identity (age, gender, name)
                 c) Preferences (communication style, preferred language, etc.)
                 d) Aliases for Homey entities used by the user
            4. Homey items
               - While conversing with the user, be attentive to any new information that falls into these categories:
                 a) Homey zones
                 b) Homey devices
                 c) Homey alternate names for devices, rooms, zones etc.
            4. Memory Update:
               - If any new information was gathered during the interaction, update your memory as follows:
                 a) Create entities for recurring people
                 b) Create entities for Homey zones, devices and alternate names for devices, rooms, zones etc.
                 c) Connect them to the current entities using relations
                 d) Store facts about them as observations"""
        )


def prewarm(proc: agents.JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

    if os.path.exists("mcp.json"):
        mcp_servers = load_mcp_servers_from_json("mcp.json")
    else:
        mcp_servers = []
    proc.userdata["mcp_servers"] = mcp_servers


async def entrypoint(ctx: agents.JobContext):
    mcp_servers = ctx.proc.userdata["mcp_servers"]

    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt=google.STT(model="latest_long", languages=["pl-PL"], punctuate=False),
        tts=google.TTS(
            gender="female", voice_name="pl-PL-Chirp3-HD-Despina", language="pl-PL"
        ),
        llm=google.LLM(model="gemini-2.5-flash", temperature=0.7),
        mcp_servers=mcp_servers,
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            video_enabled=False,
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    await session.generate_reply(
        instructions="Greet the user with 'Hey'. Use a friendly tone and Polish by default."
    )


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        )
    )
