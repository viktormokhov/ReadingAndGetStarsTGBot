import logging

from motor.motor_asyncio import AsyncIOMotorClient

from core.config import db_settings

logger = logging.getLogger(__name__)

_client = AsyncIOMotorClient(db_settings.mongodb_uri)
db = _client[db_settings.mongodb_name]
history_collection = db["history"]

async def init_mongo():
    """Проверяет соединение с MongoDB."""
    try:
        await db.command("ping")
        logger.info(f"✅ MongoDB connected to {db_settings.mongodb_name} at {db_settings.mongodb_uri}")
    except Exception as e:
        logger.error("❌ MongoDB connection failed", exc_info=e)


async def ensure_collections():
    """Гарантирует существование коллекций в MongoDB."""
    await db["history"].update_one({"_id": "__init__"}, {"$setOnInsert": {}}, upsert=True)
