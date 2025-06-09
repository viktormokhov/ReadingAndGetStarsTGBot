from datetime import datetime

from config.settings import get_tg_settings
from core.domain.models.user import UserResponse


async def notify_admin_about_registration(user: UserResponse, birth_date: str):
    """Уведомление администратора о новой регистрации"""
    from core.utils.date_utils import calculate_age

    tg_settings = get_tg_settings()
    try:
        bot_token = tg_settings.tg_bot_token
        admin_id = tg_settings.tg_admin_id

        if not bot_token or not admin_id:
            print("TELEGRAM_BOT_TOKEN или TELEGRAM_ADMIN_ID не настроены")
            return

        # Форматируем дату рождения
        birth_date_formatted = datetime.strptime(birth_date, "%Y-%m-%d").strftime("%d.%m.%Y")

        # Вычисляем возраст
        age = calculate_age(birth_date)

        # Создаем текст уведомления
        text = f"""
        🆕 <b>Новая регистрация!</b>

        👤 <b>Имя:</b> {user.name}
        🆔 <b>Telegram ID:</b> {user.telegram_id}
        🎂 <b>Возраст:</b> {age} лет
        📅 <b>Дата рождения:</b> {birth_date_formatted}
        🎨 <b>Аватар:</b> {user.avatar}

        ⏰ <b>Время регистрации:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

        Подтвердить регистрацию пользователя?
        """

        # Создаем inline клавиатуру
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

        await send_telegram_message(
            bot_token,
            int(admin_id),
            text,
            reply_markup
        )

    except Exception as e:
        print(f"Ошибка отправки уведомления администратору: {e}")
