from aiogram import BaseMiddleware
from aiogram.types import Message

from core.constants import KIND_TO_MESSAGE, BLOCK_MSG_KEY
from core.services.users.user_flags import get_generating_status


class CommandBlockerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        if event.text and event.text.startswith("/"):
            dispatcher = data["dispatcher"]
            redis = dispatcher["redis"]
            user_id = event.from_user.id
            kind = await get_generating_status(redis, user_id)
            if kind in KIND_TO_MESSAGE:
                key = BLOCK_MSG_KEY.format(user_id=user_id)
                # 1. Удаляем предыдущее сообщение, если есть
                prev_msg_id = await redis.get(key)
                if prev_msg_id:
                    try:
                        await event.bot.delete_message(event.chat.id, int(prev_msg_id))
                    except Exception:
                        pass
                    await redis.delete(key)
                # 2. Отправляем новое сообщение
                sent = await event.answer(KIND_TO_MESSAGE[kind])
                # 3. Сохраняем новое message_id
                await redis.set(key, sent.message_id, ex=60)
                return
        return await handler(event, data)
