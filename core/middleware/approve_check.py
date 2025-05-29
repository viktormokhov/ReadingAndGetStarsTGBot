# from aiogram import BaseMiddleware
# from aiogram.types import TelegramObject, Message, CallbackQuery
# from typing import Callable, Awaitable, Dict, Any
#
# class ApproveCheckMiddleware(BaseMiddleware):
#     async def __call__(
#         self,
#         handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#         event: TelegramObject,
#         data: Dict[str, Any]
#     ) -> Any:
#         db_user = data.get("db_user")
#         if db_user is None:
#             data["is_approved"] = False
#             return await handler(event, data)
#
#         if not db_user.is_approved:
#             if isinstance(event, Message):
#                 await event.answer("⛔ Доступ только для одобренных пользователей.")
#             elif isinstance(event, CallbackQuery):
#                 await event.answer("⛔ Вы не одобрены.", show_alert=True)
#             return
#
#         # Пользователь одобрен — передаём is_approved=True
#         data["is_approved"] = True
#         return await handler(event, data)
