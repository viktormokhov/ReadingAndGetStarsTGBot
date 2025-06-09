import functools
from aiogram.types import Message

from src.config.constants import KIND_TO_MESSAGE


def async_with_generating_flag(get_user_id, kind):
    """
    Асинхронный декоратор для работы с Redis-флагом генерации.
    Требует передачи dispatcher через kwargs в функцию.
    get_user_id — функция (lambda), которая по аргументам возвращает user_id.
    kind — тип генерации ('card', 'text', ...)
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            dispatcher = kwargs.get('dispatcher')
            if dispatcher is None:
                raise ValueError("dispatcher должен быть передан как keyword argument (dispatcher=...)")
            user_id = get_user_id(*args, **kwargs)
            from src.core.application.services.users.user_flags import set_generating, clear_generating

            await set_generating(dispatcher["redis"], user_id, kind=kind)
            try:
                return await func(*args, **kwargs)
            finally:
                await clear_generating(dispatcher["redis"], user_id, kind=kind)
        return wrapper
    return decorator

def block_if_active_question(get_user_id):
    """
    Декоратор, который блокирует handler, если у пользователя есть активный вопрос.
    get_user_id — функция, возвращающая user_id по аргументам handler-а.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем dispatcher (aiogram 3 DI: должен быть в kwargs)
            dispatcher = kwargs.get("dispatcher")
            if dispatcher is None:
                raise ValueError("dispatcher должен быть передан как keyword argument (dispatcher=...)")
            redis = dispatcher["redis"]

            # Получаем user_id через функцию (например, lambda message, ...: message.from_user.id)
            user_id = get_user_id(*args, **kwargs)
            from src.core.application.services.users.user_flags import has_active_question

            if await has_active_question(redis, user_id):
                # Находим message/CallbackQuery
                msg = None
                for arg in args:
                    if isinstance(arg, Message):
                        msg = arg
                        break
                if msg:
                    await msg.answer(KIND_TO_MESSAGE.get('read'))
                return
            return await func(*args, **kwargs)
        return wrapper
    return decorator