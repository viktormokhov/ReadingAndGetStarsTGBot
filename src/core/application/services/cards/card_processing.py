from aiogram.types import CallbackQuery


async def edit_placeholder_with_error(call: CallbackQuery, msg_id: int, error_text: str) -> None:
    """Заменяет плейсхолдер-сообщение на текст ошибки."""
    await call.bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=msg_id,
        text=error_text
    )