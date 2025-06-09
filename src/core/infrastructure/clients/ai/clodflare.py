import aiohttp

from src.config.settings import get_cloudflare_settings


async def get_cloudflare_worker_image_response(model, prompt):
    """
    Выполняет асинхронный POST-запрос к Cloudflare Workers AI для генерации изображения.
    """
    ai_settings = get_cloudflare_settings()

    url = f'{ai_settings.cloudflare_worker_image_url}'
    headers = {
        'Authorization': f'Bearer {ai_settings.cloudflare_api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        "prompt": prompt
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            response.raise_for_status()
            return await response.read(), response.url.name