import asyncio
from asyncio.log import logger

from aiogram import Router, F, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from fastapi import Depends

from bot.handlers.ui.ui_main import reading, topics_kb, categories_kb
from config.constants import ACTIVE_QUESTION_KEY, MAX_ATTEMPTS
from config.content import CATEGORIES
from core.application.decorators.block import async_with_generating_flag
from core.application.security.approved_user_only import is_approved_user
from core.application.services.users.user_flags import delete_blocking_message
from core.domain.services.reading.reading_result import save_card_and_notify
from core.domain.services.reading.reading_service import prepare_next_question, prepare_first_question, \
    has_exceeded_daily_limit
from core.domain.services.users.user_progress import accuracy
from core.infrastructure.clients.redis_client import rc as redis_client
from core.infrastructure.database.repository_factory import RepositoryFactory

router = Router()


async def user_repo_dep():
    return RepositoryFactory.create_user_repository()


@router.callback_query(F.data.startswith("T|"))
@is_approved_user()
@async_with_generating_flag(lambda call, is_approved, state, dispatcher: call.from_user.id, kind="text")
async def questions_handler(call: CallbackQuery,
                            is_approved: bool,
                            state: FSMContext,
                            dispatcher,
                            user_repo=Depends(user_repo_dep)):
    data = await state.get_data()
    category = data.get("category")

    theme = call.data.split("|", 1)[1].strip()

    # if await block_if_pending_message(call.message, state):
    #     return

    if await has_exceeded_daily_limit(call.from_user.id, theme):
        # 1) показываем alert (ждём завершения этого запроса)
        await call.answer(
            f"❗Ты ответил на все вопросы по этой теме.\n🦸🏻 Попробуй завтра",
            show_alert=True,
            cache_time=0,  # на всякий случай сброс кэша
        )
        # 2) небольшая «передышка», чтобы Telegram успел отобразить окошко
        await asyncio.sleep(0.5)

        # 3) теперь шлём меню
        category_name = get_category_by_theme(theme)
        if category_name:
            await call.message.edit_text(
                f"📂 {category_name}\n\nВыберите тему:",
                reply_markup=topics_kb(category_name)
            )
        else:
            await call.message.edit_text(
                "📂 Выберите раздел:",
                reply_markup=categories_kb()
            )
        return
    await call.answer()
    await redis_client.set(ACTIVE_QUESTION_KEY.format(user_id=call.from_user.id), 1, ex=600)
    await call.message.edit_text("✍️ Генерирую текст…", protect_content=True)
    try:
        reading_state = await prepare_first_question(call.from_user.id, category, theme)
        await delete_blocking_message(dispatcher["redis"], call.from_user.id, call.message.bot, call.message.chat.id)
    except RuntimeError as err:
        await call.message.edit_text(str(err))
        return

    # сохраняем всё в FSM
    await state.update_data(**reading_state.__dict__)

    # Удаляем старое сообщение-заглушку
    try:
        await call.bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    except:
        pass

    # Создаём **новое** сообщение с защитой и полным текстом
    gen_msg = await call.bot.send_message(
        chat_id=call.message.chat.id,
        text=reading_state.full_text,
        protect_content=True
    )
    # перед показом первого вопроса
    keyboard, shuffled_options = reading(reading_state.qa[0]["options"])
    await state.update_data(reading_options=shuffled_options)

    # показываем первый вопрос
    try:
        await call.bot.send_message(
            chat_id=call.message.chat.id,
            text=f"<b>{reading_state.qa[0]["question"]}</b>",
            protect_content=True,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    except TelegramBadRequest as err:
        if "BUTTON_DATA_INVALID" in err.message:
            logger.error("Неверный callback_data в кнопке: %s", err)
            await call.answer("Произошла внутренняя ошибка с кнопками. Попробуйте снова.")
        else:
            raise


@router.callback_query(F.data.startswith("OPT|"))
@is_approved_user()
async def answer_handler(call: CallbackQuery, is_approved: bool, state: FSMContext, dispatcher: Dispatcher):
    # await call.answer()
    data = await state.get_data()
    chosen_idx = int(call.data.split("|", 1)[1])
    options = data['reading_options']
    chosen = options[chosen_idx]

    # Остальные поля — для reading_state
    reading_data = {k: v for k, v in data.items() if k not in ('reading_options', 'category')}
    reading_state = ReadingState(**reading_data)

    if chosen == reading_state.correct:
        await accuracy(reading_state.uid, True)
        await save_card_and_notify(call, state, reading_state, dispatcher)
        return

    # Если дошли сюда — ответ неверный
    await accuracy(reading_state.uid, False)
    reading_state.wrong += 1

    # Если ошибок >= лимита (например, 2) — финал
    if reading_state.wrong >= MAX_ATTEMPTS:
        await save_card_and_notify(call, state, reading_state, dispatcher)
        return

    # Не достигли лимита ошибок — задаём следующий вопрос
    await state.update_data(wrong=reading_state.wrong)
    await prepare_next_question(call, state, reading_state)


def get_category_by_theme(theme):
    for category, topics in CATEGORIES.items():
        for t in topics:
            if t[0] == theme:
                return category
    return None
