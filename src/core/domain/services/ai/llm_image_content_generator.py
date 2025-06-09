import logging
import random
from typing import Any

from aiogram.types import InputMediaPhoto

from src.config.settings import get_ai_settings
from src.core.domain.services.ai.llm_providers import LLM_IMAGE_PROVIDERS
from src.core.domain.services.ai.prompt.prompt import CARD_PROMPT
from src.config.constants import MAX_RETRIES
from src.config.content import IMAGE_FORMATS, IMAGE_STYLES
from src.core.domain.services.ai.decorators.handle_image_errors import handle_image_errors
from src.core.infrastructure.clients.ai.igmbb import upload_to_imgbb

logger = logging.getLogger(__name__)

ResultType = dict[str, Any]


class LLMImageContentGenerator:
    """
    Генератор картинок с помощью LLM (Stable Diffusion/DALLE) для заданной темы и возраста пользователя.

    Строит промпт, отправляет запрос на LLM-генерацию картинки с ретраями и сохраняет результат в истории пользователя.

    Attrs:
        uid (int): Идентификатор пользователя.
        theme (str): Тема карточки.
        age (int): Возраст пользователя (может влиять на генерацию).
    """

    def __init__(self, uid: int, theme: str, age: int):
        self.uid = uid
        self.theme = theme
        self.age = age
        self.ai_settings = get_ai_settings()

    def _build_prompt(self, title: str, age: int) -> str:
        """Формирует промпт для генерации изображения."""
        format_ = random.choice(IMAGE_FORMATS)
        style = random.choice(IMAGE_STYLES)
        return CARD_PROMPT % (title, age, format_, style)

    @handle_image_errors
    async def generate_image(self, title: str) -> InputMediaPhoto:
        """
        Асинхронно генерирует изображение по заголовку и возрасту (или self.age).
        Повторяет попытку генерации до MAX_RETRIES раз при ошибках.
        Сохраняет ссылку на изображение в истории пользователя.
        """
        last_exception = None
        for _ in range(MAX_RETRIES):
            raw, model = await self.get_llm_raw_image(title)
            if isinstance(raw, bytes):
                image_base64 = await upload_to_imgbb(raw)
                raw = image_base64['data']['display_url']
            return InputMediaPhoto(media=raw, caption=f"{title} ({model})")

        raise Exception("❗️Произошла ошибка при генерации картинки") from last_exception

    async def get_llm_raw_image(self, title: str) -> tuple[str, str]:
        """
        Генерирует изображение с помощью одной из LLM (Stable Diffusion или DALL-E).
        Возвращает кортеж (url, model).
        """
        prompt = self._build_prompt(title, self.age)
        provider_name, params = random.choice(list(self.ai_settings.get_all_image_models().items()))
        provider = LLM_IMAGE_PROVIDERS[provider_name]
        response = await provider['get_response'](params['image']['model_name'], prompt)
        return response[0], response[1]
