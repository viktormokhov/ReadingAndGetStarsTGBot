import random
from typing import Optional, Any

from core.ai.llm_providers import LLM_TEXT_PROVIDERS
from core.ai.prompt.prompt_builder import build_prompt
from core.ai.utils.normalize_and_validate import validate_generated_data
from core.config import ai_settings
from core.constants import MAX_RETRIES
from core.decorators.handle_text_generation import handle_text_errors
from core.services.storage.history_service import remember_text

ResultType = dict[str, Any]


class LLMTextContentGenerator:
    """
    Генератор текстового контента с использованием больших языковых моделей (LLM)
    для заданной темы и возраста пользователя.

    Класс обеспечивает построение промпта, отправку его в LLM и обработку ошибок при генерации текста.
    Может повторять попытки генерации текста при возникновении ошибок соединения или превышения лимитов.

    Attrs:
        uid (int): Идентификатор пользователя.
        theme (str): Тема, по которой генерируется текст.
        age (int): Возраст пользователя для персонализации контента.
    """

    def __init__(self, uid: int, theme: str, age: int):
        self.uid = uid
        self.theme = theme
        self.age = age

    def _build_prompt(self, category) -> str:
        """Формирует промпт для LLM на основе категории, темы и возраста пользователя."""
        return build_prompt(category, self.theme, self.age)

    @handle_text_errors
    async def generate_text(self, category) -> ResultType:
        """
        Асинхронно генерирует уникальный и корректно структурированный текст по заданной категории и теме.
        Повторяет попытку генерации до MAX_RETRIES раз при возникновении ошибок.
        Сохраняет сгенерированный текст в историю пользователя.
        """
        last: Optional[dict] = None
        for _ in range(MAX_RETRIES):
            result = await self.get_llm_raw_text(category)
            text = result.get("text", "").strip()

            # TODO: Проверка уникальности текста
            # if await text_is_semantically_similar(self.uid, text):
            #     last = result
            #     continue

            await remember_text(self.uid, text)
            # await remember_text_with_embedding(self.uid, text)
            return result
        return last or {"text": "", "card": "", "qa": []}

    async def get_llm_raw_text(self, category) -> dict[str, Any] | None:
        """
        Асинхронно отправляет запрос к LLM и получает сырые данные для заданной категории.
        Оборачивает вызов в обработчик ошибок с ретраями.
        """
        prompt = self._build_prompt(category)
        models = list(ai_settings.get_all_text_models().items())
        # Присвоим веса: по умолчанию 1, для openrouter — 0.2 (или 1/5)
        weights = [0.2 if name == "deepseek" else 1 for name, _ in models]
        provider_name, params = random.choices(models, weights=weights, k=1)[0]
        provider = LLM_TEXT_PROVIDERS[provider_name]
        response = await provider['get_response'](params['text']['model_name'], prompt)
        raw_text = provider['extract_text'](response)
        normalize_response_json = provider['normalize_response'](raw_text)
        normalize_response_json.update({'model': provider['get_model'](response)})
        validate_generated_data(normalize_response_json)
        return normalize_response_json
