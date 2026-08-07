from datetime import datetime, timezone

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field
from schemas import MCPServer
from typing import Optional


class Thread(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    api_key: str
    thread_name: str
    user_id: ObjectId
    session_id: ObjectId
    thread_id: str
    model_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    mcpServers: Optional[list[MCPServer]]
