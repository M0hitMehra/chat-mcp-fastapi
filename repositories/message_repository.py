from bson import ObjectId

from core.database import db

from typing import Optional


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

    async def find_recent_messages(
        self,
        thread_id,
        user_id: ObjectId,
        limit=50,
    ):
        cursor = (
            await self.collection.find(
                thread_id=thread_id,
                user_id=ObjectId(user_id),
            )
            .sort("created_at", -1)
            .limit(limit)
        )
        return cursor.reverse()

    async def find_messages_after_summary(
        self,
        thread_id: str,
        user_id: str,
        last_message_id: Optional[ObjectId] = None,
    ):
        if last_message_id:
            
            cursor = self.collection.find(
                {
                    "thread_id": thread_id,
                    "user_id": ObjectId(user_id),
                    "_id": {"$gt": ObjectId(last_message_id)},
                }
            ).sort("_id", 1)

            return await cursor.to_list(None)
        
        cursor = self.collection.find(
                {
                    "thread_id": thread_id,
                    "user_id": ObjectId(user_id),
                }
            ).sort("_id", 1)

        return await cursor.to_list(None)
        

    async def find_messages_before_summary(
        self,
        thread_id: str,
        user_id: str,
        last_message_id: ObjectId,
    ):
        cursor = self.collection.find(
            {
                "thread_id": thread_id,
                "user_id": ObjectId(user_id),
                "_id": {"$gt": last_message_id},
            }
        ).sort("_id", -1).limit(50)

        return await cursor.to_list(None)
