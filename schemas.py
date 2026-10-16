from pydantic import BaseModel, Field
from typing import List, Optional,Literal


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
    

class CompanySearchResult(BaseModel):
    companyName: str = Field(..., description="Company / LLP name")
    cin: str = Field(..., description="CIN for companies, LLPIN for LLPs")
    type: Literal["COMPANY", "LLP"] | str =None
    status: Optional[str] = None
    rocCode: Optional[str] = None
    prevCompanyName: Optional[str] = None


class CompanySearchResponse(BaseModel):
    query: str
    results: list[CompanySearchResult]

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
