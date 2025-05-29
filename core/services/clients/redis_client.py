import logging

import redis.asyncio as redis

logger = logging.getLogger(__name__)

redis_client = redis.Redis(
    host='127.0.0.1',
    port=6379,
    decode_responses=True
)


async def init_redis():
    """
    Проверяет соединение с Redis.
    """
    try:
        pong = await redis_client.ping()
        if pong:
            logger.info("✅ Redis connected successfully")
        else:
            logger.error("❌ Redis ping failed — no response")
    except Exception as e:
        logger.error("❌ Redis connection failed", exc_info=e)
