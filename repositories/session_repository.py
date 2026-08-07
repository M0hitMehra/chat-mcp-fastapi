from core.database import db
from bson import ObjectId

class SessionRepository:

    def __init__(self):
        self.collection = db["MCP_CHAT_SESSIONS"]

    async def create(self, session: dict):
        return await self.collection.insert_one(session)

    async def find_by_session_id(
        self,
        session_id: str,
    ):
        return await self.collection.find_one(
            {
                "session_id": session_id,
            }
        )

    async def find_by_user_id(
        self,
        user_id: str,
    ):
        cursor = self.collection.find(
            {
                "user_id": user_id,
            }
        ).sort("updated_at", -1)

        return await cursor.to_list(length=100)

    async def find_user_session(
        self,
        session_id: str,
        user_id: ObjectId,
    ):
        return await self.collection.find_one(
            {
                "session_id": session_id,
                "user_id": ObjectId(user_id),
            }
        )

    async def delete(
        self,
        session_id: str,
        user_id: str,
    ):
        return await self.collection.delete_one(
            {
                "session_id": session_id,
                "user_id": user_id,
            }
        )
