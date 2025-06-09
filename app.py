import logging
from contextlib import asynccontextmanager

import aiohttp
from fastapi import FastAPI, HTTPException
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware

from config.settings import get_tg_settings, get_db_settings, get_minio_settings
from core.application.commands.notify_service import notify_admin_after_restart
from core.infrastructure.clients.minio_client import init_minio
from core.infrastructure.clients.mongodb import init_mongo
from core.infrastructure.clients.postgres import init_db, sqlalchemy_engine
from core.infrastructure.clients.redis_client import init_redis
from core.infrastructure.security.backend import APIKeyAuthBackend
from core.infrastructure.telegram.telegram_client import TelegramClient, ensure_webhook
from core.presentation.health.health_router import router as health_router
from core.presentation.telegram.telegram_webhook import router as webhook_router
from core.presentation.user.create_account import router as create_account_router
from core.presentation.user.user_profile import router as user_profile_router

# --- Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

tg_settings = get_tg_settings()
db_settings = get_db_settings()
minio_settings = get_minio_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Lifespan started!")

    # Инициализация PostgreSQL+SQLAlchemy
    await init_db()

    # Инициализация MongoDB
    mongo_client = await init_mongo(app, db_settings)

    # Инициализация MinIO
    minio_client = await init_minio(app, minio_settings)
    app.state.minio_client = minio_client

    # 4. Инициализация Redis
    redis_client = await init_redis(app, db_settings)
    app.state.redis = redis_client

    # Инициализация aiohttp-сессии (глобально)
    session = aiohttp.ClientSession()
    app.state.aiohttp_session = session

    # Глобальный TelegramClient
    tg_client = TelegramClient(tg_settings.bot_token, session)
    app.state.tg_client = tg_client

    # Проверка и установка Webhook
    await ensure_webhook(
        tg_client,
        webhook_url=tg_settings.tg_webhook_url,
        secret_token=tg_settings.webhook_token,
    )

    # Уведомление администратора о перезагрузке
    await notify_admin_after_restart(tg_client)

    yield

    await sqlalchemy_engine.dispose()
    await mongo_client.close()
    await redis_client.close()
    await session.close()
    logging.info("🛑 Shutting down. Database sessions have been closed.")


# --- FastAPI
app = FastAPI(
    title="QuizBot API",
    description="API for external calls to the Telegram Reading Bot",
    version="1.0.0",
    docs_url=None,
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthenticationMiddleware, backend=APIKeyAuthBackend())

# --- Routers
app.include_router(health_router)
app.include_router(create_account_router)
app.include_router(user_profile_router)
app.include_router(webhook_router)

# --- Кастомный Swagger UI (docs) только для админа
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi import Request


@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui(request: Request):
    user = getattr(request, "user", None)
    if user and getattr(user, "username", None) == "admin":
        return get_swagger_ui_html(openapi_url="/api/openapi.json", title="Telegram Reading Bot API")
    else:
        raise HTTPException(status_code=403, detail="Access denied")
