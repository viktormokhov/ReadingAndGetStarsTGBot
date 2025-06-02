import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.routers import user
from config.settings import get_tg_settings, get_db_settings
from core.application.commands.notify_service import notify_admin_after_restart
from core.application.startup import ensure_webhook
from core.infrastructure.clients.mongodb import init_mongo
from core.infrastructure.clients.postgres import init_db
from core.infrastructure.clients.redis_client import init_redis
from core.infrastructure.database.connection import sqlalchemy_engine
from core.presentation.routers.telegram_webhook import router as webhook_router
from core.presentation.health.health_router import router as health_router

# --- Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# --- Глобальные настройки
tg_settings = get_tg_settings()
db_settings = get_db_settings()


# --- FastAPI lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Lifespan started!")

    # 1. Инициализация PostgreSQL+SQLAlchemy
    await init_db()

    # 2. Инициализация Redis
    await init_redis()

    # 3. Инициализация MongoDB
    mongo_client = await init_mongo(app, db_settings)

    # 4. Проверка и установка Telegram webhook
    await ensure_webhook()

    # 5. Уведомление администратора о перезагрузке
    await notify_admin_after_restart()

    yield

    await sqlalchemy_engine.dispose()
    await mongo_client.close()
    logging.info("🛑 Shutting down. Database sessions have been closed.")


# --- Инициализация FastAPI
app = FastAPI(
    title="Telegram Reading Bot API",
    description="API for external calls to the Telegram Reading Bot",
    version="1.0.0",
    lifespan=lifespan
)

# --- CORS middleware
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:8000",
    #                "http://127.0.0.1:8000",
    #                "https://localhost:8001",
    #                "https://127.0.0.1:8001",
    #                "https://vercel.app"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers
app.include_router(health_router)
app.include_router(user.router)
app.include_router(webhook_router)
# app.include_router(users_router.router)
