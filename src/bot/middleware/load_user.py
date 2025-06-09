# from aiogram import BaseMiddleware
# from aiogram.types import TelegramObject
# from typing import Callable, Awaitable, Dict, Any
# from core.db.session import Session
# from core.db.models import User
#
#
# class LoadUserMiddleware(BaseMiddleware):
#     async def __call__(
#         self,
#         handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#         event: TelegramObject,
#         data: Dict[str, Any]
#     ) -> Any:
#         users = data.get("event_from_user")
#         if users:
#             async with Session() as s:
#                 db_user = await s.get(User, users.id)
#                 data["db_user"] = db_user
#         return await handler(event, data)
