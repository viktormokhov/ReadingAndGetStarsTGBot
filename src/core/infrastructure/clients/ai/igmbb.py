import base64

from aiogram.client.session import aiohttp

from src.config.settings import get_imgbb_settings

imgbb_settings = get_imgbb_settings()

async def upload_to_imgbb(raw):
    image_base64 = base64.b64encode(raw).decode('utf-8')
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": imgbb_settings.imgbb_api_key,
        "image": image_base64
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as resp:
            data = await resp.json()
            if not data.get('success', False):
                error_message = data.get('error', {}).get('message', 'Unknown error')
                raise f"Failed to upload to imgbb: {error_message}"
            return data
