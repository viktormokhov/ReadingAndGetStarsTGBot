import logging
from typing import Any, Optional

from aiogram.types import CallbackQuery
from pydantic import ValidationError

from core.ai.llm_image_content_generator import LLMImageContentGenerator
from core.database.card_ops import save_card, is_card_duplicate
from core.database.user_ops import get_user_age
from core.decorators.block import async_with_generating_flag
from core.services.clients.sqlalchemy import AsyncSessionLocal


@async_with_generating_flag(lambda call, qs, logger, dispatcher: qs.uid, kind="card")
async def process_card_generation(
        call: CallbackQuery,
        qs: Any,
        logger: logging.Logger,
        dispatcher
) -> Optional[bool]:
    """
    Асинхронно генерирует карточку с помощью LLM, заменяет плейсхолдер на изображение и сохраняет результат в БД.

    Шаги работы функции:
        1. Проверяет, не является ли карточка дубликатом.
        2. Получает возраст пользователя.
        3. Создаёт генератор контента.
        4. Отправляет сообщение-плейсхолдер в чат.
        5. Генерирует изображение для карточки.
        6. Заменяет плейсхолдер на сгенерированное изображение (или сообщение с ошибкой).
        7. Сохраняет карточку в базе данных.
    """
    async with AsyncSessionLocal() as session:
        # Проверка на дубликат в БД
        if await is_card_duplicate(qs.uid, qs.theme, qs.card_title, session):
            return None

        age = await get_user_age(qs.uid, session)
        generator = LLMImageContentGenerator(uid=qs.uid, theme=qs.theme, age=age)

        # Отправляем placeholder сообщение
        placeholder_msg = await call.bot.send_message(
            chat_id=call.message.chat.id,
            text="🎨 Генерирую карточку…",
        )
        msg_id = placeholder_msg.message_id

        # Генерируем изображение
        try:
            url = await generator.generate_image(qs.card_title)
        except Exception as err:
            await edit_placeholder_with_error(call, msg_id, str(err))
            return False

        # Заменяем placeholder на изображение
        if not await replace_placeholder_with_media(call, msg_id, url, logger):
            return None

        # Сохраняем карточку в БД
        try:
            await save_card(qs.uid, qs.theme, qs.card_title, url.media, session)
            return True
        except Exception as err:
            await call.message.edit_text(str(err))
            return False


async def edit_placeholder_with_error(call: CallbackQuery, msg_id: int, error_text: str) -> None:
    """Заменяет плейсхолдер-сообщение на текст ошибки."""
    await call.bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=msg_id,
        text=error_text
    )


async def replace_placeholder_with_media(call: CallbackQuery, msg_id: int, url: str, logger: logging.Logger) -> bool:
    """
    Пытается заменить сообщение-плейсхолдер на изображение.
    В случае ошибки валидации media, меняет текст плейсхолдера на ссылку.
    При других ошибках удаляет сообщение-плейсхолдер.
    """
    try:
        await call.bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=msg_id,
            media=url
        )
        return True
    except ValidationError as e:
        logger.error("Ошибка валидации media для edit_message_media: %s", e)
        await call.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=msg_id,
            text=f"✔️ Карточка готова: {url}"
        )
        return True
    except Exception:
        logger.exception("Не смогли заменить placeholder на картинку")
        await call.bot.delete_message(call.message.chat.id, msg_id)
        return False
