import logging
from typing import Optional, Any

import aiohttp
from fastapi import Request

from config.settings import get_tg_settings

logger = logging.getLogger("telegram_client")


class TelegramClient:
    """
    Асинхронный клиент для работы с Telegram Bot API.

    Пример использования:
        session = aiohttp.ClientSession()
        client = TelegramClient(bot_token="YOUR_BOT_TOKEN", session=session)
        await client.send_message(chat_id=123456789, text="Привет, мир!")

    Атрибуты:
        base_url (str): Базовый URL для запросов к Telegram Bot API.
        session (aiohttp.ClientSession): Сессия для выполнения HTTP-запросов.
    """

    def __init__(self, bot_token: str, session: aiohttp.ClientSession):
        self.base_url: str = f"https://api.telegram.org/bot{bot_token}"
        self.session: aiohttp.ClientSession = session

    async def _request(self, method: str, payload: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """
        Выполняет HTTP-запрос к Telegram Bot API.

        Args:
            method (str): Метод Telegram API (например, 'sendMessage').
            payload (Optional[dict]): Тело запроса (если необходимо).

        Returns:
            dict: Ответ Telegram API.

        Raises:
            aiohttp.ClientError: При ошибке сети.
        """
        url = f"{self.base_url}/{method}"
        try:
            if payload is not None:
                async with self.session.post(url, json=payload) as response:
                    data = await response.json()
            else:
                async with self.session.get(url) as response:
                    data = await response.json()
            if response.status != 200 or not data.get("ok", True):
                logger.error(f"Telegram API error: {response.status} {data}")
            return data
        except Exception as e:
            logger.exception(f"Telegram request failed: {e}")
            raise

    async def get_webhook_info(self) -> dict[str, Any]:
        """
        Получает информацию о текущем webhook.
        """
        return await self._request("getWebhookInfo")

    async def set_webhook(
            self,
            webhook_url: str,
            secret_token: str,
            drop_pending_updates: bool = False,
    ) -> dict[str, Any]:
        """
        Устанавливает webhook для Telegram бота.

        Args:
            webhook_url (str): URL для webhook.
            secret_token (str): Секретный токен для безопасности.
            drop_pending_updates (bool): Сбрасывать ли ожидающие обновления.

        Returns:
            dict: Результат установки webhook.
        """
        payload = {
            "url": webhook_url,
            "drop_pending_updates": drop_pending_updates,
            "secret_token": secret_token,
        }
        return await self._request("setWebhook", payload)

    async def send_message(
            self,
            chat_id: int,
            text: str,
            reply_markup: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Отправляет сообщение в чат.

        Args:
            chat_id (int): ID чата Telegram.
            text (str): Текст сообщения.
            reply_markup (Optional[dict]): Клавиатура или другие элементы управления (опционально).

        Returns:
            dict: Результат отправки сообщения.
        """
        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return await self._request("sendMessage", payload)

    async def edit_message(
            self,
            chat_id: int,
            message_id: int,
            text: str,
            reply_markup: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Редактирует ранее отправленное сообщение.

        Args:
            chat_id (int): ID чата Telegram.
            message_id (int): ID сообщения для редактирования.
            text (str): Новый текст сообщения.
            reply_markup (Optional[dict]): Клавиатура или другие элементы управления (опционально).

        Returns:
            dict: Результат редактирования сообщения.
        """
        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML",
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return await self._request("editMessageText", payload)


async def ensure_webhook(
        tg_client: TelegramClient,
        webhook_url: str,
        secret_token: str,
) -> None:
    """
    Проверяет, установлен ли правильный webhook для Telegram-бота, и если нет — устанавливает его.

    Args:
        tg_client (TelegramClient): Экземпляр TelegramClient.
        webhook_url (str): Желаемый URL webhook.
        secret_token (str): Секретный токен для валидации Telegram.
    """
    webhook_info = await tg_client.get_webhook_info()
    current_url = webhook_info.get("result", {}).get("url")
    if current_url != webhook_url:
        logger.info(f"🔗 Webhook is missing or incorrect. Setting webhook to {webhook_url} ...")
        result = await tg_client.set_webhook(webhook_url, secret_token, drop_pending_updates=True)
        if result.get("ok"):
            logger.info("✅ Webhook set successfully.")
        else:
            logger.error(f"❌ Failed to set webhook: {result}")
    else:
        logger.info(f"✅ Webhook already set: {current_url}")


def get_tg_client(request: Request):
    """
    Фабрика для получения TelegramClient из объекта запроса FastAPI.

    Args:
        request (Request): Объект запроса FastAPI.

    Returns:
        TelegramClient: Инициализированный клиент Telegram.
    """
    tg_settings = get_tg_settings()
    session = request.app.state.aiohttp_session
    return TelegramClient(bot_token=tg_settings.bot_token, session=session)
