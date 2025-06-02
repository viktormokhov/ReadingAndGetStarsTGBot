from typing import Literal

from openai import AsyncOpenAI

from config.settings import get_openai_settings


ai_settings = get_openai_settings()
client_open_ai = AsyncOpenAI(api_key=ai_settings.openai_api_key)


async def get_openai_gpt_text_response(model, prompt):
    """Асинхронно вызывает OpenAI GPT и возвращает сгенерированный текст."""
    response = await client_open_ai.chat.completions.create(
        model=model,
        messages=[{"role": "users", "content": prompt}],
        temperature=0.8,
        max_tokens=600,
    )
    return response


async def get_openai_dalle_image_response(model,
                                          prompt: str,
                                          n: int = 1,
                                          size: Literal["1024x1024"] = "1024x1024",
                                          quality: Literal["standard"] = "standard"):
    """
    Асинхронно вызывает OpenAI DALL-E и возвращает URL сгенерированного изображения.
    """
    response = await client_open_ai.images.generate(
        model=model,
        prompt=prompt,
        n=n,
        size=size,
        quality=quality,
    )
    return response.data[0].url, model
