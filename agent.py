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
    api_key: str, model_name: str, mcp_servers: list[MCPServer], llm_name: str
):

    servers = {}
    print("mcp_servers_mcp_servers", mcp_servers)
    for server in mcp_servers:
        if not server["url"]:
            continue

        config = {
            "transport": "streamable_http",
            "url": server["url"],
        }

        if server.get("token") :
            config["headers"] = {
                "Authorization": f"Bearer {server['token']}"
            }
        print("config+config")
        print(config)
        print(mcp_servers)
        servers[server["name"]] = config

    client = MultiServerMCPClient(servers)

    tools = await client.get_tools()
    
    os.environ["GOOGLE_API_KEY"] = api_key
    model = ChatGoogleGenerativeAI(
                model=model_name,
            )

    # if llm_name.lower() == "gemini":
    #     os.environ["GOOGLE_API_KEY"] = api_key
    #     model = ChatGoogleGenerativeAI(
    #         model=model_name,
    #     )
    # elif llm_name.lower() == "groq":
    #     os.environ["GROQ_API_KEY"] = api_key
    #     model = ChatXAI(model="grok-3-mini" )
    # elif llm_name.lower() == "openai":
    #     os.environ["OPENAI_API_KEY"] = api_key
    #     model = ChatOpenAI(model="gpt-5" )

    agent = create_agent(
        model,
        tools,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent
