from aiogram import Router, F
from aiogram.types import CallbackQuery

from core.database.user_ops import get_user
from core.decorators.approved_user_only import is_approved_user
from handlers.ui.ui_main import main_menu_inline_kb
from handlers.ui.ui_profile import profile_inline_kb

router = Router()

@router.callback_query(F.data == "profile")
@is_approved_user()
async def profile_callback(callback: CallbackQuery):
    """
    Профиль пользователя: по нажатию на inline-кнопку "profile:menu"
    """
    await callback.answer()
    user = await get_user(callback.from_user.id)
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