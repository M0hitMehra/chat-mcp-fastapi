from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import SummarizationMiddleware

from schemas import MCPServer

import os


async def create_chat_agent(
    api_key: str,
    model_name: str,
    mcp_servers: list[MCPServer],
):
    """
    Creates a LangChain Agent dynamically.

    Parameters
    ----------
    api_key : Gemini API Key

    model_name : Gemini model

    mcp_servers : List of MCP servers

    Returns
    -------
    LangChain Agent
    """

    # ---------------------------------
    # Gemini API Key
    # ---------------------------------

    os.environ["GOOGLE_API_KEY"] = api_key

    # ---------------------------------
    # Convert MCP Servers
    # ---------------------------------

    servers = {}

    for server in mcp_servers:

        servers[server.name] = {
            "transport": "streamable-http",
            "url": server.url,
        }

    # ---------------------------------
    # Create MCP Client
    # ---------------------------------

    client = MultiServerMCPClient(servers)

    # ---------------------------------
    # Fetch Tools
    # ---------------------------------

    tools = await client.get_tools()

    # ---------------------------------
    # Gemini Model
    # ---------------------------------

    model = ChatGoogleGenerativeAI(
        model=model_name,
    )

    # ---------------------------------
    # Agent
    # ---------------------------------

    agent = create_agent(
        model,
        tools,
        checkpointer=InMemorySaver(),
        middleware=[
            SummarizationMiddleware(
                model=f"google_genai:{model_name}",
                trigger=("messages", 50),
                keep=("messages", 10),
            )
        ],
    )

    return agent