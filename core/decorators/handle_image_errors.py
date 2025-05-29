import asyncio
import functools
import logging

import httpx
import openai

from core.constants import MAX_RETRIES, BACKOFF_BASE_SECONDS
from core.services.clients.redis_client import redis_client

logger = logging.getLogger(__name__)

async def clear_user_redis_client_keys(redis_client, user_id):
    # Можно расширить список ключей по вашей логике
    keys = f"user:{user_id}:is_generating_card"
    await redis_client.delete(keys)

def handle_image_errors(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Получаем self и user_id, если они есть
        self = args[0] if args else None
        user_id = getattr(self, 'uid', None)
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return await func(*args, **kwargs)
            except (
                openai.APIConnectionError,
                openai.RateLimitError,
                openai.APIStatusError,
                openai.APITimeoutError,
            ) as exc:
                # Сбросить ключи при ошибке OpenAI
                if redis_client and user_id:
                    await clear_user_redis_client_keys(redis_client, user_id)
                if attempt == MAX_RETRIES:
                    raise RuntimeError(f"Image generation failed after {MAX_RETRIES} attempts: {exc}") from exc
                await asyncio.sleep(BACKOFF_BASE_SECONDS * 2 ** (attempt - 1))
            except httpx.HTTPStatusError as exc:
                logger.error(f"Ошибка генерации изображения (HTTP): {exc}")
                # Сбросить ключи при ошибке HTTP
                if redis_client and user_id:
                    await clear_user_redis_client_keys(redis_client, user_id)
                raise RuntimeError("❗️Произошла ошибка при генерации изображения")
            except Exception as exc:
                logger.error(f"Непредвиденная ошибка генерации изображения: {exc}")
                # Сбросить ключи при неизвестной ошибке
                if redis_client and user_id:
                    await clear_user_redis_client_keys(redis_client, user_id)
                raise RuntimeError("❗️Что-то пошло не так при генерации изображения. Попробуйте позже.")
        return None
    return wrapper
