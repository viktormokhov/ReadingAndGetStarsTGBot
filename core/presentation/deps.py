from typing import Optional

from fastapi import Header, Request, HTTPException
from starlette import status

from config.settings import get_tg_settings, get_backend_settings
from core.application.services.health_service import HealthService
from core.infrastructure.health.db_health_checker import DefaultDBHealthChecker
from core.infrastructure.health.mongo_health_checker import DefaultMongoHealthChecker
from core.infrastructure.health.redis_health_checker import DefaultRedisHealthChecker
from core.infrastructure.health.system_status_checker import DefaultSystemStatusChecker


backend_settings = get_backend_settings()

def verify_api_key(request: Request):
    user = getattr(request, "user", None)
    if user and getattr(user, "username", None) == "admin":
        return
    api_key = request.headers.get("x-api-key")
    if api_key != backend_settings.user_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def verify_webhook_api_key(x_telegram_bot_api_secret_token: Optional[str] = Header(None)):
    tg_settings = get_tg_settings()
    if x_telegram_bot_api_secret_token != tg_settings.webhook_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Webhook API Key",
        )


def get_health_service() -> HealthService:
    """
    Провайдер HealthService для FastAPI Depends.
    """
    return HealthService(
        mongo_checker=DefaultMongoHealthChecker(),
        redis_checker=DefaultRedisHealthChecker(),
        db_checker=DefaultDBHealthChecker(),
        system_checker=DefaultSystemStatusChecker(),
    )
