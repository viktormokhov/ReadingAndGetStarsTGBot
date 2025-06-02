from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fastapi import Depends

from config.settings import get_tg_settings
from core.infrastructure.database import user_ops
from core.infrastructure.database.models import User
from core.application.security.admin_only import admin_only
from bot.handlers.ui.ui_main import main_menu_inline_kb
from bot.handlers.ui.ui_admin import admin_back_menu_kb
from core.infrastructure.database.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from core.infrastructure.database.repository_factory import RepositoryFactory

router = Router()


# 1) Пользователь запрашивает доступ — рассылаем всем админам кнопки «Одобрить/Отклонить»
@router.callback_query(F.data == "request_access")
async def request_access_callback(call: CallbackQuery):
    """
    Обрабатывает нажатие на кнопку "Запросить доступ".
    Ставит флаг has_requested_access = True для пользователя.
    """
    tg_settings = get_tg_settings()
    uid = call.from_user.id
    async with SQLAlchemyUserRepository() as repo:
        user = await repo.get_by_id(uid)

    if not user.has_requested_access:
        user.has_requested_access = True
    if not user or not user.name:
        await call.answer("Сначала введите имя.", show_alert=True)
        return

    # Inline-клавиатура для админов
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Одобрить",
        callback_data=f"approve_user:{uid}"
    )
    builder.button(
        text="❌ Отклонить",
        callback_data=f"deny_user:{uid}"
    )
    kb = builder.as_markup(row_width=2)

    # Рассылаем уведомление админам
    for admin_id in tg_settings.tg_admin_id:
        await call.bot.send_message(
            chat_id=admin_id,
            text=f"🔔 Запрос доступа от {user.name} (ID: {uid})",
            reply_markup=kb,
            protect_content=True
        )

    # Отвечаем пользователю
    await call.message.edit_text("✅ Запрос отправлен! Ожидай одобрения.")
    await call.answer()


# 2) Админ заходит в раздел «Заявки на доступ» — видит список всех неподтверждённых
@router.callback_query(F.data == "admin:requests")
@admin_only()
async def show_requests(call: CallbackQuery, is_admin: bool):
    await call.answer()

    async with SQLAlchemyUserRepository() as repo:
        users = await repo.get_not_approved()
    if not users:
        # Все одобрены — только уведомление и кнопка "В меню"
        await call.message.edit_text("✅ Все пользователи одобрены.", reply_markup=admin_back_menu_kb())
        return

    # Для каждого — выводим отдельное сообщение с двумя кнопками
    for user in users:
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Одобрить", callback_data=f"approve_user:{user.id}")
        builder.button(text="🚫 Отклонить",  callback_data=f"deny_user:{user.id}")
        kb = builder.as_markup(row_width=2)

        await call.message.answer(
            f"• ID: {user.id}\nИмя: {user.name or '—'}",
            reply_markup=kb
        )

    # Кнопка «Назад» в конце списка
    kb_back = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 В меню", callback_data="admin:menu")]
    ])
    await call.message.answer("🔙 В меню", reply_markup=kb_back)


# 3) Общие обработчики approve/deny — одинаковая логика, только флаг is_approved
@router.callback_query(F.data.startswith("approve_user:"))
@admin_only()
async def approve_user(call: CallbackQuery, is_admin: bool):
    user_id = int(call.data.split(":", 1)[1])

    async with SQLAlchemyUserRepository() as repo:
        user = await repo.get_by_id(user_id)

    if not user:
        await call.answer("❌ Пользователь не найден", show_alert=True)
        return
    if user.is_approved:
        await call.answer("Уже одобрен", show_alert=True)
        return
    user.is_approved = True

    # Сообщаем в админском чате
    await call.message.edit_text(f"✅ Пользователь {user.name or user.id} одобрен.")
    await call.answer("Пользователь одобрен")

    # И уведомляем самого пользователя
    try:
        await call.bot.send_message(
            chat_id=user_id,
            text="✅ Доступ был одобрен. Выбирай раздел:",
            reply_markup=main_menu_inline_kb()
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("deny_user:"))
@admin_only()
async def deny_user(call: CallbackQuery, is_admin: bool):
    user_id = int(call.data.split(":", 1)[1])

    async with SQLAlchemyUserRepository() as repo:
        user = repo.get_by_id(user_id)

    if not user:
        await call.answer("❌ Пользователь не найден", show_alert=True)
        return
    await s.delete(user)

    # Сообщаем в админском чате
    await call.message.edit_text(f"🚫 Пользователь {user.name or user.id} был отклонён и удалён.")
    await call.answer("Пользователь отклонён", show_alert=True)

    # Уведомляем пользователя
    try:
        await call.bot.send_message(
            chat_id=user_id,
            text="🚫 Ваш доступ к боту был отклонён."
        )
    except Exception:
        pass
