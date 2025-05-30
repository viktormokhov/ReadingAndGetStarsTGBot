import logging
from typing import Any, Optional

from aiogram.types import CallbackQuery
from pydantic import ValidationError

from core.domain.services.ai.llm_image_content_generator import LLMImageContentGenerator
from core.infrastructure import save_card, is_card_duplicate
from core.infrastructure import get_user_age
from core.application.decorators.block import async_with_generating_flag
from core.infrastructure import AsyncSessionLocal


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
