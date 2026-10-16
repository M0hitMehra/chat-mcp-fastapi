from core.database import db
from bson import ObjectId
from models.PitchThread import PithcThread


def _to_json_safe(doc):
    if doc is None:
        return None
    if isinstance(doc, dict):
        return {
            k: (str(v) if isinstance(v, ObjectId) else _to_json_safe(v))
            for k, v in doc.items()
        }
    if isinstance(doc, list):
        return [_to_json_safe(d) for d in doc]
    return doc

class PitchThreadRepository:

    def __init__(self):
        self.collection = db["MCP_CHAT_PITCH_THREADS"]

    async def create(self, thread: PithcThread):
        return await self.collection.insert_one(thread)

    async def find_by_thread_name(self, thread_name: str, user_id: str):
        return await self.collection.find_one(
            {
                "thread_name": thread_name,
                "user_id": ObjectId(user_id),
            }
        )

    async def find_by_thread_id(
        self,
        thread_id: str,
    ):
        return await self.collection.find_one(
            {
                "thread_id": thread_id,
            }
        )

    async def find_by_user_id(
        self,
        user_id: str,
    ):
        cursor = self.collection.find(
            {
                "user_id": ObjectId(user_id),
            }
        ).sort("updated_at", -1)

        return await cursor.to_list(length=100)
    
    
    async def find_latest_pitch_thread_by_user_id(
            self,
            user_id: str,
        ):
            cursor = self.collection.find(
                        {
                            "user_id": ObjectId(user_id),
                        }
                        ).sort("updated_at", -1)
            data = await cursor.to_list(length=1)
            return _to_json_safe(data[0]) if data else None  ;
            
            
            

    async def find_by_user_id_and_thread_id(self, user_id: str, thread_id: str):
        cursor = self.collection.find_one(
            {
                "user_id": ObjectId(user_id),
                "thread_id": thread_id,
            }
        )

        return await cursor

    async def update_config(
        self,
        user_id: str,
        thread_id: str,
        data: dict,
    ):
        return await self.collection.update_one(
            {
                "user_id": ObjectId(user_id),
                "thread_id": thread_id,
            },
            {"$set": data},
        )
