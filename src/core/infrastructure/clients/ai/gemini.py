from aiogram.client.session import aiohttp

from src.config.settings import get_gemini_settings


async def _get_gemini_response(url, prompt):
    """Выполняет асинхронный POST-запрос к Google Gemini API."""
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            response.raise_for_status()
            return await response.json()


async def get_google_gemini_text_response(model, prompt):
    """Получает ответ от текстовой модели Google Gemini."""
    ai_settings = get_gemini_settings()

    compose_url = f"{ai_settings.google_gemini_proxy_url}{model}?key={ai_settings.google_gemini_api_key}"
    return await _get_gemini_response(compose_url, prompt)


# TODO Imagen model need pay
# async def get_google_gemini_vision_image_response(prompt):
#     """Получает ответ от визуальной (vision/image) модели Google Gemini."""
#     url = f"{ai_settings.google_gemini_proxy_url}{ai_settings.gemini_image_model}"
#     return await _get_gemini_response(url, prompt), ai_settings.gemini_image_model
