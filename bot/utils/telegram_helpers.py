from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InputMedia

async def safe_edit_text(
    bot: Bot,
    chat_id: int,
    message_id: int,
    new_text: str,
    **kwargs
) -> None:
    """
    Пытаемся отредактировать текст, но молча игнорируем
    TelegramBadRequest: Message is not modified
    """
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=new_text,
            **kwargs
        )
    except TelegramBadRequest as e:
        # Игнорируем ошибку, если текст не изменился
        if "Message is not modified" in str(e):
            return
        # Пробрасываем другие ошибки
        raise

async def safe_edit_media(
    bot: Bot,
    chat_id: int,
    message_id: int,
    media: InputMedia,
    **kwargs
) -> None:
    """
    Обертка для bot.edit_message_media, игнорируем ошибку при отсутствии изменений
    """
    try:
        await bot.edit_message_media(
            chat_id=chat_id,
            message_id=message_id,
            media=media,
            **kwargs
        )
    except TelegramBadRequest as e:
        # Игнорируем, если медиа не было изменено
        if "Message is not modified" in str(e):
            return
        # Пробрасываем прочие ошибки
        raise