import os

from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, mcp, RoomInputOptions
from livekit.plugins import google, silero, noise_cancellation

load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="You are a helpful AI assistant for Homey smart home platform. Use polish language by default. Keep your messages short and concise. Greet the user very shortly."
            "You can help with home automation, device control, and smart home management. "
            "You have access to various tools through MCP servers. The main one is Homey itself. Treat it as a default one. You're operating in Voice mode."
            # "Before executing any MCP tool, always ask for confirmation from the user unless the name of a tool starts with 'list' then execute it without confirmation."
            # "Use Knowledge Graph MCP Server for memory retrieval and storage."
            # """Follow these steps for each interaction:
            # 1. User Identification:
            #    - You should assume that you are interacting with default_user
            #    - If you have not identified default_user, proactively try to do so.
            # 2. Memory Retrieval:
            #    - Retrieve all relevant information from your knowledge graph
            #    - Always refer to your knowledge graph as your "memory"
            # 3. Memory
            #    - While conversing with the user, be attentive to any new information that falls into these categories:
            #      a) Basic Identity (age, gender, name)
            #      c) Preferences (communication style, preferred language, etc.)
            #      d) Aliases for Homey entities used by the user
            # 4. Homey items
            #    - While conversing with the user, be attentive to any new information that falls into these categories:
            #      a) Homey zones
            #      b) Homey devices
            #      c) Homey alternate names for devices, rooms, zones etc.
            # 4. Memory Update:
            #    - If any new information was gathered during the interaction, update your memory as follows:
            #      a) Create entities for recurring people
            #      b) Create entities for Homey zones, devices and alternate names for devices, rooms, zones etc.
            #      c) Connect them to the current entities using relations
            #      d) Store facts about them as observations"""
        )


def prewarm(proc: agents.JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: agents.JobContext):
    current_location = os.path.dirname(os.path.abspath(__file__))
    memory_path = os.path.join(current_location, "memory.jsonl")
    print(memory_path)
    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        llm=google.beta.realtime.RealtimeModel(
            # model="gemini-2.5-flash-preview-native-audio-dialog",
            model="gemini-2.0-flash-live-001",
            voice="Puck",
            temperature=0.7,
        ),
        mcp_servers=[
            mcp.MCPServerHTTP("http://localhost:4445/mcp/"),
            mcp.MCPServerStdio(
                "npx",
                ["-y", "mcp-knowledge-graph", "--memory-path", memory_path],
            ),
        ],
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
        instructions="Greet the user and offer your assistance. Use a friendly tone and Polish by default."
    )


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm)
    )
