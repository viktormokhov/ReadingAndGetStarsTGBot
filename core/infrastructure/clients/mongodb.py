import logging

from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


async def init_mongo(app, db_settings):
    """
    Инициализация MongoDB клиента и коллекций.
    """
    mongo_client = AsyncIOMotorClient(db_settings.mongodb_uri)
    app.state.mongo_client = mongo_client
    app.state.db = mongo_client[db_settings.mongodb_name]

    try:
        await app.state.db.command("ping")
        logger.info(f"✅ MongoDB connected to {db_settings.mongodb_name} at {db_settings.mongodb_uri}")
    except Exception as e:
        logger.error("❌ MongoDB connection failed", e)

    await app.state.db["history"].update_one({"_id": "__init__"}, {"$setOnInsert": {}}, upsert=True)
    await app.state.db["quiz_history"].update_one({"_id": "__init__"}, {"$setOnInsert": {}}, upsert=True)

    return mongo_client


# Доступ к базе
def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


# Доступ к коллекциям
def get_history_collection(request: Request):
    return request.app.state.db["history"]


def get_quiz_history_collection(request: Request):
    return request.app.state.db["quiz_history"]
