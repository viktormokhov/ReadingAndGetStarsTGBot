import logging

from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


async def init_mongo(app, db_settings):
    """
    Инициализация MongoDB клиента и коллекций.
    """
    mongo_client = AsyncIOMotorClient(db_settings.mongodb_url)
    app.state.mongo_client = mongo_client
    app.state.db = mongo_client[db_settings.mongodb_name]

    try:
        await app.state.db.command("ping")
        logger.info(f"✅ MongoDB connected to {db_settings.mongodb_name}")
    except Exception as e:
        logger.error("❌ MongoDB connection failed", {e})

    await app.state.db["quiz_questions_history"].update_one({"_id": "__init__"},
                                                            {"$setOnInsert": {}},
                                                            upsert=True)

    return mongo_client


# Доступ к базе
def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


# Доступ к коллекциям
def get_history_collection(request: Request):
    return request.app.state.db["history"]


def get_quiz_history_collection(request: Request):
    return request.app.state.db["quiz_history"]
