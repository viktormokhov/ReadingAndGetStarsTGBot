from aiogram import Router, F
from aiogram.types import CallbackQuery

from core.application.security.approved_user_only import is_approved_user
from bot.handlers.ui.ui_main import main_menu_inline_kb
from bot.handlers.ui.ui_profile import profile_inline_kb
from core.infrastructure.db.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository

router = Router()

@router.callback_query(F.data == "profile")
@is_approved_user()
async def profile_callback(callback: CallbackQuery):
    """
    Профиль пользователя: по нажатию на inline-кнопку "profile:menu"
    """
    await callback.answer()
    async with SQLAlchemyUserRepository() as repo:
        user = await repo.get_by_id(callback.from_user.id)
    await callback.message.edit_text(
        f"⚙️ Профиль <b>{user.name}</b>:",
        reply_markup=profile_inline_kb()
    )

@router.callback_query(F.data == "profile:back")
async def reading_back_callback(call: CallbackQuery, is_admin: bool):
    await call.answer()
    await call.message.edit_text(
        "<b>Главное меню</b>. Выбирай раздел:",
        reply_markup=main_menu_inline_kb(is_admin),
        parse_mode="HTML"
    )