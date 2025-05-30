from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.handlers.ui.ui_main import categories_kb, topics_kb, main_menu_inline_kb
from bot.utils.guards import block_if_pending_callback
from core.application.decorators.block import block_if_active_question
from core.application.security.approved_user_only import is_approved_user
from core.infrastructure.database.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository

router = Router()


@router.callback_query(F.data == "reading")
@is_approved_user()
@block_if_active_question(lambda call, is_approved, state, dispatcher: call.from_user.id)
async def reading_panel(call: CallbackQuery, is_approved: bool, state: FSMContext, dispatcher):
    """Панель тем /reading"""
    await call.answer()
    await call.message.edit_text(
        "🧐<b> Выбери раздел для чтения</b>:",
        reply_markup=categories_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("cat|"))
@is_approved_user()
async def choose_category(call: CallbackQuery, is_approved: bool, state: FSMContext):
    """Обработка выбора конкретной категории"""
    # данные callback_data вида "cat|<имя_категории>"
    _, category = call.data.split("|", 1)

    if "Школа" in category:
        async with SQLAlchemyUserRepository() as repo:
            get_age = await repo.get_by_id(call.from_user.id)
            age = get_age.age

        if age > 18:
            await call.answer(
                "❗Этот раздел только для школьников. К сожалению, доступ ограничен.",
                show_alert=True,
            )
            return
    await state.update_data(category=category)

    await call.message.edit_text(
        f"📁 <b>{category}</b>",
        reply_markup=topics_kb(category)
    )


@router.callback_query(F.data == "back_to_categories")
@is_approved_user()
async def back_to_categories(call: CallbackQuery, state: FSMContext, is_approved: bool):
    """Возврат к выбору категорий. Блокирует, если есть активный вопрос."""
    if await block_if_pending_callback(call, state):
        return

    await call.answer()
    await call.message.edit_text("📂 Выбери раздел:", reply_markup=categories_kb())


@router.callback_query(F.data == "reading:back")
async def reading_back_callback(call: CallbackQuery, is_admin: bool):
    await call.answer()
    await call.message.edit_text(
        "<b>Главное меню</b>:",
        reply_markup=main_menu_inline_kb(is_admin),
        parse_mode="HTML"
    )
