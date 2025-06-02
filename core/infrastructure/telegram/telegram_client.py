from typing import Optional

import aiohttp


class TelegramClient:
    def __init__(self, bot_token: str):
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    async def get_webhook_info(self):
        url = f"{self.base_url}/getWebhookInfo"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    async def set_webhook(self, webhook_url: str, secret_token: str, drop_pending_updates: bool = False):
        """
        Устанавливает webhook для Telegram бота.
        :param webhook_url: URL, на который Telegram будет отправлять обновления.
        :param drop_pending_updates: Сбросить ли все ожидающие обновления (по умолчанию False).
        """
        url = f"{self.base_url}/setWebhook"
        payload = {
            "url": webhook_url,
            "drop_pending_updates": drop_pending_updates,
            "secret_token": secret_token
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                return await response.json()

    async def send_message(self, chat_id: int, text: str, reply_markup: Optional[dict] = None):
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    return {
                        "ok": False,
                        "error_code": response.status,
                        "description": await response.text()
                    }
                return await response.json()

    async def edit_message(self, chat_id: int, message_id: int, text: str, reply_markup: Optional[dict] = None):
        url = f"{self.base_url}/editMessageText"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML"
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    return {
                        "ok": False,
                        "error_code": response.status,
                        "description": await response.text()
                    }
                return await response.json()
