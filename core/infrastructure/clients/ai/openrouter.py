from openai import AsyncOpenAI

from config.settings import ai_settings

client_openrouter_ai = AsyncOpenAI(
    base_url=ai_settings.deepseek.openrouter_url,
    api_key=ai_settings.deepseek.openrouter_api_key.get_secret_value()
)


async def get_openrouter_deepseek_text_response(model, prompt):
    """Асинхронно вызывает OpenRouter (deepseek) и возвращает сгенерированный текст."""
    response = await client_openrouter_ai.chat.completions.create(
        model=model,
        messages=[{"role": "users", "content": prompt}],
    )
    return response
