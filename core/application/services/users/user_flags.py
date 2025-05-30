from redis.asyncio import Redis

from config.constants import ACTIVE_QUESTION_KEY, BLOCK_MSG_KEY

GENERATING_FLAG = "users:{user_id}:is_generating_{kind}"  # kind: card, text, image, ...

async def set_generating(redis: Redis, user_id: int, kind: str):
    await redis.set(GENERATING_FLAG.format(user_id=user_id, kind=kind), "1", ex=600)

async def clear_generating(redis: Redis, user_id: int, kind: str):
    await redis.delete(GENERATING_FLAG.format(user_id=user_id, kind=kind))

async def is_generating(redis: Redis, user_id: int, kind: str) -> bool:
    return await redis.exists(GENERATING_FLAG.format(user_id=user_id, kind=kind)) > 0

async def has_active_question(redis, user_id: int) -> bool:
    return bool(await redis.get(ACTIVE_QUESTION_KEY.format(user_id=user_id)))

async def get_generating_status(redis: Redis, user_id: int):
    # Вернёт строку статуса, если какой-то из известных флагов установлен
    for kind in ["text", "card", "read"]:
        if await is_generating(redis, user_id, kind=kind):
            return kind
    return None


async def delete_blocking_message(redis, user_id, bot, chat_id):
    key = BLOCK_MSG_KEY.format(user_id=user_id)
    msg_id = await redis.get(key)
    if msg_id:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=int(msg_id))
        except Exception:
            pass
        await redis.delete(key)