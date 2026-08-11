from bson import ObjectId

from core.database import db
from models.summary import Summary


class SummaryRepository:
    def __init__(self):
        self.collection = db["MCP_THREAD_SUMMARY"]

    async def find_by_thread(
        self,
        thread_id: str,
        user_id: ObjectId,
    ):
        
        print("thread_id-user_id",thread_id,user_id)
        return await self.collection.find_one(
            {
                "thread_id": thread_id,
                "user_id": ObjectId(user_id),
            }
        )

    async def create(self, summary: Summary):
        return await self.collection.insert_one(summary)

    async def update(
        self,
        thread_id: str,
        user_id: ObjectId,
        data: dict,
    ):
        return await self.collection.update_one(
            {
                "thread_id": thread_id,
                "user_id": user_id,
            },
            {"$set": data},
        )
