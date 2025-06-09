from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hbold
from fastapi import Depends

from core.application.security.admin_only import admin_only
from bot.handlers.ui.ui_admin import admin_back_menu_kb
from core.application.services.admin.admin_stats import get_general_stats
from core.infrastructure.db.repository_factory import RepositoryFactory

router = Router()

async def user_repo_dep():
    return RepositoryFactory.create_user_repository()

@router.callback_query(F.data == "admin:stats")
@admin_only()
async def show_general_stats(call: CallbackQuery, is_admin: bool, user_repo = Depends(user_repo_dep)):
    try:
        await call.answer()
        stats = await get_general_stats(user_repo)

        msg = (
            f"{hbold('📊 Общая статистика')}\n\n"
            f"👥 Всего пользователей: {stats.total_users}\n"
            f"✅ Одобрено: {stats.approved_users}\n"
            f"📈 Средняя точность: {stats.avg_accuracy * 100:.0f}%\n"
            f"⭐ Общее количество звёзд: {stats.total_stars}\n"
            f"🕓 Среднее время в боте: {stats.avg_active_hours} ч {stats.avg_active_minutes} мин\n"
            f"💬 Вопросов задано: {stats.total_questions}\n"
            f"🃏 Карточек выдано: {stats.total_cards}"
        )

        await call.message.edit_text(
            msg,
            reply_markup=admin_back_menu_kb(),
            parse_mode="HTML"
        )

    except Exception as e:
        await call.message.edit_text(
            "❌ Произошла ошибка при получении статистики. Попробуйте позже.",
            reply_markup=admin_back_menu_kb()
        )
