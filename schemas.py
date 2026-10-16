from pydantic import BaseModel, Field
from typing import List, Optional


class MCPCred(BaseModel):
    username:str|None=None
    password:str|None=None
    apiKey:str|None=None
    token:str|None=None
    

class MCPServer(BaseModel):
    name: str
    url: str
    auth:MCPCred|None =None
    token:str|None= None


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
    
class CompanySelection(BaseModel):
    companyName: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Name of the Indian company to look up",
    )
    apiKey: str = Field(..., min_length=10, description="API key for the LLM provider")


class CompanyCINResponse(BaseModel):
    companyName: str = Field(..., description="Company name as provided by the user")
    cin: str | None = Field(
        None,
        description="CIN or LLPIN returned by the tool. Null if the tool found no match.",
    )

class User(BaseModel):
    username: str
    email: str
    password: str


class UserRegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class UserLoginRequest(BaseModel):
    email: str ="string@string.com"
    password: str ="string"


class CreateThreadRequest(BaseModel):
    session_id: str
    model_name: str = "gemini-3.1-flash-lite"
    apiKey: str
    mcp_servers: list[MCPServer]
    
    
class CreatePitchThreadRequest(BaseModel):
        session_id: str
        model_name: str = "gemini-3.1-flash-lite"
        apiKey: str
        mcp_servers: list[MCPServer]
        thread_type: str|None="PITCH"
        pitch_info:PitchInfo|None= None
        
        
class PitchInfo(BaseModel):
        pitch_type:str|None="COMPANY"
        cin:str
        contact:str|None = None
        email:str|None = None
        phone:str|None = None
        pitch_description:str|None = None
        companyName:str|None=None



class UpdateThreadConfigRequest(BaseModel):
    api_key: str | None = None
    model_name: str | None = None
    mcp_servers: list[MCPServer] | None = None
    thread_name: str = "New Chat"
