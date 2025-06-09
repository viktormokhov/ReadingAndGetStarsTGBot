from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fastapi import Depends
from sqlalchemy import delete

from config.constants import PAGE_SIZE
from core.infrastructure.db import user_ops
from core.infrastructure.db.models import User
from core.application.security.admin_only import admin_only
from core.domain.models.pagination import PageParams
from core.application.services.admin.admin_stats import render_user_stats
from core.domain.services.admin.admin_user_service import fetch_user_stats
from bot.handlers.ui.ui_admin import admin_pagination_kb, admin_back_menu_kb
from core.infrastructure.db.repository_factory import RepositoryFactory

router = Router()

async def user_repo_dep():
    return RepositoryFactory.create_user_repository()


@router.callback_query(F.data.startswith("admin:all_users"))
@admin_only()
async def show_all_users(call: CallbackQuery, is_admin: bool, user_repo = Depends(user_repo_dep)):
    await call.answer()
    parts = call.data.split(":")
    page = int(parts[2]) if len(parts) > 2 else 0
    pp = PageParams(page=page, page_size=PAGE_SIZE)

    user_stats, total = await fetch_user_stats(pp)
    if not user_stats:
        await call.message.edit_text("🙁 Нет пользователей на этой странице.")
        return

    # Собираем текст из UserStat.format_html()
    text = "\n\n".join(u.format_html() for u in user_stats)

    await call.message.edit_text(
        text,
        reply_markup=admin_pagination_kb(pp.page, total, PAGE_SIZE),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("reset_user:"))
@admin_only()
async def reset_user(call: CallbackQuery, is_admin: bool, user_repo = Depends(user_repo_dep)):
    from core.infrastructure.db.models import UserStars

    user_id = int(call.data.split(":", 1)[1])
    user = await user_repo.get_by_id(user_id)
    if user:
        # Delete all UserStar entries for this users
        await s.execute(delete(UserStars).where(UserStars.user_id == user_id))

        user.q_ok = 0
        user.q_tot = 0
        user.streak = 0
        await s.execute(user_ops.delete_theme_stats_for_user(user_id))

    await call.answer("♻️ Статистика сброшена")
    # После сброса показываем обновлённую информацию
    text, user = await render_user_stats(user_id)
    kb = InlineKeyboardBuilder()
    kb.button(text="♻️ Сброс", callback_data=f"reset_user:{user.id}")
    kb.button(text="🗑 Удалить", callback_data=f"delete_user:{user.id}")
    kb.button(text="🔙 Назад", callback_data="admin:menu")
    kb.adjust(2)
    await call.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")


@router.callback_query(F.data.startswith("delete_user:"))
@admin_only()
async def delete_user(call: CallbackQuery, is_admin: bool, state: FSMContext):
    user_id = int(call.data.split(":", 1)[1])
    async with AsyncSessionLocal.begin() as s:
        user = await s.get(User, user_id)
        if user:
            if user.is_admin:
                await call.answer("⛔ Нельзя удалить администратора", show_alert=True)
                return
            await s.execute(user_ops.delete_theme_stats_for_user(user_id))
            await s.delete(user)

    await call.answer("🗑 Удалён")
    await call.message.edit_text(f"🗑 Пользователь {user_id} удалён.")
    await state.set_state("awaiting_user_id")

    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 В меню", callback_data="admin:menu")
    await call.message.bot.send_message(
        chat_id=call.from_user.id,
        text="🔎 Введите другой ID пользователя:",
        reply_markup=kb.as_markup()
    )


@router.callback_query(F.data.startswith("admin:lookup_user"))
@admin_only()
async def ask_user_id(call: CallbackQuery, is_admin: bool, state: FSMContext):
    await call.answer()

    await call.message.edit_text(
        "🔎 Введите ID пользователя:",
        reply_markup=admin_back_menu_kb()
    )
    await state.set_state("awaiting_user_id")


@router.message(F.text.regexp(r"^\d+$"))
@admin_only()
async def receive_user_id(message: Message, state: FSMContext, is_admin: bool):
    if await state.get_state() != "awaiting_user_id":
        return

    user_id = int(message.text)
    text, user = await render_user_stats(user_id)

    if not user:
        await message.answer("❌ Пользователь не найден. Введите ID ещё раз:")
        return

    await state.clear()
    await message.answer(
        text,
        reply_markup=admin_user_manage_kb(user.id),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("admin:user_info:"))
@admin_only()
async def user_info(call: CallbackQuery, is_admin: bool):
    parts = call.data.split(":")
    if len(parts) < 3:
        await call.answer("⚠️ ID пользователя не передан", show_alert=True)
        return

    user_id = int(parts[2])
    text, user = await render_user_stats(user_id)
    if not user:
        await call.answer(text, show_alert=True)
        return

    kb = InlineKeyboardBuilder()
    kb.button(text="♻️ Сброс", callback_data=f"reset_user:{user.id}")
    kb.button(text="🗑 Удалить", callback_data=f"delete_user:{user.id}")
    kb.button(text="🔙 Назад", callback_data="admin:menu")
    kb.adjust(2)

    await call.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
