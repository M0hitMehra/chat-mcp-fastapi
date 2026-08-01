from pydantic import BaseModel
from typing import List


class MCPServer(BaseModel):
    name: str
    url: str


class ConnectRequest(BaseModel):
    api_key: str
    model: str = "gemini-3.1-flash-lite"
    thread_id: str = "default"
    mcp_servers: List[MCPServer]


class ConnectResponse(BaseModel):
    session_id: str


class ChatRequest(BaseModel):
    session_id: str
    message: str
