import aiohttp

from core.config import ai_settings


async def get_cloudflare_worker_image_response(model, prompt):
    """
    Выполняет асинхронный POST-запрос к Cloudflare Workers AI для генерации изображения.
    """
    url = f'{ai_settings.cloudflare.cloudflare_worker_image_url}'
    headers = {
        'Authorization': f'Bearer {ai_settings.cloudflare.cloudflare_api_key.get_secret_value()}',
        'Content-Type': 'application/json'
    }
    payload = {
        "prompt": prompt
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            response.raise_for_status()
            return await response.read(), response.url.name