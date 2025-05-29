from functools import wraps
from typing import Callable, Any
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from core.database.init_db import AsyncSessionLocal
from core.database.init_db import User

def is_approved_user():
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 1) Ищем FSMContext среди аргументов
            state: FSMContext | None = kwargs.get("state")
            if state is None:
                for a in args:
                    if isinstance(a, FSMContext):
                        state = a
                        break

            # Если во время регистрации — пропускаем проверку
            if state:
                current = await state.get_state()
                if current is not None:
                    return await func(*args, **kwargs)

            # 2) Находим Message или CallbackQuery, чтобы взять from_user.id
            event = kwargs.get("call") or kwargs.get("message") or args[0]
            user_id = None
            if isinstance(event, Message):
                user_id = event.from_user.id
            elif isinstance(event, CallbackQuery):
                user_id = event.from_user.id

            # Если не получилось найти user_id — разрешаем проход
            if user_id is None:
                return await func(*args, **kwargs)

            # 3) Читаем из БД актуальную запись users.is_approved
            async with AsyncSessionLocal.begin() as session:
                user = await session.get(User, user_id)

            if not user or not user.is_approved:
                # отказ
                if isinstance(event, CallbackQuery):
                    await event.answer(
                        "⛔ Доступ только для подтвержденных пользователей",
                        show_alert=True
                    )
                else:  # Message
                    await event.answer(
                        "⛔ Доступ только для подтвержденных пользователей."
                    )
                return

            # всё ок
            return await func(*args, **kwargs)

        return wrapper
    return decorator
