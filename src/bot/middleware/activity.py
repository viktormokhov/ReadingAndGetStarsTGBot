from datetime import datetime, timezone
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from core.infrastructure.db.connection import AsyncSessionLocal
from core.infrastructure.db.models import User


class LastActiveMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user = data.get("event_from_user")
        if user:
            async with AsyncSessionLocal.begin() as session:
                db_user = await session.get(User, user.id)
                if db_user:
                    now = datetime.now(timezone.utc)
                    if not db_user.first_active:
                        db_user.first_active = now
                    db_user.last_active = now
        return await handler(event, data)
