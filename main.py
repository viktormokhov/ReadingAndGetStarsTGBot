import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

from core.config import tg_settings
from core.database.init_db import AsyncSessionLocal
from core.database.init_db import init_db
from core.middleware.access import AdminMiddleware
from core.middleware.activity import LastActiveMiddleware
from core.middleware.admin_check import AdminCheckMiddleware
from core.middleware.command_block import CommandBlockerMiddleware
# from core.middleware.approve_check import ApproveCheckMiddleware
# from core.middleware.load_user import LoadUserMiddleware
from core.middleware.user_check import UserCheckMiddleware
from core.services.clients.mongodb import init_mongo, ensure_collections
from core.services.clients.redis_client import init_redis, redis_client
from handlers import start
from handlers.admin import admin_menu, requests, users, admin_general_stats, restart_bot, delete_redis_keys
from handlers.profile import profile_menu, profile_stats
from handlers.users.cards import router as cards_router
from handlers.reading import reading_main, reading_menu
# from handlers.webapp import router as webapp_router


async def on_startup(bot: Bot):
    await notify_admin_after_restart(bot)
    logging.info("✅ Бот запущен.")


async def notify_admin_after_restart(bot):
    admin_id = await redis_client.get("restart_notify_admin_id")
    if admin_id:
        logging.info(f"admin_id из Redis: {admin_id!r}")
        await bot.send_message(int(admin_id), "✅ Бот успешно перезагружен!")
        await redis_client.delete("restart_notify_admin_id")

async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    await init_db()
    await init_redis()
    await init_mongo()
    await ensure_collections()
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

    # @dp.callback_query()
    # async def debug_callback(callback: CallbackQuery):
    #     print("DEBUG CALLBACK:", callback.data)
    #     await callback.answer("Неизвестная команда", show_alert=True)
    #
    # dp.message.middleware(LoadUserMiddleware())
    # dp.callback_query.middleware(LoadUserMiddleware())
    #
    # dp.message.middleware(ApproveCheckMiddleware())
    # dp.callback_query.middleware(ApproveCheckMiddleware())

    # Роутеры Admin
    # dp.include_router(blocker.router)
    dp.include_router(start.router)
    dp.include_router(admin_menu.router)
    dp.include_router(requests.router)
    dp.include_router(users.router)
    dp.include_router(admin_general_stats.router)
    dp.include_router(restart_bot.router)
    dp.include_router(delete_redis_keys.router)

    # Роутеры Topic
    dp.include_router(reading_menu.router)
    dp.include_router(reading_main.router)

    # Роутер Quiz Arena (WebApp)
    # dp.include_router(webapp_router)

    # Роутеры Users
    dp.include_router(profile_menu.router)
    dp.include_router(cards_router)
    dp.include_router(profile_stats.router)

    # dp.include_router(users.router)

    # dp.include_router(withdrawal.router)
    # dp.include_router(settings.router)

    # dp.include_router(test_quiz.router)

    async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
        """Завершение работы — освобождение ресурсов."""
        await AsyncSessionLocal().remove()
        await bot.session.close()
        logging.info("🛑 Завершение. Сессии БД и бот закрыты.")

    # Ловим сразу две разновидности сообщений:
    # 1) анимации (GIF) — F.animation
    # 2) любой текст, но не команды (F.text & ~F.text.startswith('/'))

    # Удаляем мусор в чате
    # @dp.message(~StateFilter(Registration), lambda message: not message.text.startswith("/"))
    # async def delete_all_except_commands(message: Message):
    #     # Пропускаем только команды (например, /start и др.)
    #     if message.text.startswith("/"):
    #         return
    #     await asyncio.sleep(2)
    #     try:
    #         await message.delete()
    #     except Exception as e:
    #         logging.warning(f"Не удалось удалить сообщение {message.message_id}: {e}")
    # @dp.message(
    #     F.animation,
    #     ~StateFilter(Registration)
    # )
    # async def delete_animation(message: Message):
    #     await asyncio.sleep(2)
    #     try:
    #         await message.delete()
    #     except Exception as e:
    #         logging.warning(f"Не удалось удалить анимацию {message.message_id}: {e}")
    #
    # # Удаляем текстовые сообщения, которые не начинаются с “/”
    # @dp.message(
    #     F.text,
    #     ~StateFilter(Registration),
    #     lambda message: not message.text.startswith("/")
    # )
    # async def delete_plain_text(message: Message):
    #     await asyncio.sleep(2)
    #     try:
    #         await message.delete()
    #     except Exception as e:
    #         logging.warning(f"Не удалось удалить сообщение {message.message_id}: {e}")

    try:
        await dp.start_polling(bot, on_startup=on_startup)
    finally:
        await on_shutdown(dp, bot)


if __name__ == "__main__":
    asyncio.run(main())
