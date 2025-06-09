from openai import AsyncOpenAI

from src.config.settings import get_deepseek_settings

ai_settings = get_deepseek_settings()

client_openrouter_ai = AsyncOpenAI(
    base_url=ai_settings.openrouter_url,
    api_key=ai_settings.openrouter_api_key
)


async def get_openrouter_deepseek_text_response(model, prompt):
    """Асинхронно вызывает OpenRouter (deepseek) и возвращает сгенерированный текст."""
    response = await client_openrouter_ai.chat.completions.create(
        model=model,
        messages=[{"role": "users", "content": prompt}],
    )
    return response
