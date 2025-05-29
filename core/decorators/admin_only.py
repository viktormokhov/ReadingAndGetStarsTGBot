from functools import wraps
from typing import Callable, Any
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

def admin_only():
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Попытка достать FSMContext из kwargs или args
            state: FSMContext | None = kwargs.get("state")
            if state is None:
                for a in args:
                    if isinstance(a, FSMContext):
                        state = a
                        break

            # Если есть FSMContext и в нём активное состояние — пропускаем проверку админа
            if state:
                current = await state.get_state()
                if current is not None:
                    return await func(*args, **kwargs)

            # Дальше стандартная проверка is_admin
            is_admin = kwargs.get("is_admin")
            if not is_admin:
                event = kwargs.get("call") or kwargs.get("message") or args[0]
                if isinstance(event, CallbackQuery):
                    await event.answer("⛔ Только для администраторов", show_alert=True)
                elif isinstance(event, Message):
                    await event.answer("⛔ Только для администраторов.")
                return

            return await func(*args, **kwargs)

        return wrapper

    return decorator
