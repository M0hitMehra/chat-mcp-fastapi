from datetime import datetime, timezone

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class Message(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    user_id: ObjectId
    thread_id: str
    role: MessageRole
    content: str

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    SYSTEM = "system"


