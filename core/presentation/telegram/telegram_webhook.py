from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends

from core.application.commands.process_start_command import process_start_command
# from api.routers.user import moderate_user
# from config.settings import tg_settings, WEBAPP_URL
from core.domain.models.telegram import TelegramWebhook
from core.domain.models.user import ModerationRequest
from core.infrastructure.telegram.telegram_client import TelegramClient, get_tg_client
from core.presentation.deps import verify_webhook_api_key

router = APIRouter(
    prefix="/api/v1/telegram",
    tags=["telegram"],
    dependencies=[Depends(verify_webhook_api_key)],
    responses={404: {"description": "Not found"}},
)


@router.post("/telegram-webhook")
async def telegram_webhook(webhook: TelegramWebhook,
                           background_tasks: BackgroundTasks,
                           tg_client: TelegramClient = Depends(get_tg_client)):
    """Обработка webhook от Telegram"""
    user_id = webhook.message["chat"]["id"]

    try:
        if webhook.callback_query:
            callback_data = webhook.callback_query.get("data", "")
            chat_id = webhook.callback_query["message"]["chat"]["id"]
            message_id = webhook.callback_query["message"]["message_id"]
            admin_id = webhook.callback_query["from"]["id"]

            if callback_data.startswith("approve_user_") or callback_data.startswith("reject_user_"):
                action = "approve" if callback_data.startswith("approve_user_") else "reject"
                user_id = int(callback_data.split("_")[-1])

                # Обновляем статус пользователя
                moderation_request = ModerationRequest(
                    user_id=user_id,
                    action=action,
                    admin_id=admin_id
                )

                # Обрабатываем модерацию
                await moderate_user(moderation_request, background_tasks)

                # Обновляем сообщение администратора
                bot_token = tg_settings.tg_bot_token
                if bot_token:
                    status_text = "✅ ПОДТВЕРЖДЕН" if action == "approve" else "❌ ОТКЛОНЕН"
                    updated_text = f"""
                    🆕 <b>Регистрация обработана</b>

                    👤 <b>Пользователь ID:</b> {user_id}
                    📊 <b>Статус:</b> {status_text}
                    👨‍💼 <b>Обработал:</b> {admin_id}
                    ⏰ <b>Время:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}
                    """

                    await edit_telegram_message(
                        bot_token,
                        chat_id,
                        message_id,
                        updated_text.strip()
                    )
        elif webhook.message:
            text = webhook.message.get("text", "")
            if text and text.startswith("/start"):
                background_tasks.add_task(process_start_command, user_id, tg_client)

        return {"success": True}

    except Exception as e:
        print(f"Ошибка обработки webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))
