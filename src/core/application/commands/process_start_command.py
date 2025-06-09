from config.settings import WEBAPP_URL
from core.infrastructure.telegram.telegram_client import TelegramClient


async def process_start_command(user_id: int, tg_client: TelegramClient):
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "🤖 Открыть Читайка Q",
                    "web_app": {"url": WEBAPP_URL}
                }
            ]
        ]
    }

    await tg_client.send_message(
        user_id,
        "Добро пожаловать!\nНажми кнопку ниже, чтобы открыть приложение:",
        keyboard
    )
