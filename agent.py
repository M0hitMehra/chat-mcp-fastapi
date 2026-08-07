from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from langgraph.checkpoint.memory import InMemorySaver 
from langchain.agents.middleware import SummarizationMiddleware 

from schemas import MCPServer
from response_schemas import SYSTEM_PROMPT
import os


from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class State(TypedDict):

    messages: Annotated[list, add_messages]

    needs_human: bool

    verification_reason: str


async def create_chat_agent(
    api_key: str,
    model_name: str,
    mcp_servers: list[MCPServer],
):
   
    os.environ["GOOGLE_API_KEY"] = api_key
    servers = {}
    print("mcp_servers_mcp_servers",mcp_servers)
    for server in mcp_servers:
        if not  server["url"] :
            continue
        servers[server["name"]] = {
            "transport": "streamable-http",
            "url": server["url"],
        }

    client = MultiServerMCPClient(servers)

    tools = await client.get_tools()

    model = ChatGoogleGenerativeAI(
        model=model_name,
    )

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
        system_prompt=SYSTEM_PROMPT,
    )

    return agent
