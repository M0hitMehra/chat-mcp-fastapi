from datetime import datetime, timezone

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field
from schemas import MCPServer
from typing import Optional


class Summary(BaseModel):
    thread_id: str

    user_id: ObjectId

    summary: str

    # summarized_message_count: int = 0

    last_summarized_message_id: Optional[ObjectId] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_config = {
        "arbitrary_types_allowed": True,
        "populate_by_name": True,
        "json_encoders": {ObjectId: str},  # Convert ObjectId to string when serializing
    }
