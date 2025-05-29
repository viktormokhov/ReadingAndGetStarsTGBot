from core.services.clients.redis_client import redis_client
from aiogram import Router, F
from aiogram.types import CallbackQuery

from core.decorators.admin_only import admin_only

router = Router()


@router.callback_query(F.data == "admin:redis_del")
@admin_only()
async def delete_redis_users_keys(callback: CallbackQuery, is_admin: bool):
    pattern = "user:*"
    keys = await redis_client.keys(pattern)
    if keys:
        await redis_client.delete(*keys)
        await callback.answer(f"🗑️ Удалено {len(keys)} ключей user:*")
    else:
        await callback.answer("Нет ключей user:*")
