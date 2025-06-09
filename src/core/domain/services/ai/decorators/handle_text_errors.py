import asyncio
import functools
import logging

import httpx
import openai

from config.constants import MAX_RETRIES, BACKOFF_BASE_SECONDS
from core.infrastructure.clients.redis_client import rc as redis_client

logger = logging.getLogger(__name__)

async def clear_user_redis_client_keys(redis_client, user_id):
    keys = [f"user:{user_id}:has_active_question", f"user:{user_id}:is_generating_text"]
    await redis_client.delete(*keys)

def handle_text_errors(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        self = args[0] if args else None
        user_id = getattr(self, 'uid', None)
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                result = await func(*args, **kwargs)
                # Удаляем ключ после успешного выполнения
                if redis_client.redis_client and user_id:
                    await clear_user_redis_client_keys(redis_client, user_id)
                return result
            except (
                openai.APIConnectionError,
                openai.RateLimitError,
                openai.APIStatusError,
                openai.APITimeoutError,
            ) as exc:
                # Сбросить ключи при ошибке
                if redis_client.redis_client and user_id:
                    await clear_user_redis_client_keys(redis_client, user_id)
                if attempt == MAX_RETRIES:
                    raise RuntimeError(f"Text generation failed after {MAX_RETRIES} attempts: {exc}") from exc
                await asyncio.sleep(BACKOFF_BASE_SECONDS * 2 ** (attempt - 1))
            except httpx.HTTPStatusError as exc:
                logger.error(f"Ошибка 404 или иная HTTP-ошибка: {exc}")
                if redis_client and user_id:
                    await clear_user_redis_client_keys(redis_client, user_id)
                raise RuntimeError("❗️Произошла ошибка при генерации текста. Попробуйте ещё раз через пару минут!")
            except Exception as exc:
                logger.error(f"Ошибка при генерации текста: {exc}")
                if redis_client and user_id:
                    await clear_user_redis_client_keys(redis_client, user_id)
                raise RuntimeError("❗️Что-то пошло не так. Попробуйте позже.")
        return None
    return wrapper
