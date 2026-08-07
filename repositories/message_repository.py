from bson import ObjectId

from core.database import db


class MessageRepository:

    def __init__(self):
        self.collection = db["MCP_CHAT_MESSAGES"]

    async def create(self, message: dict):
        return await self.collection.insert_one(message)

    async def find_by_thread_id(
        self,
        thread_id: str,
        user_id: str,
        limit: int = 100,
        skip: int = 0,
    ):
        cursor = (
            self.collection.find(
                {
                    "thread_id": thread_id,
                    "user_id": ObjectId(user_id),
                }
            )
            .sort("created_at", 1)
            .skip(skip)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)

    async def delete_by_thread_id(
        self,
        thread_id: str,
        user_id: str,
    ):
        return await self.collection.delete_many(
            {
                "thread_id": thread_id,
                "user_id": ObjectId(user_id),
            }
        )
