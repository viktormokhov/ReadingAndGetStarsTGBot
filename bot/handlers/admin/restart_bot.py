import os

from aiogram import Router, F
from aiogram.types import CallbackQuery

from core.application.security.admin_only import admin_only
from core.infrastructure.clients.redis_client import rc as redis_client

router = Router()


@router.callback_query(F.data == "admin:restart")
@admin_only()
async def restart_bot(callback: CallbackQuery, is_admin: bool):
    await callback.answer("🔄 Restarting the bot...")
    await redis_client.set("restart_notify_admin_id", callback.from_user.id)
    os.system("systemctl restart tg_reading_bot.service")
