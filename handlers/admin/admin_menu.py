from aiogram import Router, F
from aiogram.types import CallbackQuery

from core.decorators.admin_only import admin_only
from handlers.ui.ui_main import main_menu_inline_kb
from handlers.ui.ui_admin import admin_panel_inline_kb

router = Router()


@router.callback_query(F.data == "admin")
@admin_only()
async def admin_panel_callback(callback: CallbackQuery, is_admin: bool):
    """
    Панель администратора: по нажатию на inline-кнопку "admin:menu"
    """
    await callback.answer()
    await callback.message.edit_text(
        "🔧 Панель администратора:",
        reply_markup=admin_panel_inline_kb()
    )

@router.callback_query(F.data == "admin:back")
@admin_only()
async def admin_panel_back(callback: CallbackQuery, is_admin: bool):
    await callback.answer()
    # Здесь верни предыдущий экран (например, главное меню или другое сообщение)
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=main_menu_inline_kb(is_admin)  # функция для твоего главного меню
    )
