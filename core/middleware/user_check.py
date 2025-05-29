from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Awaitable, Dict, Any

from async_lru import alru_cache

from core.database.models import User
from core.database.init_db import AsyncSessionLocal


class UserCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = data.get("event_from_user")
        data["is_approved"] = await self.is_approved(user.id) if user else False
        return await handler(event, data)

    @alru_cache(maxsize=1024)
    async def is_approved(self, user_id: int) -> bool:
        async with AsyncSessionLocal() as s:
            user = await s.get(User, user_id)
            return user and user.is_approved
