import asyncio
import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.routers import health as health_router
from api.routers import users as users_router
from bot.handlers import start
from bot.handlers.admin import restart_bot, admin_menu, requests, admin_general_stats, delete_redis_keys, users
from bot.handlers.profile import profile_stats, profile_menu
from bot.handlers.reading import reading_main, reading_menu
from bot.handlers.users.cards import router as cards_router
from bot.middleware.access import AdminMiddleware
from bot.middleware.activity import LastActiveMiddleware
from bot.middleware.admin_check import AdminCheckMiddleware
from bot.middleware.command_block import CommandBlockerMiddleware
from bot.middleware.user_check import UserCheckMiddleware
from config.settings import tg_settings, db_settings
from core.infrastructure.clients.redis_client import rc as redis_client
from core.infrastructure.clients.mongodb import init_mongo
from core.infrastructure.clients.redis_client import init_redis
from core.infrastructure.clients.sqlalchemy import init_db
from core.infrastructure.database.connection import sqlalchemy_engine
from core.infrastructure.database.repository_factory import RepositoryFactory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


async def notify_admin_after_restart(bot):
    admin_id = await redis_client.get("restart_notify_admin_id")
    if admin_id:
        logging.info(f"admin_id из Redis: {admin_id!r}")
        await bot.send_message(int(admin_id), "✅ Бот успешно перезагружен!")
        await redis_client.delete("restart_notify_admin_id")


async def on_startup(bot: Bot):
    await notify_admin_after_restart(bot)
    logging.info("✅ Бот запущен.")


async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    await bot.session.close()
    await sqlalchemy_engine.dispose()
    logging.info("🛑 Завершение. Сессии БД и бот закрыты.")


# --- FastAPI lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Lifespan started!")

    # 1. Инициализация SQLAlchemy
    await init_db()

    # 2. Инициализация Redis
    await init_redis()

    # 3. Инициализация MongoDB
    mongo_client = await init_mongo(app, db_settings)

    # Запускаем aiogram-бота как фоновую задачу
    bot = Bot(
        token=tg_settings.tg_bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.startup.register(on_startup)
    dp["redis"] = redis_client

    # Middleware
    dp.message.middleware(CommandBlockerMiddleware())
    dp.message.middleware(LastActiveMiddleware())
    dp.callback_query.middleware(LastActiveMiddleware())
    dp.message.middleware(AdminCheckMiddleware())
    dp.message.middleware(AdminMiddleware())
    dp.callback_query.middleware(AdminCheckMiddleware())
    dp.message.middleware(UserCheckMiddleware())
    dp.callback_query.middleware(UserCheckMiddleware())

    # Routers
    dp.include_router(start.router)
    dp.include_router(admin_menu.router)
    dp.include_router(requests.router)
    dp.include_router(users.router)
    dp.include_router(admin_general_stats.router)
    dp.include_router(restart_bot.router)
    dp.include_router(delete_redis_keys.router)
    dp.include_router(reading_menu.router)
    dp.include_router(reading_main.router)
    dp.include_router(profile_menu.router)
    dp.include_router(cards_router)
    dp.include_router(profile_stats.router)


    # stop_event = asyncio.Event()

    async def polling():
        logging.info("Starting aiogram polling...")
        await notify_admin_after_restart(bot)
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logging.exception("Polling task crashed!")

    polling_task = asyncio.create_task(polling())
    yield
    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError as e:
        logging.warning(f"Polling cancelled: {e}")
    await on_shutdown(dp, bot)
    await mongo_client.close()


# app = FastAPI(lifespan=lifespan)
app = FastAPI(
    title="Telegram Reading Bot API",
    description="API for external calls to the Telegram Reading Bot",
    version="1",
    lifespan=lifespan
)

# Add CORS middleware
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

app.include_router(health_router.router)
app.include_router(users_router.router)
