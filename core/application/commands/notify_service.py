import logging
from datetime import datetime

from config.settings import get_tg_settings
from core.domain.models.user import UserResponse
from core.infrastructure.telegram.telegram_client import TelegramClient


async def notify_admin_about_registration(user: UserResponse, birth_date: str):
    tg_settings = get_tg_settings()
    bot_token = tg_settings.tg_bot_token
    admin_id = tg_settings.tg_admin_id

    birth_date_formatted = datetime.strptime(birth_date, "%Y-%m-%d").strftime("%d.%m.%Y")
    text = (
        f"🆕 <b>Новая регистрация!</b>\n\n"
        f"👤 <b>Имя:</b> {user.name}\n"
        f"🆔 <b>Telegram ID:</b> {user.telegram_id}\n"
        f"🎂 <b>Возраст:</b> {user.age} лет\n"
        f"📅 <b>Дата рождения:</b> {birth_date_formatted}\n"
        f"🎨 <b>Аватар:</b> {user.avatar}\n\n"
        f"⏰ <b>Время регистрации:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        f"Подтвердить регистрацию пользователя?"
    )
    reply_markup = {
        "inline_keyboard": [
            [
                {
                    "text": "✅ Подтвердить",
                    "callback_data": f"approve_user_{user.telegram_id}"
                },
                {
                    "text": "❌ Отклонить",
                    "callback_data": f"reject_user_{user.telegram_id}"
                }
            ]
        ]
    }
    await send_message(
        bot_token,
        int(admin_id),
        text,
        reply_markup
    )


async def notify_admin_after_restart():
    tg_settings = get_tg_settings()
    tg_client = TelegramClient(tg_settings.bot_token)
    admin_id = tg_settings.tg_admin_id
    try:
        response = await tg_client.send_message(
            admin_id,
            "✅ Бот успешно перезагружен!"
        )
        if response.get("ok"):
            logging.info("Admin notified about restart successfully.")
        else:
            logging.error(f"Failed to notify admin: {response}")
    except Exception as e:
        logging.error(f"Exception during admin notification: {e}")