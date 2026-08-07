from bson import ObjectId

from core.database import db


class UserRepository:

    def __init__(self):

        self.collection = db["MCP_USERS"]

    async def create(self, user: dict):

        return await self.collection.insert_one(user)

    async def find_by_email(self, email: str):

        return await self.collection.find_one({"email": email})

    async def find_by_id(self, user_id: str):

        return await self.collection.find_one({"_id": ObjectId(user_id)})

    async def update(self, user_id: str, data: dict):

        return await self.collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": data}
        )

    async def delete(self, user_id: str):

        return await self.collection.delete_one({"_id": ObjectId(user_id)})
