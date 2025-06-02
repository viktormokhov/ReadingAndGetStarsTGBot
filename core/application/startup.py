import logging
from core.infrastructure.telegram.telegram_client import TelegramClient
from config.settings import get_tg_settings

async def ensure_webhook():
    tg_settings = get_tg_settings()
    webhook_url = tg_settings.tg_webhook_url
    bot_token = tg_settings.bot_token
    secret_token = tg_settings.webhook_token
    tg_client = TelegramClient(bot_token)
    webhook_info = await tg_client.get_webhook_info()

    current_url = webhook_info.get("result", {}).get("url")
    if current_url != webhook_url:
        logging.info(f"🔗 Webhook is missing or incorrect. Setting webhook to {webhook_url} ...")
        result = await tg_client.set_webhook(webhook_url, secret_token, drop_pending_updates=True)
        if result.get("ok"):
            logging.info("✅ Webhook set successfully.")
        else:
            logging.error(f"❌ Failed to set webhook: {result}")
    else:
        logging.info(f"✅ Webhook already set: {current_url}")