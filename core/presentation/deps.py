from typing import Optional

from fastapi import Header, HTTPException
from starlette import status

from config.settings import get_backend_settings, get_tg_settings


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    backend_settings = get_backend_settings()

    if x_api_key != backend_settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )


async def verify_webhook_api_key(x_telegram_bot_api_secret_token: Optional[str] = Header(None)):
    tg_settings = get_tg_settings()
    if x_telegram_bot_api_secret_token != tg_settings.webhook_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Webhook API Key",
        )
