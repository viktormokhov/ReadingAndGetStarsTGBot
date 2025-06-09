from src.core.infrastructure.clients.redis_client import rc as redis_client
from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.core.application.security.admin_only import admin_only

router = Router()


@router.callback_query(F.data == "admin:redis_del")
@admin_only()
async def delete_redis_users_keys(callback: CallbackQuery, is_admin: bool):
    pattern = "users:*"
    keys = await redis_client.keys(pattern)
    if keys:
        await redis_client.delete(*keys)
        await callback.answer(f"🗑️ Удалено {len(keys)} ключей users:*")
    else:
        await callback.answer("Нет ключей users:*")
