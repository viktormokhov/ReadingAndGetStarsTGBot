import redis.asyncio as redis
import logging

async def init_redis(app, redis_settings):
    """
    Инициализация Redis клиента и проверка соединения.
    """
    redis_url = redis_settings.redis_url
    redis_client = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    app.state.redis = redis_client

    try:
        pong = await redis_client.ping()
        if pong:
            logging.info("✅ Redis connection established")
        else:
            logging.error("❌ Redis ping failed")
            raise Exception("Redis ping failed")
    except Exception as err:
        logging.error(f"❌ Redis error: {err}")
        raise
    return redis_client


