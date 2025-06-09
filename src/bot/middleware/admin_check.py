from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from async_lru import alru_cache

from src.core.infrastructure.database.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository


class AdminCheckMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user = data.get("event_from_user")
        data["is_admin"] = await self.is_admin(user.id) if user else False
        return await handler(event, data)

    @alru_cache(maxsize=1024)
    async def is_admin(self, user_id: int) -> bool:
        async with SQLAlchemyUserRepository() as repo:
            user = await repo.get_by_id(user_id)
            return user and user.is_admin
