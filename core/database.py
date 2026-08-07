from pymongo import AsyncMongoClient

from core.config import settings


client = AsyncMongoClient(settings.MONGO_URI)

db = client[settings.DATABASE_NAME]