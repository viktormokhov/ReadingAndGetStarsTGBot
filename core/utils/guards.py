from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.database import user_ops
from core.database.init_db import AsyncSessionLocal


async def block_if_pending_message(message: Message, state: FSMContext) -> bool:
    """
    Блокирует команды, если активен незавершённый вопрос (theme установлен).
    Используется для текстовых сообщений.
    """
    data = await state.get_data()
    if data.get("theme"):
        await message.answer("Сначала ответь на текущий вопрос! 😊")
        return True
    return False


async def block_if_pending_callback(callback: CallbackQuery, state: FSMContext) -> bool:
    """
    Блокирует кнопки, если активен незавершённый вопрос (theme установлен).
    Используется для CallbackQuery.
    """
    data = await state.get_data()
    if data.get("theme"):
        await callback.answer("Сначала ответь на текущий вопрос!", show_alert=True)
        return True
    return False
