from typing import Callable, Any

from aiogram import BaseMiddleware
from async_lru import alru_cache

from core.infrastructure.database.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository


class AdminMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable,
            event: Any,
            data: dict[str, Any]
    ) -> Any:
        # Получаем user_id
        user_id = None
        if hasattr(event, "from_user"):
            user_id = event.from_user.id
        elif hasattr(event, "message") and hasattr(event.message, "from_user"):
            user_id = event.message.from_user.id

        is_admin = False
        user = data.get("event_from_user")
        if user_id:
            is_admin = await self.is_admin(user_id) if user else False

        data["is_admin"] = is_admin

        return await handler(event, data)

    @alru_cache(maxsize=1024)
    async def is_admin(self, user_id: int) -> bool:
        async with SQLAlchemyUserRepository() as repo:
            user = await repo.get_by_id(user_id)
            return user.is_admin
