import os
import sys

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from core.decorators.admin_only import admin_only
from core.services.clients.redis_client import redis_client

router = Router()


@router.callback_query(F.data == "admin:restart")
@admin_only()
async def restart_bot(callback: CallbackQuery, is_admin: bool):
    await callback.answer("🔄 Перезагрузка бота...")

    # Сохраняем id админа в Redis
    await redis_client.set("restart_notify_admin_id", callback.from_user.id)

    # Рестарт бота
    try:

        bot: Bot = callback.bot
        await bot.session.close()
    except:
        pass
    os.execv(sys.executable, [sys.executable] + sys.argv)
