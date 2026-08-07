from pydantic import BaseModel
from typing import List, Optional


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
    thread_id: str
    model_name: str


class User(BaseModel):
    username: str
    email: str
    password: str


class UserRegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class UserLoginRequest(BaseModel):
    email: str
    password: str


class CreateThreadRequest(BaseModel):
    session_id: str
    model_name: str = "gemini-3.1-flash-lite"
    apiKey: str
    mcp_servers: list[MCPServer]


class UpdateThreadConfigRequest(BaseModel):
    api_key: str | None = None
    model_name: str | None = None
    mcp_servers: list[MCPServer] | None = None
